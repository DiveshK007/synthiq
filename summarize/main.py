"""
Summarize service - clusters and summarizes text
"""
import json
import logging
import os
from typing import List

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
    title="SynthIQ Summarize",
    description="Clusters and summarizes text content",
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


class SummarizeRequest(BaseModel):
    doc_ids: List[str]
    goal: str


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


@app.post("/summarize")
async def summarize(request: SummarizeRequest):
    """Summarize and cluster documents"""
    try:
        doc_ids = request.doc_ids
        goal = request.goal
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="doc_ids cannot be empty")
        
        # Create 3 placeholder clusters
        clusters = []
        for i in range(min(3, len(doc_ids))):
            cluster = Cluster(
                label=f"Cluster {i + 1}",
                summary=f"This cluster relates to {goal}. It contains key insights and findings relevant to the research goal. The documents in this cluster provide important context and analysis.",
                citations=[
                    Citation(
                        doc_id=doc_ids[i] if i < len(doc_ids) else doc_ids[0],
                        spans=[CitationSpan(chunk_id=1, start=0, end=80)]
                    )
                ]
            )
            clusters.append(cluster)
        
        # Build TL;DR from first sentences
        tldr_parts = [f"Research on {goal} reveals important insights."]
        for cluster in clusters[:2]:
            first_sentence = cluster.summary.split('.')[0] + '.'
            tldr_parts.append(first_sentence)
        
        tldr = " ".join(tldr_parts)
        if len(tldr) > 200:
            tldr = tldr[:197] + "..."
        
        # Build FAQs
        faqs = [
            FAQ(
                q=f"What is the main focus of research on {goal}?",
                a=f"The main focus is understanding key aspects of {goal} through comprehensive analysis of the provided documents."
            ),
            FAQ(
                q="What are the key findings?",
                a="The key findings include important insights derived from the analyzed documents, covering methodology, results, and implications."
            )
        ]
        
        log_json("INFO", "Summarization complete", cluster_count=len(clusters), faq_count=len(faqs))
        
        return {
            "clusters": [c.model_dump() for c in clusters],
            "tldr": tldr,
            "faqs": [f.model_dump() for f in faqs]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_json("ERROR", "Error summarizing", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error summarizing: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8082"))
    uvicorn.run(app, host="0.0.0.0", port=port)
