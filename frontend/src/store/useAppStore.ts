import { create } from 'zustand'

const API_BASE_URL = 'http://localhost:8080'

export interface Progress {
  ingestor: number
  summarize: number
  viz: number
}

export interface Cluster {
  label: string
  summary: string
  citations: Array<{
    doc_id: string
    spans: Array<{
      chunk_id: number
      start: number
      end: number
    }>
  }>
}

export interface FAQ {
  question: string
  answer: string
}

export interface Result {
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

interface AppState {
  jobId: string | null
  status: 'idle' | 'queued' | 'running' | 'done' | 'error'
  progress: Progress
  result: Result | null
  error: string | null
  setJobId: (jobId: string | null) => void
  setStatus: (status: AppState['status']) => void
  setProgress: (progress: Partial<Progress>) => void
  setResult: (result: Result | null) => void
  setError: (error: string | null) => void
  reset: () => void
}

export const useAppStore = create<AppState>((set) => ({
  jobId: null,
  status: 'idle',
  progress: {
    ingestor: 0,
    summarize: 0,
    viz: 0
  },
  result: null,
  error: null,
  
  setJobId: (jobId) => set({ jobId }),
  setStatus: (status) => set({ status }),
  setProgress: (progress) => set((state) => ({
    progress: { ...state.progress, ...progress }
  })),
  setResult: (result) => set({ result }),
  setError: (error) => set({ error }),
  reset: () => set({
    jobId: null,
    status: 'idle',
    progress: { ingestor: 0, summarize: 0, viz: 0 },
    result: null,
    error: null
  })
}))

export async function createJob(sources: Array<{ type: string; value: string }>, goal: string): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sources, goal })
  })
  
  if (!response.ok) {
    throw new Error('Failed to create job')
  }
  
  const data = await response.json()
  return data.job_id
}

export async function getJob(jobId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`)
  
  if (!response.ok) {
    throw new Error('Failed to fetch job')
  }
  
  return response.json()
}
