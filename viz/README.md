# Viz Service

Generates Mermaid graphs and visualizations.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
export FRONTEND_ORIGIN=http://localhost:5174
export PORT=8083  # Optional, defaults to 8083

python -m uvicorn main:app --host 0.0.0.0 --port 8083
```

Or:

```bash
python main.py
```

## API

- `GET /healthz` - Health check
- `POST /viz` - Generate Mermaid graph from clusters

See http://localhost:8083/docs for OpenAPI documentation.
