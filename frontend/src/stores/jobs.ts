import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Job } from '../types'

interface JobsState {
  jobsById: Record<string, Job>
  currentJob: Job | null
  lastCreatedId: string | null
  lastFormValues: {
    sources: Array<{ type: 'url' | 'pdf' | 'text'; value: string }>
    goal: string
  } | null
  
  addJob: (job: Job) => void
  updateJob: (id: string, partial: Partial<Job>) => void
  setCurrentJob: (job: Job | null) => void
  setLastCreatedId: (id: string | null) => void
  setLastFormValues: (values: JobsState['lastFormValues']) => void
}

export const useJobsStore = create<JobsState>()(
  persist(
    (set) => ({
      jobsById: {},
      currentJob: null,
      lastCreatedId: null,
      lastFormValues: null,
      
      addJob: (job) =>
        set((state) => ({
          jobsById: { ...state.jobsById, [job.id]: job },
        })),
      
      updateJob: (id, partial) =>
        set((state) => {
          const existing = state.jobsById[id]
          if (!existing) return state
          
          const updated = { ...existing, ...partial }
          
          return {
            jobsById: {
              ...state.jobsById,
              [id]: updated,
            },
            currentJob: state.currentJob?.id === id ? updated : state.currentJob,
          }
        }),
      
      setCurrentJob: (job) => set({ currentJob: job }),
      
      setLastCreatedId: (id) => set({ lastCreatedId: id }),
      
      setLastFormValues: (values) => set({ lastFormValues: values }),
    }),
    {
      name: 'synthiq-jobs',
      partialize: (state) => ({
        jobsById: state.jobsById,
        lastFormValues: state.lastFormValues,
      }),
    }
  )
)

