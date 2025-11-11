# SynthIQ

SynthIQ is a multi-agent research summarizer that ingests content from URLs and PDFs, extracts meaning through an orchestrator service, processes content via an ingestor service, clusters and summarizes insights with a summarize service, and visualizes results as knowledge graphs through a viz service, all coordinated by a Vite React frontend.

## Local with Docker

### Quick Start

```bash
# Build and start all services
docker compose up --build

# Services will be available at:
# - Orchestrator: http://localhost:8080
# - Ingestor: http://localhost:8081
# - Summarize: http://localhost:8082
# - Viz: http://localhost:8083
# - Frontend: http://localhost:5174
```

### Health Checks

```bash
curl http://localhost:8080/healthz
curl http://localhost:8081/healthz
curl http://localhost:8082/healthz
curl http://localhost:8083/healthz
```

### Stop Services

```bash
docker compose down
```

### Dev Containers (VS Code/Cursor)

The repository includes a `.devcontainer/devcontainer.json` configuration for VS Code/Cursor Dev Containers. This provides:

- Python 3.11 and Node 20 pre-installed
- Docker-in-Docker support
- Port forwarding for all services
- Pre-configured extensions and settings

To use:
1. Open the repository in VS Code/Cursor
2. When prompted, click "Reopen in Container"
3. All dependencies will be installed automatically

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

### Quick Test Commands

```bash
# Run all tests
make test

# Run linting
make lint

# Format code
make fmt

# Install all dependencies
make install
```

### Manual Testing

For testing individual services:

```bash
# Orchestrator tests
cd orchestrator
source .venv/bin/activate
pip install pytest httpx
pytest tests/ -v

# E2E test (requires all services running)
pytest orchestrator/tests/test_e2e.py -v
```

### Test Coverage

- Unit tests for each service (`/healthz`, `/version` endpoints)
- E2E test that spins up downstream services and tests full job flow
- Validation tests for request/response models

## Roadmap

### Short-term (Current Sprint)
- ✅ Production-grade API contracts with Pydantic validation
- ✅ Rate limiting and request size guards
- ✅ E2E testing infrastructure
- ✅ Safety rails (URL validation, script stripping)

### Medium-term
- [ ] Agentic extraction (LLM-guided chunk ranking via Vertex AI)
- [ ] Cloud Run deployment (once billing is configured)
- [ ] Pub/Sub pipeline for long-running jobs
- [ ] Firestore for job persistence
- [ ] Docker + Dev Containers for one-command local up
- [ ] Basic clustering + extractive summaries (deterministic with TF-IDF + KMeans)
- [ ] Architecture documentation with Mermaid diagrams

### Long-term
- [ ] Authentication with Supabase Auth
- [ ] Monitoring and observability (Prometheus, Sentry)
- [ ] Comprehensive test coverage (80%+)
- [ ] Performance optimization and caching
- [ ] Multi-tenant support
- [ ] Advanced visualization options (interactive graphs, export formats)

See [docs/ENHANCEMENTS.md](docs/ENHANCEMENTS.md) for detailed enhancement plans.

