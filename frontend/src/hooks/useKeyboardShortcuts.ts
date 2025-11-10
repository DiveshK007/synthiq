import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

export function useKeyboardShortcuts() {
  const navigate = useNavigate()
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + N - New job
      if ((e.metaKey || e.ctrlKey) && e.key === 'n') {
        e.preventDefault()
        navigate('/')
      }
      
      // Cmd/Ctrl + K - Search (placeholder)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        // TODO: Open search modal
        console.log('Search (not implemented yet)')
      }
      
      // Esc - Close modals (if any)
      if (e.key === 'Escape') {
        // TODO: Close any open modals
        console.log('Escape pressed')
      }
      
      // Cmd/Ctrl + / - Show shortcuts help
      if ((e.metaKey || e.ctrlKey) && e.key === '/') {
        e.preventDefault()
        // TODO: Show shortcuts modal
        alert('Keyboard Shortcuts:\n\nCmd/Ctrl + N: New Job\nCmd/Ctrl + K: Search\nEsc: Close')
      }
    }
    
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [navigate])
}

