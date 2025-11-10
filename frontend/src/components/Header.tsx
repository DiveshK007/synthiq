import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Plus, History } from 'lucide-react'
import ThemeToggle from './ThemeToggle'

export default function Header() {
  const navigate = useNavigate()
  
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-[rgba(11,16,32,0.8)] dark:bg-[rgba(11,16,32,0.8)] backdrop-blur-md border-b border-[rgba(11,16,32,0.2)] dark:border-[rgba(11,16,32,0.2)] shadow-lg">
      <div className="container mx-auto px-6 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-3">
            <motion.div
              className="p-2 bg-gradient-to-br from-primary to-accent rounded-xl"
              whileHover={{ scale: 1.05, rotate: 5 }}
              whileTap={{ scale: 0.95 }}
            >
              <Brain className="w-6 h-6 text-white" />
            </motion.div>
            <span className="text-xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              SynthIQ
            </span>
          </Link>
          
          <div className="flex items-center space-x-4">
            <motion.button
              onClick={() => navigate('/jobs')}
              className="flex items-center space-x-2 px-4 py-2 bg-[rgba(11,16,32,0.5)] hover:bg-[rgba(11,16,32,0.7)] rounded-xl text-slate-200 font-medium transition-all duration-200"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              aria-label="View job history"
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </motion.button>
            <ThemeToggle />
            <motion.button
              onClick={() => navigate('/')}
              className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-primary to-accent hover:from-primary-900 hover:to-accent rounded-xl text-white font-medium transition-all duration-200 shadow-md hover:shadow-lg"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              aria-label="Create new job"
            >
              <Plus className="w-4 h-4" />
              <span>New Job</span>
            </motion.button>
          </div>
        </div>
      </div>
    </header>
  )
}
