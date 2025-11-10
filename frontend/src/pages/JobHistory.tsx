import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Clock, CheckCircle, XCircle, Loader, Search } from 'lucide-react'
import { apiGet } from '../lib/api'
import { useJobsStore } from '../stores/jobs'
import { LoadingSkeleton } from '../components/LoadingSkeleton'
import type { Job } from '../types'

export default function JobHistory() {
  const navigate = useNavigate()
  const { jobsById, addJob, setCurrentJob } = useJobsStore()
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  
  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const jobs = await apiGet<Job[]>('/jobs')
        jobs.forEach(job => addJob(job))
      } catch (error) {
        console.error('Failed to fetch jobs:', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchJobs()
  }, [addJob])
  
  const jobs = Object.values(jobsById).sort((a, b) => 
    (b.created_at || 0) - (a.created_at || 0)
  )
  
  const filteredJobs = jobs.filter(job => {
    const matchesSearch = !searchQuery || 
      job.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (job.result?.tldr || '').toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesStatus = !filterStatus || job.status === filterStatus
    
    return matchesSearch && matchesStatus
  })
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'done':
        return <CheckCircle className="w-5 h-5 text-success" />
      case 'error':
        return <XCircle className="w-5 h-5 text-error" />
      case 'running':
        return <Loader className="w-5 h-5 text-warning animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-muted" />
    }
  }
  
  const formatTimestamp = (ms: number) => {
    return new Date(ms).toLocaleString()
  }
  
  return (
    <div className="pt-24 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <h1 className="text-3xl font-bold mb-8 text-slate-200 dark:text-slate-200">
            Job History
          </h1>
          
          {/* Search and Filter */}
          <div className="card mb-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-muted" />
                <input
                  type="text"
                  placeholder="Search jobs..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input pl-10"
                />
              </div>
              <div className="flex gap-2">
                {['queued', 'running', 'done', 'error'].map((status) => (
                  <button
                    key={status}
                    onClick={() => setFilterStatus(filterStatus === status ? null : status)}
                    className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                      filterStatus === status
                        ? 'bg-gradient-to-r from-primary to-accent text-white'
                        : 'bg-ink/50 dark:bg-ink/50 text-muted hover:text-slate-200'
                    }`}
                  >
                    {status.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
          
          {/* Job List */}
          {isLoading ? (
            <div className="card">
              <LoadingSkeleton />
            </div>
          ) : filteredJobs.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-muted text-lg mb-4">No jobs found</p>
              <button
                onClick={() => navigate('/')}
                className="btn-primary"
              >
                Create New Job
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <AnimatePresence>
                {filteredJobs.map((job) => (
                  <motion.div
                    key={job.id}
                    className="card cursor-pointer hover:shadow-xl transition-all duration-200"
                    onClick={() => {
                      setCurrentJob(job)
                      navigate(`/job/${job.id}`)
                    }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4 flex-1 min-w-0">
                        {getStatusIcon(job.status)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-1">
                            <span className="text-sm font-medium text-slate-200 dark:text-slate-200">
                              {job.id.substring(0, 8)}...
                            </span>
                            <span
                              className={`px-2 py-1 rounded text-xs font-semibold ${
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
                          </div>
                          {job.result?.tldr && (
                            <p className="text-sm text-muted line-clamp-2">
                              {job.result.tldr}
                            </p>
                          )}
                          <p className="text-xs text-muted mt-1">
                            {formatTimestamp(job.created_at || Date.now())}
                          </p>
                        </div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

