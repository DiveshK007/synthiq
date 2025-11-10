import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { X, Plus } from 'lucide-react'
import toast from 'react-hot-toast'
import { apiPost } from '../lib/api'
import { useJobsStore } from '../stores/jobs'
import type { Source } from '../types'

const GOAL_PRESETS = [
  'Executive summary',
  'Risk & opportunities',
  'Competitor highlights',
]

export default function NewJob() {
  const navigate = useNavigate()
  const { setLastCreatedId, setLastFormValues } = useJobsStore()
  
  const [activeTab, setActiveTab] = useState<'url' | 'pdf' | 'text'>('url')
  const [sources, setSources] = useState<Source[]>([])
  const [currentInput, setCurrentInput] = useState('')
  const [goal, setGoal] = useState('')
  const [selectedPreset, setSelectedPreset] = useState<string | null>(null)
  const [autoFAQ, setAutoFAQ] = useState(true)
  const [generateSlides, setGenerateSlides] = useState(false)
  const [knowledgeGraph, setKnowledgeGraph] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const validateUrl = (url: string): boolean => {
    try {
      const parsed = new URL(url)
      return parsed.protocol === 'http:' || parsed.protocol === 'https:'
    } catch {
      return false
    }
  }
  
  const handleAddSource = () => {
    if (!currentInput.trim()) return
    
    if (activeTab === 'url' || activeTab === 'pdf') {
      if (!validateUrl(currentInput.trim())) {
        toast.error('Please enter a valid URL')
        return
      }
    }
    
    setSources([...sources, { type: activeTab, value: currentInput.trim() }])
    setCurrentInput('')
  }
  
  const handleRemoveSource = (index: number) => {
    setSources(sources.filter((_, i) => i !== index))
  }
  
  const handlePresetSelect = (preset: string) => {
    setGoal(preset)
    setSelectedPreset(preset)
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (sources.length === 0) {
      toast.error('Please add at least one source')
      return
    }
    
    if (!goal.trim()) {
      toast.error('Please enter a goal')
      return
    }
    
    setIsSubmitting(true)
    
    try {
      // Save form values for potential retry
      setLastFormValues({ sources, goal })
      
      const response = await apiPost<{ job_id: string }>('/jobs', {
        sources,
        goal,
      })
      
      setLastCreatedId(response.job_id)
      toast.success('Job created successfully!')
      navigate(`/job/${response.job_id}`)
    } catch (error) {
      console.error('Failed to create job:', error)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const canSubmit = sources.length > 0 && goal.trim().length > 0
  
  return (
    <div className="pt-24 pb-12" style={{ minHeight: 'calc(100vh - 4rem)' }}>
      <motion.div
        className="max-w-7xl mx-auto px-6"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        <h1 className="text-3xl font-bold mb-8" style={{ color: 'rgb(226 232 240)' }}>
          New Research Job
        </h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Panel: Sources */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'rgb(226 232 240)' }}>
              Sources
            </h2>
            
            {/* Tabs */}
            <div className="flex space-x-2 mb-4">
              {(['url', 'pdf', 'text'] as const).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-4 py-2 rounded-xl font-medium transition-all duration-200 ${
                    activeTab === tab
                      ? 'bg-gradient-to-r from-primary to-accent text-white'
                      : 'text-muted hover:text-slate-200'
                  }`}
                  style={activeTab !== tab ? { backgroundColor: 'rgba(11, 16, 32, 0.5)' } : {}}
                >
                  {tab.toUpperCase()}
                </button>
              ))}
            </div>
            
            {/* Input */}
            <div className="flex space-x-2 mb-4">
              {activeTab === 'text' ? (
                <textarea
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  placeholder="Paste your text here..."
                  className="input flex-1 min-h-[120px] resize-none"
                  rows={5}
                />
              ) : (
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleAddSource()}
                  placeholder={
                    activeTab === 'url'
                      ? 'https://example.com/article'
                      : 'https://example.com/document.pdf'
                  }
                  className="input flex-1"
                />
              )}
              <motion.button
                onClick={handleAddSource}
                disabled={!currentInput.trim()}
                className="px-4 py-2 bg-gradient-to-r from-primary to-accent disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-medium transition-all duration-200"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                aria-label="Add source"
              >
                <Plus className="w-5 h-5" />
              </motion.button>
            </div>
            
            {/* Source List */}
            {sources.length > 0 && (
              <div className="space-y-2">
                {sources.map((source, idx) => (
                  <motion.div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl"
                    style={{ backgroundColor: 'rgba(11, 16, 32, 0.3)' }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                  >
                    <div className="flex-1 min-w-0">
                      <span className="text-xs text-muted uppercase mr-2">
                        {source.type}
                      </span>
                      <span className="text-sm" style={{ color: 'rgb(226 232 240)' }} style={{ color: 'rgb(226 232 240)' }}>
                        {source.value}
                      </span>
                    </div>
                    <button
                      onClick={() => handleRemoveSource(idx)}
                      className="p-1 rounded-lg transition-colors"
                      style={{ backgroundColor: 'transparent' }}
                      onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(11, 16, 32, 0.5)'}
                      onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                      aria-label="Remove source"
                    >
                      <X className="w-4 h-4 text-muted" />
                    </button>
                  </motion.div>
                ))}
              </div>
            )}
          </div>
          
          {/* Right Panel: Goal & Run */}
          <div className="card">
            <h2 className="text-xl font-semibold mb-4" style={{ color: 'rgb(226 232 240)' }}>
              Goal & Run
            </h2>
            
            {/* Goal Presets */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-muted mb-2">
                Quick Presets
              </label>
              <div className="flex flex-wrap gap-2">
                {GOAL_PRESETS.map((preset) => (
                  <button
                    key={preset}
                    onClick={() => handlePresetSelect(preset)}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-all duration-200 ${
                      selectedPreset === preset
                        ? 'bg-primary text-white'
                        : 'text-muted hover:text-slate-200'
                    }`}
                    style={selectedPreset !== preset ? { backgroundColor: 'rgba(11, 16, 32, 0.5)' } : {}}
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>
            
            {/* Goal Textarea */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-muted mb-2">
                Goal
              </label>
              <textarea
                value={goal}
                onChange={(e) => {
                  setGoal(e.target.value)
                  setSelectedPreset(null)
                }}
                placeholder="What do you want to learn from this content?"
                className="input min-h-[120px] resize-none"
                rows={5}
              />
            </div>
            
            {/* Optional Switches */}
            <div className="space-y-3 mb-6">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={autoFAQ}
                  onChange={(e) => setAutoFAQ(e.target.checked)}
                  className="w-4 h-4 text-primary rounded focus:ring-primary"
                />
                <span className="text-sm" style={{ color: 'rgb(226 232 240)' }}>
                  Auto-FAQ
                </span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={generateSlides}
                  onChange={(e) => setGenerateSlides(e.target.checked)}
                  className="w-4 h-4 text-primary rounded focus:ring-primary"
                />
                <span className="text-sm" style={{ color: 'rgb(226 232 240)' }}>
                  Generate slides
                </span>
              </label>
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={knowledgeGraph}
                  onChange={(e) => setKnowledgeGraph(e.target.checked)}
                  className="w-4 h-4 text-primary rounded focus:ring-primary"
                />
                <span className="text-sm" style={{ color: 'rgb(226 232 240)' }}>
                  Knowledge graph
                </span>
              </label>
            </div>
            
            {/* Submit Button */}
            <motion.button
              onClick={handleSubmit}
              disabled={!canSubmit || isSubmitting}
              className="w-full px-6 py-3 bg-gradient-to-r from-primary to-accent disabled:opacity-50 disabled:cursor-not-allowed rounded-xl text-white font-semibold transition-all duration-200 shadow-lg hover:shadow-xl"
              whileHover={canSubmit ? { scale: 1.02 } : {}}
              whileTap={canSubmit ? { scale: 0.98 } : {}}
            >
              {isSubmitting ? 'Creating...' : 'Run Pipeline'}
            </motion.button>
          </div>
        </div>
      </motion.div>
    </div>
  )
}
