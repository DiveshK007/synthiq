import { motion } from 'framer-motion'

export default function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-8 bg-ink/50 rounded animate-pulse" />
      <div className="h-32 bg-ink/50 rounded animate-pulse" />
      <div className="h-24 bg-ink/50 rounded animate-pulse" />
    </div>
  )
}

export function ClusterSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {[1, 2, 3].map((i) => (
        <motion.div
          key={i}
          className="p-4 bg-ink/30 rounded-xl border border-ink/20"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <div className="h-6 bg-ink/50 rounded mb-3 animate-pulse" />
          <div className="h-4 bg-ink/50 rounded mb-2 animate-pulse" />
          <div className="h-4 bg-ink/50 rounded w-3/4 animate-pulse" />
        </motion.div>
      ))}
    </div>
  )
}

export function ProgressSkeleton() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i}>
          <div className="h-4 bg-ink/50 rounded mb-2 w-1/4 animate-pulse" />
          <div className="h-2 bg-ink/50 rounded-full animate-pulse" />
        </div>
      ))}
    </div>
  )
}

