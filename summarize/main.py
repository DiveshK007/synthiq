"""
Summarize service - clusters and summarizes text
"""
import json
import logging
import os
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from pydantic import ValidationError
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from schemas import SummarizeRequest, SummarizeResponse, Cluster, FAQ, Citation, CitationSpan, Chunk

# Try to import clustering module
try:
    from clustering import generate_clusters
    CLUSTERING_AVAILABLE = True
except ImportError as e:
    CLUSTERING_AVAILABLE = False
    # Will log warning later when needed

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
    title="SynthIQ Summarize",
    description="Clusters and summarizes text content",
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


# OpenAI client (optional - falls back to placeholder if not configured)
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_client = None
use_openai = False

def get_openai_client():
    """Lazy initialization of OpenAI client"""
    global openai_client, use_openai
    if openai_client is None and openai_api_key:
        try:
            openai_client = OpenAI(api_key=openai_api_key)
            use_openai = True
        except Exception as e:
            log_json("WARN", "Failed to initialize OpenAI client", error=str(e))
            openai_client = None
            use_openai = False
    return openai_client


def log_json(level: str, message: str, **kwargs):
    """Log as JSON"""
    log_entry = {
        "level": level,
        "message": message,
        **kwargs
    }
    logger.info(json.dumps(log_entry))


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def summarize_with_openai(text: str, goal: str) -> dict:
    """Summarize text using OpenAI GPT-4"""
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI API key not configured")
    
    prompt = f"""You are a research assistant. Analyze the following content and provide:
1. A concise TL;DR summary (max 200 words)
2. 3-5 key clusters/themes with summaries
3. 2-3 frequently asked questions with answers

Research Goal: {goal}

Content:
{text[:8000]}  # Limit to avoid token limits

Format your response as JSON with keys: tldr, clusters (list of {{label, summary}}), faqs (list of {{q, a}}).
"""
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview"),
            messages=[
                {"role": "system", "content": "You are a research assistant that provides structured summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        content = response.choices[0].message.content
        # Try to parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        else:
            # Fallback: return structured response
            return {
                "tldr": content[:200],
                "clusters": [{"label": f"Cluster {i+1}", "summary": content} for i in range(3)],
                "faqs": [{"q": "What is the main topic?", "a": content[:100]}]
            }
    except Exception as e:
        log_json("ERROR", "OpenAI API error", error=str(e))
        raise


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"ok": True, "version": VERSION}


@app.get("/version")
async def version():
    """Version endpoint"""
    return {"version": VERSION, "service": "summarize"}


@app.post("/summarize", response_model=SummarizeResponse)
async def summarize(request: SummarizeRequest):
    """Summarize and cluster documents"""
    try:
        doc_ids = request.doc_ids
        chunks = request.chunks or []
        goal = request.goal
        seed = request.seed
        
        if not doc_ids:
            raise HTTPException(status_code=400, detail="doc_ids cannot be empty")
        
        # If we have chunks and clustering is available, use deterministic clustering
        if chunks and CLUSTERING_AVAILABLE:
            try:
                # Use TF-IDF + KMeans clustering with extractive summarization
                clusters = generate_clusters(chunks, goal, n_clusters=None, seed=seed)
                
                # Build TL;DR from cluster summaries
                tldr_sentences = [c.summary.split('.')[0] + '.' for c in clusters[:3] if c.summary]
                tldr = " ".join(tldr_sentences)
                if len(tldr) > 200:
                    tldr = tldr[:197] + "..."
                
                # Generate simple FAQs
                faqs = [
                    FAQ(
                        q=f"What are the main themes in research on {goal}?",
                        a=f"The research reveals {len(clusters)} key themes: " + 
                          ", ".join([c.label for c in clusters[:3]]) + "."
                    ),
                    FAQ(
                        q="What sources were analyzed?",
                        a=f"Analysis included {len(set(c.doc_id for cluster in clusters for c in cluster.citations))} documents."
                    )
                ]
                
                log_json("INFO", "Summarization complete (TF-IDF+KMeans)", 
                        cluster_count=len(clusters), chunk_count=len(chunks), seed=seed)
                
                return SummarizeResponse(
                    clusters=clusters,
                    tldr=tldr,
                    faqs=faqs
                )
            except Exception as e:
                log_json("WARN", "Clustering failed, using fallback", error=str(e))
                # Fall through to placeholder implementation
        
        # Try OpenAI if configured, otherwise use placeholder
        if use_openai:
            try:
                # For now, use placeholder text - in production, fetch actual document content
                placeholder_text = f"Documents related to {goal}. " * 20
                ai_result = await summarize_with_openai(placeholder_text, goal)
                
                # Convert to our format
                clusters = []
                for i, cluster_data in enumerate(ai_result.get("clusters", [])[:5]):
                    cluster = Cluster(
                        label=cluster_data.get("label", f"Cluster {i + 1}"),
                        summary=cluster_data.get("summary", ""),
                        citations=[
                            Citation(
                                doc_id=doc_ids[i % len(doc_ids)] if doc_ids else "doc1",
                                spans=[CitationSpan(chunk_id=1, start=0, end=80)]
                            )
                        ]
                    )
                    clusters.append(cluster)
                
                tldr = ai_result.get("tldr", "")[:200]
                faqs = [FAQ(q=faq.get("q", ""), a=faq.get("a", "")) for faq in ai_result.get("faqs", [])[:3]]
                
                log_json("INFO", "Summarization complete (OpenAI)", cluster_count=len(clusters), faq_count=len(faqs))
                
                return SummarizeResponse(
                    clusters=clusters,
                    tldr=tldr,
                    faqs=faqs
                )
            except Exception as e:
                log_json("WARN", "OpenAI summarization failed, using fallback", error=str(e))
                # Fall through to placeholder implementation
        
        # Placeholder implementation (fallback)
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
        
        log_json("INFO", "Summarization complete (placeholder)", cluster_count=len(clusters), faq_count=len(faqs))
        
        return SummarizeResponse(
            clusters=clusters,
            tldr=tldr,
            faqs=faqs
        )
        
    except HTTPException:
        raise
    except ValidationError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        log_json("ERROR", "Error summarizing", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error summarizing: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8082"))
    uvicorn.run(app, host="0.0.0.0", port=port)
