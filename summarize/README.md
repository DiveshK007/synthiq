# Summarize Service

Clusters and summarizes text content.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8082  # Optional, defaults to 8082

python -m uvicorn main:app --host 0.0.0.0 --port 8082
```

Or:

```bash
python main.py
```

## API

- `GET /healthz` - Health check
- `POST /summarize` - Summarize and cluster documents

See http://localhost:8082/docs for OpenAPI documentation.
