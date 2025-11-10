# Summarize Service

Clusters and summarizes text content, generating TL;DR, clusters, and FAQs.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8002
```

## API

- `POST /summarize` - Summarize and cluster text

See http://localhost:8002/docs for OpenAPI documentation.

