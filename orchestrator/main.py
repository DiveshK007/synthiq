"""
Orchestrator service - coordinates the pipeline
"""
import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Optional
from uuid import uuid4

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from database import init_db, create_job as db_create_job, get_job as db_get_job, update_job as db_update_job, list_jobs as db_list_jobs

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynthIQ Orchestrator",
    description="Coordinates the research summarization pipeline",
    version="0.1.0",
    default_response_class=ORJSONResponse
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    log_json("INFO", "Database initialized", route="startup")

# CORS middleware
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5174")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service URLs from environment
INGESTOR_URL = os.getenv("INGESTOR_URL", "http://localhost:8081")
SUMMARIZE_URL = os.getenv("SUMMARIZE_URL", "http://localhost:8082")
VIZ_URL = os.getenv("VIZ_URL", "http://localhost:8083")

# WebSocket connections for real-time updates
active_connections: Dict[str, List[WebSocket]] = {}


class Source(BaseModel):
    type: str  # "url" | "pdf" | "text"
    value: str


class NewJobPayload(BaseModel):
    sources: List[Source]
    goal: str


class JobProgress(BaseModel):
    ingest: int
    summarize: int
    viz: int


class CitationSpan(BaseModel):
    chunk_id: int
    start: int
    end: int


class Citation(BaseModel):
    doc_id: str
    spans: List[CitationSpan]


class Cluster(BaseModel):
    label: str
    summary: str
    citations: List[Citation]


class FAQ(BaseModel):
    q: str
    a: str


class JobResult(BaseModel):
    tldr: str
    clusters: List[dict]
    faqs: List[dict]
    assets: dict
    created_at: int
    duration_ms: int


class Job(BaseModel):
    id: str
    status: str  # "queued" | "running" | "done" | "error"
    error: Optional[str] = None
    progress: JobProgress
    result: Optional[JobResult] = None


def log_json(level: str, message: str, **kwargs):
    """Log as JSON"""
    log_entry = {
        "level": level,
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException))
)
async def call_service_with_retry(url: str, payload: dict, job_id: str, step: str) -> dict:
    """Call external service with retry logic"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        log_json("WARN", f"Service call failed (retrying)", 
                 job_id=job_id, step=step, url=url, error=str(e), route="run_pipeline")
        raise
    except httpx.TimeoutException as e:
        log_json("WARN", f"Service call timeout (retrying)", 
                 job_id=job_id, step=step, url=url, error=str(e), route="run_pipeline")
        raise


@app.get("/healthz")
async def healthz():
    """Health check endpoint with detailed status"""
    import time
    from datetime import datetime
    
    uptime_start = getattr(healthz, 'start_time', None)
    if not uptime_start:
        healthz.start_time = time.time()
        uptime_start = healthz.start_time
    
    uptime_seconds = int(time.time() - uptime_start)
    
    # Check dependencies
    dependencies = {}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{INGESTOR_URL}/healthz")
            dependencies["ingestor"] = response.status_code == 200
    except:
        dependencies["ingestor"] = False
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SUMMARIZE_URL}/healthz")
            dependencies["summarize"] = response.status_code == 200
    except:
        dependencies["summarize"] = False
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{VIZ_URL}/healthz")
            dependencies["viz"] = response.status_code == 200
    except:
        dependencies["viz"] = False
    
    return {
        "ok": True,
        "version": "0.1.0",
        "uptime_seconds": uptime_seconds,
        "dependencies": dependencies,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/jobs")
async def create_job(payload: NewJobPayload):
    """Create a new research job"""
    job_id = str(uuid4())
    user_id = None  # TODO: Get from auth token
    
    # Create job in database
    job = db_create_job(
        job_id=job_id,
        sources=[{"type": s.type, "value": s.value} for s in payload.sources],
        goal=payload.goal,
        user_id=user_id
    )
    
    log_json("INFO", "Job created", job_id=job_id, route="POST /jobs")
    
    # Start pipeline asynchronously
    asyncio.create_task(run_pipeline(job_id, payload))
    
    return {"job_id": job_id}


@app.get("/jobs")
async def list_jobs(user_id: Optional[str] = None, limit: int = 100, offset: int = 0):
    """List jobs (optionally filtered by user_id)"""
    jobs = db_list_jobs(user_id=user_id, limit=limit, offset=offset)
    log_json("INFO", "Jobs listed", count=len(jobs), route="GET /jobs")
    
    return [
        {
            "id": job.id,
            "status": job.status,
            "error": job.error,
            "progress": job.progress,
            "result": job.result,
            "created_at": job.created_at
        }
        for job in jobs
    ]


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    job = db_get_job(job_id)
    if not job:
        log_json("WARN", "Job not found", job_id=job_id, route="GET /jobs/{job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    log_json("INFO", "Job retrieved", job_id=job_id, route="GET /jobs/{job_id}")
    # Convert SQLModel to dict
    return {
        "id": job.id,
        "status": job.status,
        "error": job.error,
        "progress": job.progress,
        "result": job.result,
        "created_at": job.created_at
    }


@app.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates"""
    await websocket.accept()
    
    # Add connection to active connections
    if job_id not in active_connections:
        active_connections[job_id] = []
    active_connections[job_id].append(websocket)
    
    log_json("INFO", "WebSocket connected", job_id=job_id, route="WS /ws/jobs/{job_id}")
    
    try:
        # Send initial job state
        job = db_get_job(job_id)
        if job:
            await websocket.send_json({
                "id": job.id,
                "status": job.status,
                "error": job.error,
                "progress": job.progress,
                "result": job.result,
                "created_at": job.created_at
            })
        
        # Keep connection alive and send updates
        while True:
            # Poll for updates every second
            await asyncio.sleep(1)
            job = db_get_job(job_id)
            if job:
                await websocket.send_json({
                    "id": job.id,
                    "status": job.status,
                    "error": job.error,
                    "progress": job.progress,
                    "result": job.result,
                    "created_at": job.created_at
                })
                
                # Close connection if job is done or error
                if job.status in ["done", "error"]:
                    break
    except WebSocketDisconnect:
        log_json("INFO", "WebSocket disconnected", job_id=job_id, route="WS /ws/jobs/{job_id}")
    finally:
        # Remove connection
        if job_id in active_connections:
            active_connections[job_id].remove(websocket)
            if not active_connections[job_id]:
                del active_connections[job_id]


