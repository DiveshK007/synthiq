# Infrastructure

Docker and Docker Compose configurations for SynthIQ.

## Docker Compose

Run all services with Docker Compose:

```bash
docker-compose -f docker-compose.yml up --build
```

This will start:
- Orchestrator (port 8000)
- Ingestor (port 8001)
- Summarize (port 8002)
- Viz (port 8003)
- Frontend (port 5173)

## Individual Services

Each service has its own Dockerfile. Build and run individually:

```bash
cd orchestrator
docker build -t synthiq-orchestrator .
docker run -p 8000:8000 synthiq-orchestrator
```

## Cloud Run (Future)

See `cloud-run/` directory for Cloud Run deployment configurations (to be added).

