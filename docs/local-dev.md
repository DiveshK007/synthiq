# Local Development Guide

Step-by-step instructions to run SynthIQ services locally.

## Prerequisites

- Python 3.11+
- Virtual environment support (`python -m venv`)

## Step-by-Step Setup

### 1. Orchestrator Service (Terminal 1)

```bash
cd orchestrator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

export INGESTOR_URL=http://localhost:8081
export SUMMARIZE_URL=http://localhost:8082
export VIZ_URL=http://localhost:8083
export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8080

python -m uvicorn main:app --host 0.0.0.0 --port 8080
```

### 2. Ingestor Service (Terminal 2)

```bash
cd ingestor
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8081

python -m uvicorn main:app --host 0.0.0.0 --port 8081
```

### 3. Summarize Service (Terminal 3)

```bash
cd summarize
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8082

python -m uvicorn main:app --host 0.0.0.0 --port 8082
```

### 4. Viz Service (Terminal 4)

```bash
cd viz
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8083

python -m uvicorn main:app --host 0.0.0.0 --port 8083
```

### 5. Frontend (Terminal 5)

```bash
cd frontend
npm install
npm run dev
```

## Verify Services

Check all services are running:

```bash
curl http://localhost:8080/healthz  # Orchestrator
curl http://localhost:8081/healthz  # Ingestor
curl http://localhost:8082/healthz  # Summarize
curl http://localhost:8083/healthz  # Viz
```

All should return: `{"ok":true}`

## Test End-to-End

Create a test job:

```bash
curl -X POST http://localhost:8080/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [{"type": "url", "value": "https://example.com"}],
    "goal": "Understand the main concepts"
  }'
```

This returns a `job_id`. Poll for results:

```bash
curl http://localhost:8080/jobs/{job_id}
```

## Troubleshooting

### Port Already in Use

If a port is already in use, change the `PORT` environment variable:

```bash
export PORT=8084  # Use a different port
```

### CORS Issues

Ensure `FRONTEND_ORIGIN` matches your frontend URL exactly (including protocol and port).

### Service Connection Errors

Make sure all services are running before creating jobs. The orchestrator depends on:
- Ingestor (port 8081)
- Summarize (port 8082)
- Viz (port 8083)

## Environment Variables

### Orchestrator

- `INGESTOR_URL` - URL of ingestor service (default: http://localhost:8081)
- `SUMMARIZE_URL` - URL of summarize service (default: http://localhost:8082)
- `VIZ_URL` - URL of viz service (default: http://localhost:8083)
- `FRONTEND_ORIGIN` - Frontend origin for CORS (default: http://localhost:5174)
- `PORT` - Port to run on (default: 8080)

### Other Services

- `FRONTEND_ORIGIN` - Frontend origin for CORS (default: http://localhost:5174)
- `PORT` - Port to run on (default: 8081, 8082, 8083 respectively)

