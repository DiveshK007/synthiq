"""
Orchestrator service - coordinates the pipeline
"""
import asyncio
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

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(job_id)s] - %(message)s',
    style='%'
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
    type: str  # "url" | "pdf"
    value: str


class JobRequest(BaseModel):
    sources: List[Source]
    goal: str


class JobResponse(BaseModel):
    job_id: str


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/jobs", response_model=JobResponse)
async def create_job(request: JobRequest):
    """Create a new research job"""
    job_id = str(uuid4())
    created_at_ms = int(time.time() * 1000)
    
    job = {
        "job_id": job_id,
        "status": "queued",
        "progress": {
            "ingestor": 0,
            "summarize": 0,
            "viz": 0
        },
        "result": None,
        "error": None,
        "created_at": created_at_ms,
        "duration_ms": None
    }
    
    jobs[job_id] = job
    
    # Start processing asynchronously
    asyncio.create_task(run_pipeline(job_id, request.sources, request.goal))
    
    logger.info(f"Created job {job_id}", extra={"job_id": job_id, "route": "POST /jobs"})
    return JobResponse(job_id=job_id)


@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    """Get job status and results"""
    if job_id not in jobs:
        logger.warning(f"Job not found: {job_id}", extra={"job_id": job_id, "route": "GET /jobs/{job_id}"})
        raise HTTPException(status_code=404, detail="Job not found")
    
    logger.info(f"Retrieved job {job_id}", extra={"job_id": job_id, "route": "GET /jobs/{job_id}"})
    return jobs[job_id]


async def run_pipeline(job_id: str, sources: List[Source], goal: str):
    """Run the pipeline: ingestor -> summarize -> viz"""
    job = jobs[job_id]
    start_time = time.time()
    
    try:
        job["status"] = "running"
        logger.info(f"Starting pipeline for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
        
        # Step 1: Ingest content
        logger.info(f"Ingesting content for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
        job["progress"]["ingestor"] = 10
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{INGESTOR_URL}/ingest",
                json={"sources": [{"type": s.type, "value": s.value} for s in sources]}
            )
            response.raise_for_status()
            ingest_data = response.json()
        
        job["progress"]["ingestor"] = 100
        logger.info(f"Ingestion complete for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
        
        # Step 2: Summarize and cluster
        logger.info(f"Summarizing content for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
        job["progress"]["summarize"] = 10
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{SUMMARIZE_URL}/summarize",
                json={"doc_ids": ingest_data.get("doc_ids", []), "goal": goal}
            )
            response.raise_for_status()
            summarize_data = response.json()
        
        job["progress"]["summarize"] = 100
        logger.info(f"Summarization complete for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
        
        # Step 3: Generate visualization
        logger.info(f"Generating visualization for job {job_id}", extra={"job_id": job_id, "route": "run_pipeline"})
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
        job["duration_ms"] = duration_ms
        
        logger.info(f"Pipeline complete for job {job_id} in {duration_ms}ms", extra={"job_id": job_id, "route": "run_pipeline"})
        
    except httpx.HTTPError as e:
        error_msg = f"HTTP error: {str(e)}"
        logger.error(f"Pipeline error for job {job_id}: {error_msg}", extra={"job_id": job_id, "route": "run_pipeline"})
        job["status"] = "error"
        job["error"] = error_msg
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Pipeline error for job {job_id}: {error_msg}", extra={"job_id": job_id, "route": "run_pipeline"})
        job["status"] = "error"
        job["error"] = error_msg


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
