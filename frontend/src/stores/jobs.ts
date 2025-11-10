import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { Job } from '../types'

interface JobsState {
  jobsById: Record<string, Job>
  lastCreatedId: string | null
  lastFormValues: {
    sources: Array<{ type: 'url' | 'pdf' | 'text'; value: string }>
    goal: string
  } | null
  
  addJob: (job: Job) => void
  updateJob: (id: string, partial: Partial<Job>) => void
  setLastCreatedId: (id: string | null) => void
  setLastFormValues: (values: JobsState['lastFormValues']) => void
}

export const useJobsStore = create<JobsState>()(
  persist(
    (set) => ({
      jobsById: {},
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
          
          return {
            jobsById: {
              ...state.jobsById,
              [id]: { ...existing, ...partial },
            },
          }
        }),
      
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

