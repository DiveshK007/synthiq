import { motion } from 'framer-motion'
import { FileText, MessageSquare, Network } from 'lucide-react'
import { useAppStore } from '../store/useAppStore'

export default function JobResult() {
  const { currentJob } = useAppStore()
  
  if (!currentJob || currentJob.status !== 'completed' || !currentJob.result) {
    return (
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.2 }}
      >
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100">
          Results
        </h2>
        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
          {currentJob?.status === 'processing'
            ? 'Processing...'
            : 'Select a completed job to view results'}
        </p>
      </motion.div>
    )
  }
  
  const { tldr, clusters, faqs, graph } = currentJob.result
  
  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      {/* TL;DR */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100 flex items-center space-x-2">
          <FileText className="w-5 h-5 text-coral-500" />
          <span>TL;DR</span>
        </h2>
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {tldr}
        </p>
      </div>
      
      {/* Clusters */}
      {clusters && clusters.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100 flex items-center space-x-2">
            <Network className="w-5 h-5 text-indigo-500" />
            <span>Key Clusters</span>
          </h2>
          <div className="space-y-4">
            {clusters.map((cluster) => (
              <div
                key={cluster.id}
                className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {cluster.title}
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  {cluster.summary}
                </p>
                <div className="flex flex-wrap gap-2">
                  {cluster.keywords.map((keyword, idx) => (
                    <span
                      key={idx}
                      className="px-2 py-1 text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-700 dark:text-indigo-300 rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* FAQs */}
      {faqs && faqs.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100 flex items-center space-x-2">
            <MessageSquare className="w-5 h-5 text-coral-500" />
            <span>FAQs</span>
          </h2>
          <div className="space-y-4">
            {faqs.map((faq, idx) => (
              <div
                key={idx}
                className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
              >
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {faq.question}
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {faq.answer}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Graph */}
      {graph && (
        <div className="card">
          <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-gray-100 flex items-center space-x-2">
            <Network className="w-5 h-5 text-indigo-500" />
            <span>Knowledge Graph</span>
          </h2>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 overflow-x-auto">
            <pre className="text-xs text-gray-700 dark:text-gray-300 font-mono whitespace-pre-wrap">
              {graph}
            </pre>
          </div>
        </div>
      )}
    </motion.div>
  )
}

