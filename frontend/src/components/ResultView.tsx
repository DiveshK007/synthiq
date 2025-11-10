import { motion } from 'framer-motion'
import { useAppStore } from '../store/useAppStore'

export default function ResultView() {
  const { result, status } = useAppStore()
  
  if (status !== 'done' || !result) {
    return null
  }
  
  return (
    <motion.div
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* TL;DR */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
          TL;DR
        </h2>
        <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
          {result.tldr}
        </p>
      </div>
      
      {/* Clusters */}
      {result.clusters && result.clusters.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
            Clusters
          </h2>
          <div className="space-y-4">
            {result.clusters.map((cluster, idx) => (
              <motion.div
                key={idx}
                className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.1 }}
              >
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {cluster.label}
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300 mb-3">
                  {cluster.summary}
                </p>
                {cluster.citations && cluster.citations.length > 0 && (
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    Citations: {cluster.citations.length}
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      )}
      
      {/* FAQs */}
      {result.faqs && result.faqs.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
            FAQs
          </h2>
          <div className="space-y-4">
            {result.faqs.map((faq, idx) => (
              <motion.div
                key={idx}
                className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl border border-gray-200 dark:border-gray-600"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: idx * 0.1 }}
              >
                <h3 className="font-semibold text-gray-900 dark:text-gray-100 mb-2">
                  {faq.question}
                </h3>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  {faq.answer}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      )}
      
      {/* Mermaid Graph */}
      {result.assets && result.assets.mermaid && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-gray-100">
            Knowledge Graph (Mermaid)
          </h2>
          <div className="bg-gray-900 dark:bg-gray-950 rounded-xl p-4 overflow-x-auto">
            <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap">
              {result.assets.mermaid}
            </pre>
          </div>
        </div>
      )}
    </motion.div>
  )
}

