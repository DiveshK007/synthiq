"""
Summarize service - clusters and summarizes text
"""
import logging
from typing import List

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynthIQ Summarize",
    description="Clusters and summarizes text content",
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
    question: str
    answer: str


class SummarizeResponse(BaseModel):
    clusters: List[Cluster]
    tldr: str
    faqs: List[FAQ]


def synthesize_placeholder_texts(doc_ids: List[str], goal: str) -> List[str]:
    """Synthesize placeholder texts based on doc_ids and goal"""
    # In a real implementation, this would fetch actual document content
    # For now, generate placeholder texts
    texts = []
    for i, doc_id in enumerate(doc_ids):
        text = f"Document {i+1} (ID: {doc_id[:8]}...) contains information related to {goal}. "
        text += f"This document discusses key concepts and findings relevant to the research goal. "
        text += f"Key points include methodology, results, and implications for the field."
        texts.append(text)
    return texts


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """Summarize and cluster documents"""
    try:
        doc_ids = request.doc_ids
        goal = request.goal
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="doc_ids cannot be empty")
        
        # Synthesize placeholder texts
        texts = synthesize_placeholder_texts(doc_ids, goal)
        
        # Vectorize with TfidfVectorizer
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english')
        try:
            X = vectorizer.fit_transform(texts)
        except ValueError:
            # Fallback if vectorization fails
            X = np.random.rand(len(texts), 10)
        
        # KMeans clustering
        n_clusters = min(3, len(doc_ids))
        if n_clusters < 1:
            n_clusters = 1
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X)
        
        # Build clusters
        clusters = []
        for cluster_id in range(n_clusters):
            cluster_indices = [i for i, label in enumerate(labels) if label == cluster_id]
            
            if not cluster_indices:
                continue
            
            # Build summary from cluster texts
            cluster_texts = [texts[i] for i in cluster_indices]
            summary = " ".join(cluster_texts[:2])  # Use first two sentences
            if len(summary) > 300:
                summary = summary[:297] + "..."
            
            # Build citations
            citations = []
            for idx in cluster_indices[:3]:  # Limit to 3 citations per cluster
                citation = Citation(
                    doc_id=doc_ids[idx],
                    spans=[CitationSpan(chunk_id=idx, start=0, end=80)]
                )
                citations.append(citation)
            
            cluster = Cluster(
                label=f"Cluster {cluster_id + 1}",
                summary=summary,
                citations=citations
            )
            clusters.append(cluster)
        
        # Build TL;DR from first sentences of clusters
        tldr_parts = []
        for cluster in clusters[:3]:  # Use first 3 clusters
            first_sentence = cluster.summary.split('.')[0] + '.'
            tldr_parts.append(first_sentence)
        
        tldr = " ".join(tldr_parts)
        if len(tldr) > 200:
            tldr = tldr[:197] + "..."
        
        # Build FAQs
        faqs = [
            FAQ(
                question="What is the main topic?",
                answer=f"The main topic relates to {goal}. The documents discuss various aspects of this research area."
            ),
            FAQ(
                question="What are the key findings?",
                answer="The key findings include important insights derived from the analyzed documents, covering methodology, results, and implications."
            )
        ]
        
        logger.info(f"Generated {len(clusters)} clusters, {len(faqs)} FAQs")
        
        return SummarizeResponse(
            clusters=clusters,
            tldr=tldr,
            faqs=faqs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error summarizing: {e}")
        raise HTTPException(status_code=500, detail=f"Error summarizing: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
