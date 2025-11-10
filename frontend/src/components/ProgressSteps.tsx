import { motion } from 'framer-motion'
import type { JobProgress } from '../types'

interface ProgressStepsProps {
  progress: JobProgress
  status: 'queued' | 'running' | 'done' | 'error'
}

const steps = [
  { key: 'ingest' as const, label: 'Ingest' },
  { key: 'summarize' as const, label: 'Summarize' },
  { key: 'viz' as const, label: 'Visualize' },
]

export default function ProgressSteps({ progress, status }: ProgressStepsProps) {
  return (
    <div className="space-y-4" aria-live="polite">
      {steps.map((step, idx) => {
        const value = progress[step.key]
        const isActive = status === 'running' && value > 0 && value < 100
        const isComplete = value === 100
        
        return (
          <div key={step.key}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-slate-300 dark:text-slate-300">
                {step.label}
              </span>
              <span className="text-xs text-muted">
                {value}%
              </span>
            </div>
            <div className="w-full bg-[rgba(11,16,32,0.5)] dark:bg-[rgba(11,16,32,0.5)] rounded-full h-2 overflow-hidden">
              <motion.div
                className={`h-2 rounded-full ${
                  isComplete
                    ? 'bg-success'
                    : isActive
                    ? 'bg-gradient-to-r from-primary to-accent'
                    : 'bg-muted'
                }`}
                initial={{ width: 0 }}
                animate={{ width: `${value}%` }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}

