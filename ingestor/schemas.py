"""
Ingestor service schemas
"""
from typing import List, Literal
from pydantic import BaseModel, Field, validator


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

