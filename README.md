# SynthIQ

SynthIQ is a multi-agent research summarizer that ingests content from URLs and PDFs, extracts meaning through an orchestrator service, processes content via an ingestor service, clusters and summarizes insights with a summarize service, and visualizes results as knowledge graphs through a viz service, all coordinated by a Vite React frontend.

## Local Dev (no Docker)

### Terminal A (orchestrator):

```bash
python -m venv orchestrator/.venv && source orchestrator/.venv/bin/activate
pip install -r orchestrator/requirements.txt
export INGESTOR_URL=http://localhost:8081
export SUMMARIZE_URL=http://localhost:8082
export VIZ_URL=http://localhost:8083
export FRONTEND_ORIGIN=http://localhost:5174
python -m uvicorn orchestrator.main:app --host 0.0.0.0 --port 8080
```

### Terminal B (ingestor):

```bash
python -m venv ingestor/.venv && source ingestor/.venv/bin/activate
pip install -r ingestor/requirements.txt
python -m uvicorn ingestor.main:app --host 0.0.0.0 --port 8081
```

### Terminal C (summarize):

```bash
python -m venv summarize/.venv && source summarize/.venv/bin/activate
pip install -r summarize/requirements.txt
python -m uvicorn summarize.main:app --host 0.0.0.0 --port 8082
```

### Terminal D (viz):

```bash
python -m venv viz/.venv && source viz/.venv/bin/activate
pip install -r viz/requirements.txt
python -m uvicorn viz.main:app --host 0.0.0.0 --port 8083
```

### Terminal E (frontend):

```bash
cd frontend
npm i
npm run dev
```

## Smoke Tests

### Health Checks

```bash
curl http://localhost:8080/healthz
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8083/healthz
```

### Create a Job

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"type": "url", "value": "https://example.com"}],
    "goal": "Understand the main concepts"
  }'
```

## Testing

### Dev Dependencies

For testing, install pytest in the orchestrator service:

```bash
cd orchestrator
source .venv/bin/activate
pip install pytest
pytest test_orchestrator.py -v
```

