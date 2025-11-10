# Orchestrator Service

Coordinates the research summarization pipeline by calling ingestor → summarize → viz services.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

## API

- `POST /jobs` - Create a new job
- `GET /jobs/{job_id}` - Get job status and results

See http://localhost:8000/docs for OpenAPI documentation.

