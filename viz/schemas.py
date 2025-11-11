"""
Viz service schemas
"""
from typing import List, Optional
from pydantic import BaseModel, Field


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


class VisualizeRequest(BaseModel):
    """Request model for viz service"""
    clusters: List[Cluster] = Field(..., min_items=1, max_items=10)
    tldr: str = Field(..., min_length=1, max_length=2000)


class VisualizeResponse(BaseModel):
    """Response model from viz service"""
    mermaid: str = Field(..., description="Mermaid diagram code")
    graph_png_url: Optional[str] = Field(None, description="URL to PNG export")
    slides_pdf_url: Optional[str] = Field(None, description="URL to PDF slides")

