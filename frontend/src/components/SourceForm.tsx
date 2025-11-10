import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAppStore, createJob } from '../store/useAppStore'

export default function SourceForm() {
  const [sourceType, setSourceType] = useState<'url' | 'pdf'>('url')
  const [sourceValue, setSourceValue] = useState('')
  const [goal, setGoal] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const { setJobId, setStatus, reset } = useAppStore()
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!sourceValue.trim() || !goal.trim()) {
      return
    }
    
    setIsSubmitting(true)
    reset()
    setStatus('queued')
    
    try {
      const jobId = await createJob(
        [{ type: sourceType, value: sourceValue.trim() }],
        goal.trim()
      )
      setJobId(jobId)
      setStatus('queued')
    } catch (error) {
      setStatus('error')
      console.error('Failed to create job:', error)
    } finally {
      setIsSubmitting(false)
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
        New Research Job
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Source Type
          </label>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setSourceType('url')}
              className={`flex-1 px-4 py-2 rounded-xl transition-all duration-200 ${
                sourceType === 'url'
                  ? 'bg-coral-500 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              URL
            </button>
            <button
              type="button"
              onClick={() => setSourceType('pdf')}
              className={`flex-1 px-4 py-2 rounded-xl transition-all duration-200 ${
                sourceType === 'pdf'
                  ? 'bg-coral-500 text-white shadow-md'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
              }`}
            >
              PDF URL
            </button>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            {sourceType === 'url' ? 'URL' : 'PDF URL'}
          </label>
          <input
            type="text"
            value={sourceValue}
            onChange={(e) => setSourceValue(e.target.value)}
            placeholder={sourceType === 'url' ? 'https://example.com/article' : 'https://example.com/document.pdf'}
            className="input"
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Goal
          </label>
          <textarea
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="What do you want to learn from this content?"
            className="input min-h-[120px] resize-none"
            rows={5}
            required
          />
        </div>
        
        <motion.button
          type="submit"
          className="btn-primary w-full"
          disabled={isSubmitting}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          {isSubmitting ? 'Creating...' : 'Analyze'}
        </motion.button>
      </form>
    </motion.div>
  )
}

