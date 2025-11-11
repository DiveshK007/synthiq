"""
Summarize service schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    """Request model for summarize service"""
    doc_ids: List[str] = Field(..., min_items=1, description="Document IDs to summarize")
    goal: str = Field(..., min_length=1, max_length=1000, description="Summarization goal")
    seed: Optional[int] = Field(None, description="Random seed for deterministic clustering")


class CitationSpan(BaseModel):
    """Citation span within a chunk"""
    chunk_id: int = Field(..., ge=0)
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)


class Citation(BaseModel):
    """Citation with document and spans"""
    doc_id: str
    spans: List[CitationSpan] = Field(default_factory=list)


class Cluster(BaseModel):
    """Cluster with label, summary, and citations"""
    label: str = Field(..., min_length=1, max_length=200)
    summary: str = Field(..., min_length=1, max_length=5000)
    citations: List[Citation] = Field(default_factory=list)


class FAQ(BaseModel):
    """Frequently asked question"""
    q: str = Field(..., min_length=1, max_length=500)
    a: str = Field(..., min_length=1, max_length=2000)


class SummarizeResponse(BaseModel):
    """Response model from summarize service"""
    tldr: str = Field(..., min_length=1, max_length=2000)
    clusters: List[Cluster] = Field(..., max_items=10)
    faqs: List[FAQ] = Field(default_factory=list, max_items=10)

