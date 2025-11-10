# Orchestrator Service

Coordinates the research summarization pipeline.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
export INGESTOR_URL=http://localhost:8081
export SUMMARIZE_URL=http://localhost:8082
export VIZ_URL=http://localhost:8083
export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8080  # Optional, defaults to 8080

python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

Or:

```bash
python main.py
```

## API

- `GET /healthz` - Health check
- `POST /jobs` - Create a new job
- `GET /jobs/{job_id}` - Get job status and results

See http://localhost:8080/docs for OpenAPI documentation.
