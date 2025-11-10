"""
Ingestor service - fetches and cleans raw content
"""
import json
import logging
import os
import re
from typing import List
from io import BytesIO

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel
from pypdf import PdfReader

# Configure JSON logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SynthIQ Ingestor",
    description="Fetches and cleans raw content from URLs or PDFs",
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


class Source(BaseModel):
    type: str  # "url" | "pdf" | "text"
    value: str


class IngestRequest(BaseModel):
    sources: List[Source]


def log_json(level: str, message: str, **kwargs):
    """Log as JSON"""
    log_entry = {
        "level": level,
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))


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
            
            log_json("INFO", "Fetched URL", url=url, text_length=len(text))
            return text
            
    except httpx.HTTPError as e:
        log_json("ERROR", "HTTP error fetching URL", url=url, error=str(e))
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        log_json("ERROR", "Error fetching URL", url=url, error=str(e))
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
            
            log_json("INFO", "Extracted PDF", url=pdf_url, text_length=len(text))
            return text
            
    except httpx.HTTPError as e:
        log_json("ERROR", "HTTP error fetching PDF", url=pdf_url, error=str(e))
        raise HTTPException(status_code=400, detail=f"Failed to fetch PDF: {str(e)}")
    except Exception as e:
        log_json("ERROR", "Error processing PDF", url=pdf_url, error=str(e))
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True}


@app.post("/ingest")
async def ingest(request: IngestRequest):
    """Ingest content from URLs, PDFs, or text"""
    doc_ids = []
    total_chars = 0
    
    try:
        for idx, source in enumerate(request.sources):
            if source.type == "url":
                text = await fetch_url(source.value)
            elif source.type == "pdf":
                text = await fetch_pdf(source.value)
            elif source.type == "text":
                text = source.value
            else:
                raise HTTPException(status_code=400, detail=f"Unknown source type: {source.type}")
            
            # Create fake doc IDs
            doc_id = f"doc{idx + 1}"
            doc_ids.append(doc_id)
            total_chars += len(text)
        
        # Approximate tokens (rough estimate: 1 token ≈ 4 characters)
        tokens = total_chars // 4
        
        log_json("INFO", "Ingestion complete", doc_count=len(doc_ids), tokens=tokens)
        
        return {
            "doc_ids": doc_ids,
            "tokens": tokens
        }
        
    except HTTPException:
        raise
    except Exception as e:
        log_json("ERROR", "Error ingesting content", error=str(e))
        raise HTTPException(status_code=500, detail=f"Error ingesting content: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8081"))
    uvicorn.run(app, host="0.0.0.0", port=port)
