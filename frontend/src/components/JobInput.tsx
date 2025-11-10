import { useState } from 'react'
import { motion } from 'framer-motion'
import { Send, FileText, Link as LinkIcon } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'
import toast from 'react-hot-toast'

export default function JobInput() {
  const [input, setInput] = useState('')
  const [inputType, setInputType] = useState<'url' | 'text'>('url')
  const createJob = useAppStore((state) => state.createJob)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!input.trim()) {
      toast.error('Please enter a URL or text')
      return
    }
    
    try {
      await createJob(input)
      setInput('')
      toast.success('Job created successfully!')
    } catch (error) {
      toast.error('Failed to create job')
    }
  }
  
  return (
    <motion.div
      className="card"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
        New Research Job
      </h2>
      
      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setInputType('url')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
            inputType === 'url'
              ? 'bg-coral-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          <LinkIcon className="w-4 h-4" />
          <span>URL</span>
        </button>
        <button
          onClick={() => setInputType('text')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors duration-200 ${
            inputType === 'text'
              ? 'bg-coral-500 text-white'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
          }`}
        >
          <FileText className="w-4 h-4" />
          <span>Text</span>
        </button>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={
            inputType === 'url'
              ? 'Enter a URL to analyze...'
              : 'Paste or type text to analyze...'
          }
          className="input min-h-[120px] resize-none"
          rows={5}
        />
        
        <motion.button
          type="submit"
          className="btn-primary w-full flex items-center justify-center space-x-2"
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
        >
          <Send className="w-4 h-4" />
          <span>Analyze</span>
        </motion.button>
      </form>
    </motion.div>
  )
}

