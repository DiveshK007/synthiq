# Viz Service

Generates Mermaid graphs and visualizations from clusters and summaries.

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8003
```

## API

- `POST /visualize` - Generate Mermaid graph from clusters

See http://localhost:8003/docs for OpenAPI documentation.

