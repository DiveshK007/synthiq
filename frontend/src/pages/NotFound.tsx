import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="pt-24 pb-12 min-h-screen flex items-center justify-center">
      <motion.div
        className="text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-6xl font-bold mb-4 text-slate-200 dark:text-slate-200">404</h1>
        <p className="text-xl text-muted mb-8">Page not found</p>
        <Link
          to="/"
          className="inline-flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-primary to-accent rounded-xl text-white font-medium transition-all duration-200"
        >
          <Home className="w-5 h-5" />
          <span>Go Home</span>
        </Link>
      </motion.div>
    </div>
  )
}

