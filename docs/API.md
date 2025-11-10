# SynthIQ API Documentation

Complete API reference for all SynthIQ services.

## Orchestrator Service (Port 8000)

Main service that coordinates the pipeline.

### `POST /jobs`

Create a new research job.

**Request:**
```json
{
  "input": "https://example.com/article"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 0,
  "result": null,
  "error": null
}
```

### `GET /jobs/{job_id}`

Get job status and results.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "tldr": "Summary of the content...",
    "clusters": [
      {
        "id": "cluster-1",
        "title": "Main Topic",
        "summary": "Cluster summary...",
        "keywords": ["keyword1", "keyword2"]
      }
    ],
    "faqs": [
      {
        "question": "What is the main topic?",
        "answer": "The main topic is..."
      }
    ],
    "graph": "graph TD\n    TLDR[\"TL;DR\"]..."
  },
  "error": null
}
```

**Status Values:**
- `pending` - Job created, not yet processing
- `processing` - Job is being processed
- `completed` - Job completed successfully
- `error` - Job failed with error

## Ingestor Service (Port 8001)

Fetches and cleans raw content from URLs or text.

### `POST /ingest`

Ingest content from URL or text.

**Request:**
```json
{
  "input": "https://example.com/article"
}
```

**Response:**
```json
{
  "text": "Cleaned text content...",
  "source": "url",
  "metadata": {
    "url": "https://example.com/article",
    "title": "Article Title",
    "content_length": 5000,
    "status_code": 200
  }
}
```

## Summarize Service (Port 8002)

Clusters and summarizes text content.

### `POST /summarize`

Summarize and cluster text.

**Request:**
```json
{
  "text": "Long text content to summarize..."
}
```

**Response:**
```json
{
  "tldr": "Brief summary of the content...",
  "clusters": [
    {
      "id": "cluster-1",
      "title": "Cluster Title",
      "summary": "Cluster summary...",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ],
  "faqs": [
    {
      "question": "What is the main topic?",
      "answer": "The main topic is..."
    }
  ]
}
```

## Viz Service (Port 8003)

Generates Mermaid graphs and visualizations.

### `POST /visualize`

Generate Mermaid graph from clusters.

**Request:**
```json
{
  "clusters": [
    {
      "id": "cluster-1",
      "title": "Cluster Title",
      "summary": "Cluster summary...",
      "keywords": ["keyword1", "keyword2"]
    }
  ],
  "tldr": "Brief summary..."
}
```

**Response:**
```json
{
  "graph": "graph TD\n    TLDR[\"TL;DR: Summary\"]\n    Cluster0[\"Cluster Title\"]\n    TLDR --> Cluster0\n    K0_0[\"keyword1\"]\n    Cluster0 --> K0_0"
}
```

## Error Responses

All services return errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

## Interactive API Documentation

Each service provides interactive OpenAPI documentation:

- Orchestrator: http://localhost:8000/docs
- Ingestor: http://localhost:8001/docs
- Summarize: http://localhost:8002/docs
- Viz: http://localhost:8003/docs

## Example Workflow

1. **Create a job:**
   ```bash
   curl -X POST http://localhost:8000/jobs \
     -H "Content-Type: application/json" \
     -d '{"input": "https://example.com/article"}'
   ```

2. **Poll for results:**
   ```bash
   curl http://localhost:8000/jobs/{job_id}
   ```

3. **Check status:**
   - `status: "processing"` - Job is being processed
   - `status: "completed"` - Job completed, check `result` field
   - `status: "error"` - Job failed, check `error` field

## Rate Limiting

Currently, there are no rate limits. For production, implement rate limiting per service.

## Authentication

Currently, there is no authentication. For production, add authentication middleware (e.g., JWT tokens).

