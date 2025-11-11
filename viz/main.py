"""
Viz service - generates Mermaid graphs and visualizations
"""
import json
import logging
import os
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from schemas import VisualizeRequest, VisualizeResponse, Cluster

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Get version from environment or use default
VERSION = os.getenv("VERSION", "0.1.0")

app = FastAPI(
    title="SynthIQ Viz",
    description="Generates Mermaid graphs and visualizations",
    version=VERSION,
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


# Schemas imported from schemas.py


def log_json(level: str, message: str, **kwargs):
    """Log as JSON"""
    log_entry = {
        "level": level,
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))


def generate_mermaid_graph(clusters: List[Cluster], tldr: str) -> str:
    """Generate Mermaid flowchart from clusters"""
    if not clusters:
        return "flowchart LR\n    A[No Clusters] --> B[Empty Graph]"
    
    lines = ["flowchart LR"]
    
    # Add cluster nodes
    for i, cluster in enumerate(clusters):
        node_id = f"C{i + 1}"
        label = cluster.label.replace('"', "'")  # Escape quotes
        lines.append(f'    {node_id}["{label}"]')
    
    # Link clusters pairwise
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            lines.append(f'    C{i + 1} --> C{j + 1}')
    
    return "\n".join(lines)


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True, "version": VERSION}


@app.get("/version")
async def version():
    """Version endpoint"""
    return {"version": VERSION, "service": "viz"}


@app.post("/viz", response_model=VisualizeResponse)
async def visualize(request: VisualizeRequest):
    """Generate Mermaid graph from clusters"""
    try:
        clusters = request.clusters
        tldr = request.tldr
        
        # Generate Mermaid graph
        mermaid = generate_mermaid_graph(clusters, tldr)
        
        log_json("INFO", "Visualization generated", cluster_count=len(clusters))
        
        return VisualizeResponse(
            mermaid=mermaid,
            graph_png_url="https://via.placeholder.com/800x400.png?text=Graph",
            slides_pdf_url="https://example.com/slides.pdf"
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        log_json("ERROR", "Error generating graph", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error generating graph: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8083"))
    uvicorn.run(app, host="0.0.0.0", port=port)
