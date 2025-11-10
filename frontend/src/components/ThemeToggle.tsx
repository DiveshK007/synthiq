import { Moon, Sun } from 'lucide-react'
import { motion } from 'framer-motion'
import { useThemeStore } from '../stores/theme'

export default function ThemeToggle() {
  const { theme, toggle } = useThemeStore()
  
  return (
    <motion.button
      onClick={toggle}
      className="p-2 rounded-xl bg-[rgba(11,16,32,0.5)] dark:bg-[rgba(11,16,32,0.5)] hover:bg-[rgba(11,16,32,0.7)] dark:hover:bg-[rgba(11,16,32,0.7)] transition-colors duration-200"
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      {theme === 'dark' ? (
        <Sun className="w-5 h-5 text-muted" />
      ) : (
        <Moon className="w-5 h-5 text-muted" />
      )}
    </motion.button>
  )
}

