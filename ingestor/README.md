# Ingestor Service

Fetches and cleans raw content from URLs or text input.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8001
```

## API

- `POST /ingest` - Ingest content from URL or text

See http://localhost:8001/docs for OpenAPI documentation.

