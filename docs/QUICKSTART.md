# SynthIQ Quickstart Guide

Get SynthIQ running locally in minutes.

## Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

## Local Development Setup

### 1. Backend Services

Start each backend service in a separate terminal:

#### Terminal 1: Orchestrator
```bash
cd orchestrator
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### Terminal 2: Ingestor
```bash
cd ingestor
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

#### Terminal 3: Summarize
```bash
cd summarize
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
```

#### Terminal 4: Viz
```bash
cd viz
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8003
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

### 3. Access the Application

- Frontend: http://localhost:5173
- Orchestrator API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Using Docker Compose

Alternatively, use Docker Compose to run all services:

```bash
cd infra
docker-compose up --build
```

## Testing the API

### Create a Job

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"input": "https://example.com"}'
```

### Get Job Status

```bash
curl http://localhost:8000/jobs/{job_id}
```

## Troubleshooting

### Port Already in Use

If a port is already in use, change the port in the service's `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=8000)  # Change port number
```

### CORS Issues

CORS is enabled for all origins in development. For production, update CORS settings in each service's `main.py`.

### Service Connection Issues

Ensure all backend services are running before creating jobs. The orchestrator depends on ingestor, summarize, and viz services.

## Next Steps

- See [API Documentation](API.md) for detailed API reference
- Check individual service READMEs for service-specific documentation
- Explore the codebase to understand the architecture