async def broadcast_job_update(job_id: str):
    """Broadcast job update to all connected WebSocket clients"""
    if job_id not in active_connections:
        return
    
    job = db_get_job(job_id)
    if not job:
        return
    
    update = {
        "id": job.id,
        "status": job.status,
        "error": job.error,
        "progress": job.progress,
        "result": job.result,
        "created_at": job.created_at
    }
    
    # Send to all connected clients
    disconnected = []
    for connection in active_connections[job_id]:
        try:
            await connection.send_json(update)
        except Exception as e:
            log_json("WARN", "Failed to send WebSocket update", 
                    job_id=job_id, error=str(e), route="broadcast_job_update")
            disconnected.append(connection)
    
    # Remove disconnected connections
    for conn in disconnected:
        active_connections[job_id].remove(conn)
    
    if not active_connections[job_id]:
        del active_connections[job_id]


async def run_pipeline(job_id: str, payload: NewJobPayload):
    """Run the pipeline: ingest -> summarize -> viz"""
    start_time = time.time()
    
    try:
        db_update_job(job_id, status="running")
        log_json("INFO", "Pipeline started", job_id=job_id, route="run_pipeline")
        
        # Step 1: Ingest (with retry)
        log_json("INFO", "Ingesting content", job_id=job_id, route="run_pipeline")
        db_update_job(job_id, progress={"ingest": 10, "summarize": 0, "viz": 0})
        
        ingest_data = await call_service_with_retry(
            f"{INGESTOR_URL}/ingest",
            {"sources": [{"type": s.type, "value": s.value} for s in payload.sources]},
            job_id,
            "ingest"
        )
        
        db_update_job(job_id, progress={"ingest": 100, "summarize": 0, "viz": 0})
        await broadcast_job_update(job_id)
        log_json("INFO", "Ingestion complete", job_id=job_id, route="run_pipeline")
        
        # Step 2: Summarize (with retry)
        log_json("INFO", "Summarizing content", job_id=job_id, route="run_pipeline")
        db_update_job(job_id, progress={"ingest": 100, "summarize": 10, "viz": 0})
        await broadcast_job_update(job_id)
        
        summarize_data = await call_service_with_retry(
            f"{SUMMARIZE_URL}/summarize",
            {"doc_ids": ingest_data.get("doc_ids", []), "goal": payload.goal},
            job_id,
            "summarize"
        )
        
        db_update_job(job_id, progress={"ingest": 100, "summarize": 100, "viz": 0})
        await broadcast_job_update(job_id)
        log_json("INFO", "Summarization complete", job_id=job_id, route="run_pipeline")
        
        # Step 3: Visualize (with retry)
        log_json("INFO", "Generating visualization", job_id=job_id, route="run_pipeline")
        db_update_job(job_id, progress={"ingest": 100, "summarize": 100, "viz": 10})
        await broadcast_job_update(job_id)
        
        viz_data = await call_service_with_retry(
            f"{VIZ_URL}/viz",
            {
                "clusters": summarize_data.get("clusters", []),
                "tldr": summarize_data.get("tldr", "")
            },
            job_id,
            "viz"
        )
        
        db_update_job(job_id, progress={"ingest": 100, "summarize": 100, "viz": 100})
        await broadcast_job_update(job_id)
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Get job to get created_at
        job = db_get_job(job_id)
        
        # Set result
        result = {
            "tldr": summarize_data.get("tldr", ""),
            "clusters": summarize_data.get("clusters", []),
            "faqs": summarize_data.get("faqs", []),
            "assets": {
                "mermaid": viz_data.get("mermaid", ""),
                "graph_png_url": viz_data.get("graph_png_url", ""),
                "slides_pdf_url": viz_data.get("slides_pdf_url", "")
            },
            "created_at": job.created_at if job else int(time.time() * 1000),
            "duration_ms": duration_ms
        }
        
        db_update_job(job_id, status="done", result=result)
        await broadcast_job_update(job_id)
        log_json("INFO", "Pipeline complete", job_id=job_id, duration_ms=duration_ms, route="run_pipeline")
        
    except httpx.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        log_json("ERROR", "Pipeline HTTP error", job_id=job_id, error=error_msg, route="run_pipeline")
        db_update_job(job_id, status="error", error=error_msg)
        await broadcast_job_update(job_id)
    except Exception as e:
        error_msg = str(e)
        log_json("ERROR", "Pipeline error", job_id=job_id, error=error_msg, route="run_pipeline")
        db_update_job(job_id, status="error", error=error_msg)
        await broadcast_job_update(job_id)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
