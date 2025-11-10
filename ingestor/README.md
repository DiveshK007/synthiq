# Ingestor Service

Fetches and cleans raw content from URLs, PDFs, or text.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8081  # Optional, defaults to 8081

python -m uvicorn main:app --host 0.0.0.0 --port 8081
```

Or:

```bash
python main.py
```

## API

- `GET /healthz` - Health check
- `POST /ingest` - Ingest content from URLs, PDFs, or text

See http://localhost:8081/docs for OpenAPI documentation.
