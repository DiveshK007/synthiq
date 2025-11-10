import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { useAppStore, getJob } from '../store/useAppStore'

export default function JobPoller() {
  const { jobId, status, progress, setStatus, setProgress, setResult, setError } = useAppStore()
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null)
  
  useEffect(() => {
    if (!jobId || status === 'done' || status === 'error') {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
        pollIntervalRef.current = null
      }
      return
    }
    
    const poll = async () => {
      try {
        const job = await getJob(jobId)
        
        setStatus(job.status)
        
        if (job.progress) {
          setProgress(job.progress)
        }
        
        if (job.status === 'done' && job.result) {
          setResult(job.result)
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current)
            pollIntervalRef.current = null
          }
        } else if (job.status === 'error') {
          setError(job.error || 'Unknown error')
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current)
            pollIntervalRef.current = null
          }
        }
      } catch (error) {
        console.error('Failed to poll job:', error)
        setError(String(error))
        setStatus('error')
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
        }
      }
    }
    
    poll()
    pollIntervalRef.current = setInterval(poll, 1000)
    
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current)
        pollIntervalRef.current = null
      }
    }
  }, [jobId, status, setStatus, setProgress, setResult, setError])
  
  if (!jobId) {
    return null
  }
  
  const getStatusColor = () => {
    switch (status) {
      case 'queued':
        return 'text-yellow-600 dark:text-yellow-400'
      case 'running':
        return 'text-blue-600 dark:text-blue-400'
      case 'done':
        return 'text-green-600 dark:text-green-400'
      case 'error':
        return 'text-red-600 dark:text-red-400'
      default:
        return 'text-gray-600 dark:text-gray-400'
    }
  }
  
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h2 className="text-2xl font-bold mb-6 text-gray-900 dark:text-gray-100">
        Job Status
      </h2>
      
      <div className="space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Status
            </span>
            <span className={`text-sm font-semibold ${getStatusColor()}`}>
              {status.toUpperCase()}
            </span>
          </div>
        </div>
        
        <div className="space-y-3">
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600 dark:text-gray-400">Ingestor</span>
              <span className="text-xs text-gray-600 dark:text-gray-400">{progress.ingestor}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <motion.div
                className="bg-coral-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress.ingestor}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600 dark:text-gray-400">Summarize</span>
              <span className="text-xs text-gray-600 dark:text-gray-400">{progress.summarize}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <motion.div
                className="bg-indigo-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress.summarize}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
          
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs text-gray-600 dark:text-gray-400">Viz</span>
              <span className="text-xs text-gray-600 dark:text-gray-400">{progress.viz}%</span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <motion.div
                className="bg-gradient-to-r from-coral-500 to-indigo-500 h-2 rounded-full"
                initial={{ width: 0 }}
                animate={{ width: `${progress.viz}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

