import { useEffect, useRef, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Copy, ExternalLink, Download, Share2, RefreshCw } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiGet } from '../lib/api'
import { useJobsStore } from '../stores/jobs'
import { usePolling } from '../hooks/usePolling'
import { renderMermaid } from '../lib/mermaid'
import ProgressSteps from '../components/ProgressSteps'
import { LoadingSkeleton, ClusterSkeleton, ProgressSkeleton } from '../components/LoadingSkeleton'
import type { Job } from '../types'

export default function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { jobsById, addJob, updateJob, lastFormValues, setLastFormValues } = useJobsStore()
  
  const [pollingInterval, setPollingInterval] = useState(1000)
  const [pollingEnabled, setPollingEnabled] = useState(true)
  const mermaidContainerRef = useRef<HTMLDivElement>(null)
  const [mermaidRendered, setMermaidRendered] = useState(false)
  
  const job = id ? jobsById[id] : null
  
  // Fetch initial job data
  useEffect(() => {
    if (!id) return
    
    const fetchJob = async () => {
      try {
        const jobData = await apiGet<Job>(`/jobs/${id}`)
        addJob(jobData)
      } catch (error) {
        console.error('Failed to fetch job:', error)
      }
    }
    
    if (!job) {
      fetchJob()
    }
  }, [id, job, addJob])
  
  // WebSocket for real-time updates (preferred)
  const useWebSocketEnabled = !!id && job?.status !== 'done' && job?.status !== 'error'
  useWebSocket({
    jobId: id || null,
    enabled: useWebSocketEnabled,
    onMessage: (data: Job) => {
      updateJob(data.id, data)
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
      // Fall back to polling if WebSocket fails
      setPollingEnabled(true)
    },
  })
  
  // Polling as fallback (if WebSocket not available or fails)
  usePolling({
    id: id || '',
    intervalMs: pollingInterval,
    enabled: !useWebSocketEnabled && pollingEnabled && !!id && job?.status !== 'done' && job?.status !== 'error',
    onData: (data: Job) => {
      updateJob(data.id, data)
      
      // Backoff to 2s after 15s
      const jobCreatedAt = job?.created_at || job?.result?.created_at || Date.now()
      if (Date.now() - jobCreatedAt > 15000) {
        setPollingInterval(2000)
      }
      
      // Stop after 60s if still queued
      if (Date.now() - jobCreatedAt > 60000 && data.status === 'queued') {
        setPollingEnabled(false)
        toast('Job is taking longer than expected...', { icon: '⏳' })
      }
    },
    fetchFn: async () => {
      if (!id) throw new Error('No job ID')
      return apiGet<Job>(`/jobs/${id}`)
    },
  })
  
  // Render Mermaid when result is available
  useEffect(() => {
    if (job?.result?.assets?.mermaid && mermaidContainerRef.current && !mermaidRendered) {
      renderMermaid(job.id, job.result.assets.mermaid, mermaidContainerRef.current)
        .then(() => setMermaidRendered(true))
        .catch((error) => console.error('Mermaid render error:', error))
    }
  }, [job?.result?.assets?.mermaid, mermaidRendered, job?.id])
  
  if (!job) {
    return (
      <div className="pt-24 pb-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="card">
            <LoadingSkeleton />
          </div>
        </div>
      </div>
    )
  }
  
  const handleCopyMermaid = () => {
    if (job.result?.assets?.mermaid) {
      navigator.clipboard.writeText(job.result.assets.mermaid)
      toast.success('Mermaid code copied!')
    }
  }
  
  const handleCopyJobId = () => {
    navigator.clipboard.writeText(job.id)
    toast.success('Job ID copied!')
  }
  
  const handleCopyTLDR = () => {
    if (job.result?.tldr) {
      navigator.clipboard.writeText(job.result.tldr)
      toast.success('TL;DR copied!')
    }
  }
  
  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(job, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `synthiq-job-${job.id}.json`
    a.click()
    URL.revokeObjectURL(url)
    toast.success('Job exported!')
  }
  
  const handleShareLink = () => {
    navigator.clipboard.writeText(window.location.href)
    toast.success('Link copied!')
  }
  
  const handleRetry = () => {
    if (lastFormValues) {
      setLastFormValues(lastFormValues)
      navigate('/')
    } else {
      navigate('/')
    }
  }
  
  const formatTimestamp = (ms: number) => {
    return new Date(ms).toLocaleString()
  }
  
  const formatDuration = (ms: number) => {
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    return `${minutes}m ${seconds % 60}s`
  }
  
  return (
    <div className="pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        {/* Header Card */}
        <motion.div
          className="card mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex-1">
              <div className="flex items-center space-x-3 mb-2">
                <span
                  className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                    job.status === 'done'
                      ? 'bg-success/20 text-success'
                      : job.status === 'error'
                      ? 'bg-error/20 text-error'
                      : job.status === 'running'
                      ? 'bg-warning/20 text-warning'
                      : 'bg-muted/20 text-muted'
                  }`}
                >
                  {job.status.toUpperCase()}
                </span>
                {job.result && (
                  <span className="text-sm text-muted">
                    Runtime: {formatDuration(job.result.duration_ms)}
                  </span>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <p className="text-sm text-muted">
                  Created: {formatTimestamp(job.created_at || job.result?.created_at || Date.now())}
                </p>
                <span className="text-muted">•</span>
                <button
                  onClick={handleCopyJobId}
                  className="text-xs text-primary hover:underline flex items-center space-x-1"
                  aria-label="Copy Job ID"
                >
                  <span>ID: {job.id.substring(0, 8)}...</span>
                  <Copy className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        </motion.div>
        
        {/* Progress Section */}
        {job.status !== 'done' && job.status !== 'error' && (
          <motion.div
            className="card mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <h2 className="text-xl font-semibold mb-4 text-slate-200 dark:text-slate-200">
              Progress
            </h2>
            {job.status === 'queued' ? (
              <ProgressSkeleton />
            ) : (
              <ProgressSteps progress={job.progress} status={job.status} />
            )}
            {job.status === 'queued' && (
              <p className="mt-4 text-sm text-muted">Still running...</p>
            )}
          </motion.div>
        )}
        
        {/* Error State */}
        {job.status === 'error' && (
          <motion.div
            className="card mb-6 bg-error/10 border-error/20"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h2 className="text-xl font-semibold mb-2 text-error">Error</h2>
            <p className="text-slate-200 dark:text-slate-200 mb-4">{job.error || 'Unknown error'}</p>
            <motion.button
              onClick={handleRetry}
              className="flex items-center space-x-2 px-4 py-2 bg-error hover:bg-error/80 rounded-xl text-white font-medium transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry</span>
            </motion.button>
          </motion.div>
        )}
        
        {/* Result Section */}
        {job.result && (
          <div className="space-y-6">
            {/* TL;DR */}
            <motion.div
              className="card"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-slate-200 dark:text-slate-200">
                  TL;DR
                </h2>
                <motion.button
                  onClick={handleCopyTLDR}
                  className="p-2 hover:bg-ink/50 rounded-lg transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  aria-label="Copy TL;DR"
                >
                  <Copy className="w-4 h-4 text-muted" />
                </motion.button>
              </div>
              <p className="text-slate-200 dark:text-slate-200 leading-relaxed">
                {job.result.tldr}
              </p>
            </motion.div>
            
            {/* Clusters */}
            {job.result.clusters && job.result.clusters.length > 0 ? (
              <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h2 className="text-xl font-semibold mb-4 text-slate-200 dark:text-slate-200">
                  Clusters
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {job.result.clusters.map((cluster, idx) => (
                    <ClusterCard key={idx} cluster={cluster} />
                  ))}
                </div>
              </motion.div>
            ) : (
              <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h2 className="text-xl font-semibold mb-4 text-slate-200 dark:text-slate-200">
                  Clusters
                </h2>
                <ClusterSkeleton />
              </motion.div>
            )}
            
            {/* FAQs */}
            {job.result.faqs && job.result.faqs.length > 0 && (
              <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                <h2 className="text-xl font-semibold mb-4 text-slate-200 dark:text-slate-200">
                  FAQs
                </h2>
                <div className="space-y-4">
                  {job.result.faqs.map((faq, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-ink/30 dark:bg-ink/30 rounded-xl border border-ink/20"
                    >
                      <h3 className="font-semibold text-slate-200 dark:text-slate-200 mb-2">
                        {faq.q}
                      </h3>
                      <p className="text-sm text-slate-300 dark:text-slate-300">{faq.a}</p>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
            
            {/* Graph & Assets */}
            {job.result.assets && (
              <motion.div
                className="card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-xl font-semibold text-slate-200 dark:text-slate-200">
                    Knowledge Graph
                  </h2>
                  <motion.button
                    onClick={handleCopyMermaid}
                    className="flex items-center space-x-2 px-3 py-1 bg-ink/50 hover:bg-ink/70 rounded-lg text-sm text-slate-200 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Copy className="w-4 h-4" />
                    <span>Copy Mermaid</span>
                  </motion.button>
                </div>
                
                <div
                  ref={mermaidContainerRef}
                  className="bg-ink/50 dark:bg-ink/50 rounded-xl p-4 min-h-[200px] overflow-x-auto"
                />
                
                <div className="flex flex-wrap gap-3 mt-4">
                  {job.result.assets.graph_png_url && (
                    <a
                      href={job.result.assets.graph_png_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 px-3 py-1 bg-ink/50 hover:bg-ink/70 rounded-lg text-sm text-slate-200 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Open PNG</span>
                    </a>
                  )}
                  {job.result.assets.slides_pdf_url && (
                    <a
                      href={job.result.assets.slides_pdf_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-2 px-3 py-1 bg-ink/50 hover:bg-ink/70 rounded-lg text-sm text-slate-200 transition-colors"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Open Slides PDF</span>
                    </a>
                  )}
                </div>
              </motion.div>
            )}
          </div>
        )}
        
        {/* Action Bar */}
        <motion.div
          className="fixed bottom-0 left-0 right-0 bg-ink/90 dark:bg-ink/90 backdrop-blur-md border-t border-ink/20 p-4 lg:sticky lg:bottom-auto lg:mt-6 lg:rounded-xl"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          <div className="max-w-7xl mx-auto flex flex-wrap items-center justify-center gap-4">
            <motion.button
              onClick={handleExportJSON}
              className="flex items-center space-x-2 px-4 py-2 bg-ink/50 hover:bg-ink/70 rounded-xl text-slate-200 font-medium transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Download className="w-4 h-4" />
              <span>Export JSON</span>
            </motion.button>
            <motion.button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-primary to-accent rounded-xl text-white font-medium transition-all duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <span>Create New Job</span>
            </motion.button>
            <motion.button
              onClick={handleShareLink}
              className="flex items-center space-x-2 px-4 py-2 bg-ink/50 hover:bg-ink/70 rounded-xl text-slate-200 font-medium transition-colors"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <Share2 className="w-4 h-4" />
              <span>Share Link</span>
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function ClusterCard({ cluster }: { cluster: { label: string; summary: string; citations: any[] } }) {
  const [expanded, setExpanded] = useState(false)
  
  return (
    <motion.div
      className="p-4 bg-ink/30 dark:bg-ink/30 rounded-xl border border-ink/20"
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ scale: 1.02 }}
    >
      <h3 className="font-semibold text-slate-200 dark:text-slate-200 mb-2">
        {cluster.label}
      </h3>
      <p className="text-sm text-slate-300 dark:text-slate-300 line-clamp-3 mb-3">
        {cluster.summary}
      </p>
      {cluster.citations && cluster.citations.length > 0 && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-primary hover:underline"
        >
          {expanded ? 'Hide' : 'Show'} citations ({cluster.citations.length})
        </button>
      )}
      {expanded && cluster.citations && (
        <div className="mt-2 space-y-1">
          {cluster.citations.map((citation, idx) => (
            <div key={idx} className="text-xs text-muted">
              {citation.doc_id.substring(0, 8)}...
            </div>
          ))}
        </div>
      )}
    </motion.div>
  )
}

