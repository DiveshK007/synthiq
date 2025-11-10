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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

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

# In-memory job storage
jobs: Dict[str, dict] = {}


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


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/jobs")
async def create_job(payload: NewJobPayload):
    """Create a new research job"""
    job_id = str(uuid4())
    created_at = int(time.time() * 1000)
    
    job = {
        "id": job_id,
        "status": "queued",
        "error": None,
        "progress": {
            "ingest": 0,
            "summarize": 0,
            "viz": 0
        },
        "result": None,
        "created_at": created_at
    }
    
    jobs[job_id] = job
    
    log_json("INFO", "Job created", job_id=job_id, route="POST /jobs")
    
    # Start pipeline asynchronously
    asyncio.create_task(run_pipeline(job_id, payload))
    
    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in jobs:
        log_json("WARN", "Job not found", job_id=job_id, route="GET /jobs/{job_id}")
        raise HTTPException(status_code=404, detail="Job not found")
    
    log_json("INFO", "Job retrieved", job_id=job_id, route="GET /jobs/{job_id}")
    return jobs[job_id]


async def run_pipeline(job_id: str, payload: NewJobPayload):
    """Run the pipeline: ingest -> summarize -> viz"""
    job = jobs[job_id]
    start_time = time.time()
    
    try:
        job["status"] = "running"
        log_json("INFO", "Pipeline started", job_id=job_id, route="run_pipeline")
        
        # Step 1: Ingest
        log_json("INFO", "Ingesting content", job_id=job_id, route="run_pipeline")
        job["progress"]["ingest"] = 10
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INGESTOR_URL}/ingest",
                json={"sources": [{"type": s.type, "value": s.value} for s in payload.sources]}
            )
            response.raise_for_status()
            ingest_data = response.json()
        
        job["progress"]["ingest"] = 100
        log_json("INFO", "Ingestion complete", job_id=job_id, route="run_pipeline")
        
        # Step 2: Summarize
        log_json("INFO", "Summarizing content", job_id=job_id, route="run_pipeline")
        job["progress"]["summarize"] = 10
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{SUMMARIZE_URL}/summarize",
                json={"doc_ids": ingest_data.get("doc_ids", []), "goal": payload.goal}
            )
            response.raise_for_status()
            summarize_data = response.json()
        
        job["progress"]["summarize"] = 100
        log_json("INFO", "Summarization complete", job_id=job_id, route="run_pipeline")
        
        # Step 3: Visualize
        log_json("INFO", "Generating visualization", job_id=job_id, route="run_pipeline")
        job["progress"]["viz"] = 10
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{VIZ_URL}/viz",
                json={
                    "clusters": summarize_data.get("clusters", []),
                    "tldr": summarize_data.get("tldr", "")
                }
            )
            response.raise_for_status()
            viz_data = response.json()
        
        job["progress"]["viz"] = 100
        
        # Calculate duration
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Set result
        job["status"] = "done"
        job["result"] = {
            "tldr": summarize_data.get("tldr", ""),
            "clusters": summarize_data.get("clusters", []),
            "faqs": summarize_data.get("faqs", []),
            "assets": {
                "mermaid": viz_data.get("mermaid", ""),
                "graph_png_url": viz_data.get("graph_png_url", ""),
                "slides_pdf_url": viz_data.get("slides_pdf_url", "")
            },
            "created_at": job["created_at"],
            "duration_ms": duration_ms
        }
        
        log_json("INFO", "Pipeline complete", job_id=job_id, duration_ms=duration_ms, route="run_pipeline")
        
    except httpx.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        log_json("ERROR", "Pipeline HTTP error", job_id=job_id, error=error_msg, route="run_pipeline")
        job["status"] = "error"
        job["error"] = error_msg
    except Exception as e:
        error_msg = str(e)
        log_json("ERROR", "Pipeline error", job_id=job_id, error=error_msg, route="run_pipeline")
        job["status"] = "error"
        job["error"] = error_msg


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
