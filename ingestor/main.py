"""
Ingestor service - fetches and cleans raw content
"""
import logging
import os
import re
from typing import List
from uuid import uuid4

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from pypdf import PdfReader
from io import BytesIO

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynthIQ Ingestor",
    description="Fetches and cleans raw content from URLs or PDFs",
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


class Source(BaseModel):
    type: str  # "url" | "pdf"
    value: str


class IngestRequest(BaseModel):
    sources: List[Source]


class IngestResponse(BaseModel):
    doc_ids: List[str]
    tokens: int


def chunk_text(text: str, chunk_size: int = 2000) -> List[str]:
    """Split text into roughly chunk_size character chunks"""
    chunks = []
    current_chunk = ""
    
    # Split by sentences first
    sentences = re.split(r'[.!?]+\s+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # If adding this sentence would exceed chunk size, save current chunk
        if len(current_chunk) + len(sentence) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
    
    # Add remaining chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


async def fetch_url(url: str) -> str:
    """Fetch content from URL and extract text"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            })
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "lxml")
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator=" ", strip=True)
            
            # Collapse whitespace
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            logger.info(f"Fetched {len(text)} characters from {url}")
            return text
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing URL: {str(e)}")


async def fetch_pdf(pdf_url: str) -> str:
    """Fetch PDF from URL and extract text"""
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
            
            # Read PDF
            pdf_bytes = BytesIO(response.content)
            reader = PdfReader(pdf_bytes)
            
            # Extract text from all pages
            text_parts = []
            for page in reader.pages:
                text_parts.append(page.extract_text())
            
            text = "\n".join(text_parts)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
            logger.info(f"Extracted {len(text)} characters from PDF {pdf_url}")
            return text
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching PDF {pdf_url}: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to fetch PDF: {str(e)}")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_url}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/ingest", response_model=IngestResponse)
async def ingest(request: IngestRequest):
    """Ingest content from URLs or PDFs"""
    doc_ids = []
    total_chars = 0
    
    try:
        for source in request.sources:
            if source.type == "url":
                text = await fetch_url(source.value)
            elif source.type == "pdf":
                text = await fetch_pdf(source.value)
            else:
                raise HTTPException(status_code=400, detail=f"Unknown source type: {source.type}")
            
            # Chunk the text
            chunks = chunk_text(text, chunk_size=2000)
            
            # Create doc_ids for each chunk
            for chunk in chunks:
                doc_id = str(uuid4())
                doc_ids.append(doc_id)
                total_chars += len(chunk)
        
        # Approximate tokens (rough estimate: 1 token ≈ 4 characters)
        tokens = total_chars // 4
        
        logger.info(f"Ingested {len(doc_ids)} documents, {tokens} tokens")
        
        return IngestResponse(
            doc_ids=doc_ids,
            tokens=tokens
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ingesting content: {e}")
        raise HTTPException(status_code=500, detail=f"Error ingesting content: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
