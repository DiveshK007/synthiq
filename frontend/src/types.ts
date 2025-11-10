export type Source = {
  type: 'url' | 'pdf' | 'text'
  value: string
}

export type NewJobPayload = {
  sources: Source[]
  goal: string
}

export type JobProgress = {
  ingest: number
  summarize: number
  viz: number
}

export type CitationSpan = {
  chunk_id: number
  start: number
  end: number
}

export type Citation = {
  doc_id: string
  spans: CitationSpan[]
}

export type Cluster = {
  label: string
  summary: string
  citations: Citation[]
}

export type FAQ = {
  q: string
  a: string
}

export type JobResult = {
  tldr: string
  clusters: Cluster[]
  faqs: FAQ[]
  assets: {
    mermaid: string
    graph_png_url: string
    slides_pdf_url: string
  }
  created_at: number
  duration_ms: number
}

export type Job = {
  id: string
  status: 'queued' | 'running' | 'done' | 'error'
  error?: string
  progress: JobProgress
  result?: JobResult
  created_at?: number
}

