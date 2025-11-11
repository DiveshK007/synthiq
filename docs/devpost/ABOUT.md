# About SynthIQ

## What is SynthIQ?

SynthIQ is an intelligent research summarization platform that helps researchers, students, and knowledge workers quickly synthesize information from multiple sources. It automatically ingests content from URLs and PDFs, extracts key insights through advanced clustering algorithms, and presents results as interactive knowledge graphs.

## The Problem

Research often involves reading dozens of articles, papers, and documents. Manually extracting themes, summarizing content, and identifying relationships is time-consuming and error-prone. Researchers need a tool that can:

- Process multiple sources simultaneously
- Identify key themes and clusters
- Generate concise summaries with citations
- Visualize relationships between concepts

## Our Solution

SynthIQ uses a microservices architecture with specialized agents:

1. **Ingestor**: Fetches and chunks content from URLs and PDFs
2. **Summarizer**: Uses TF-IDF + KMeans clustering with extractive summarization
3. **Visualizer**: Generates Mermaid knowledge graphs
4. **Orchestrator**: Coordinates the pipeline with real-time updates

## Key Features

- **Multi-source ingestion**: URLs, PDFs, and raw text
- **Deterministic clustering**: Reproducible results with seed-based KMeans
- **Extractive summarization**: TextRank-style sentence ranking
- **Provenance tracking**: Citations with exact document and chunk references
- **Real-time updates**: WebSocket-based progress tracking
- **Knowledge graphs**: Interactive Mermaid visualizations

## Technology Stack

- **Backend**: FastAPI, SQLModel, scikit-learn, BeautifulSoup4
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Zustand
- **Infrastructure**: Docker, docker-compose, GitHub Actions
- **Algorithms**: TF-IDF vectorization, KMeans clustering, TextRank summarization

## Use Cases

- **Research synthesis**: Quickly understand themes across multiple papers
- **Literature reviews**: Identify key findings and relationships
- **Content analysis**: Extract insights from web articles and documents
- **Knowledge mapping**: Visualize connections between concepts

## Future Enhancements

- LLM-guided chunk ranking via Vertex AI
- Cloud Run deployment for scalability
- Pub/Sub pipeline for long-running jobs
- Authentication and multi-tenant support
- Advanced visualization options

