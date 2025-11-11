"""
Shared Pydantic models for API contracts
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, validator
from datetime import datetime


class Source(BaseModel):
    """Source input model"""
    type: Literal["url", "pdf", "text"] = Field(..., description="Type of source")
    value: str = Field(..., min_length=1, max_length=10000, description="Source content or URL")

    @validator('value')
    def validate_url_if_needed(cls, v, values):
        """Validate URL format if type is url or pdf"""
        if 'type' in values and values['type'] in ['url', 'pdf']:
            if not v.startswith(('http://', 'https://')):
                raise ValueError('URLs must start with http:// or https://')
        return v


class IngestRequest(BaseModel):
    """Request model for ingestor service"""
    sources: List[Source] = Field(..., min_items=1, max_items=20, description="List of sources to ingest")

    @validator('sources')
    def validate_sources_count(cls, v):
        """Ensure we don't exceed max sources"""
        if len(v) > 20:
            raise ValueError('Maximum 20 sources allowed per job')
        return v


class Chunk(BaseModel):
    """Text chunk with metadata"""
    chunk_id: int
    text: str
    doc_id: str
    start: int
    end: int


class IngestResponse(BaseModel):
    """Response model from ingestor service"""
    doc_ids: List[str] = Field(..., description="Document IDs")
    chunks: List[Chunk] = Field(..., description="Text chunks")
    total_tokens: int = Field(..., ge=0, description="Total token count")


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


class SummarizeRequest(BaseModel):
    """Request model for summarize service"""
    doc_ids: List[str] = Field(..., min_items=1, description="Document IDs to summarize")
    goal: str = Field(..., min_length=1, max_length=1000, description="Summarization goal")
    seed: Optional[int] = Field(None, description="Random seed for deterministic clustering")


class SummarizeResponse(BaseModel):
    """Response model from summarize service"""
    tldr: str = Field(..., min_length=1, max_length=2000)
    clusters: List[Cluster] = Field(..., max_items=10)
    faqs: List[FAQ] = Field(default_factory=list, max_items=10)


class VisualizeRequest(BaseModel):
    """Request model for viz service"""
    clusters: List[Cluster] = Field(..., min_items=1, max_items=10)
    tldr: str = Field(..., min_length=1, max_length=2000)


class VisualizeResponse(BaseModel):
    """Response model from viz service"""
    mermaid: str = Field(..., description="Mermaid diagram code")
    graph_png_url: Optional[str] = Field(None, description="URL to PNG export")
    slides_pdf_url: Optional[str] = Field(None, description="URL to PDF slides")


class JobCreateRequest(BaseModel):
    """Request model for creating a job"""
    sources: List[Source] = Field(..., min_items=1, max_items=20, description="List of sources")
    goal: str = Field(..., min_length=1, max_length=1000, description="Job goal")

    @validator('sources')
    def validate_sources(cls, v):
        """Validate sources count and size"""
        if len(v) > 20:
            raise ValueError('Maximum 20 sources allowed per job')
        # Estimate payload size (rough check)
        total_size = sum(len(s.value) for s in v) + len(v) * 100  # rough estimate
        if total_size > 2 * 1024 * 1024:  # 2MB
            raise ValueError('Total payload size exceeds 2MB limit')
        return v


class JobStatusResponse(BaseModel):
    """Response model for job status"""
    job_id: str
    status: Literal["pending", "ingesting", "summarizing", "visualizing", "completed", "failed"]
    progress: dict = Field(default_factory=dict)
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class HealthResponse(BaseModel):
    """Health check response"""
    ok: bool
    version: str
    uptime_seconds: Optional[float] = None
    dependencies: Optional[dict] = None
    timestamp: Optional[str] = None


class VersionResponse(BaseModel):
    """Version response"""
    version: str
    service: str

