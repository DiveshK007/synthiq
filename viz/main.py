"""
Viz service - generates Mermaid graphs and visualizations
"""
import logging
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynthIQ Viz",
    description="Generates Mermaid graphs and visualizations",
    version="0.1.0",
    default_response_class=ORJSONResponse
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class VisualizeRequest(BaseModel):
    clusters: List[Cluster]
    tldr: str


class VisualizeResponse(BaseModel):
    mermaid: str
    graph_png_url: str
    slides_pdf_url: str


def generate_mermaid_graph(clusters: List[Cluster], tldr: str) -> str:
    """Generate Mermaid flowchart from clusters"""
    if not clusters:
        return "graph TD\n    A[No Clusters] --> B[Empty Graph]"
    
    lines = ["graph TD"]
    
    # Add TL;DR node
    tldr_short = tldr[:50] + "..." if len(tldr) > 50 else tldr
    lines.append(f'    TLDR["TL;DR: {tldr_short}"]')
    
    # Add cluster nodes
    for i, cluster in enumerate(clusters):
        node_id = f"C{i}"
        label_short = cluster.label[:30] + "..." if len(cluster.label) > 30 else cluster.label
        lines.append(f'    {node_id}["{label_short}"]')
        
        # Link to TL;DR
        lines.append(f'    TLDR --> {node_id}')
    
    # Link all clusters pairwise (simple completeness)
    for i in range(len(clusters)):
        for j in range(i + 1, len(clusters)):
            lines.append(f'    C{i} --> C{j}')
    
    return "\n".join(lines)


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/viz", response_model=VisualizeResponse)
async def visualize(request: VisualizeRequest):
    """Generate Mermaid graph from clusters"""
    try:
        clusters = request.clusters
        tldr = request.tldr
        
        # Generate Mermaid graph
        mermaid = generate_mermaid_graph(clusters, tldr)
        
        logger.info(f"Generated Mermaid graph with {len(clusters)} clusters")
        
        return VisualizeResponse(
            mermaid=mermaid,
            graph_png_url="https://via.placeholder.com/800x400.png?text=Graph",
            slides_pdf_url="https://example.com/slides.pdf"
        )
        
    except Exception as e:
        logger.error(f"Error generating graph: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating graph: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
