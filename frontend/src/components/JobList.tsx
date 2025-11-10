import { motion, AnimatePresence } from 'framer-motion'
import { Clock, CheckCircle, XCircle, Loader } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

export default function JobList() {
  const { jobs, currentJob, setCurrentJob } = useAppStore()
  
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />
      case 'processing':
        return <Loader className="w-5 h-5 text-coral-500 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-400" />
    }
  }
  
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-500 bg-green-50 dark:bg-green-900/20'
      case 'error':
        return 'border-red-500 bg-red-50 dark:bg-red-900/20'
      case 'processing':
        return 'border-coral-500 bg-coral-50 dark:bg-coral-900/20'
      default:
        return 'border-gray-300 dark:border-gray-600'
    }
  }
  
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
        Job History
      </h2>
      
      <div className="space-y-3">
        <AnimatePresence>
          {jobs.length === 0 ? (
            <p className="text-gray-500 dark:text-gray-400 text-center py-8">
              No jobs yet. Create your first analysis above!
            </p>
          ) : (
            jobs.map((job) => (
              <motion.div
                key={job.id}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all duration-200 ${getStatusColor(
                  job.status
                )} ${currentJob?.id === job.id ? 'ring-2 ring-indigo-500' : ''}`}
                onClick={() => setCurrentJob(job)}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3 flex-1 min-w-0">
                    {getStatusIcon(job.status)}
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                        {job.input.substring(0, 50)}
                        {job.input.length > 50 ? '...' : ''}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                        {job.status === 'processing' && `Progress: ${job.progress}%`}
                        {job.status === 'completed' && 'Completed'}
                        {job.status === 'error' && job.error}
                      </p>
                    </div>
                  </div>
                </div>
                
                {job.status === 'processing' && (
                  <div className="mt-3">
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <motion.div
                        className="bg-coral-500 h-2 rounded-full"
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 0.3 }}
                      />
                    </div>
                  </div>
                )}
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

