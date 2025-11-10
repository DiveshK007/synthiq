import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useEffect } from 'react'
import Header from './components/Header'
import NewJob from './pages/NewJob'
import JobDetail from './pages/JobDetail'
import NotFound from './pages/NotFound'
import { useThemeStore } from './stores/theme'

function App() {
  const { theme } = useThemeStore()
  
  useEffect(() => {
    // Apply theme on mount
    if (theme === 'dark') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [theme])
  
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-ink dark:bg-ink text-slate-200 dark:text-slate-200">
        <Header />
        <Routes>
          <Route path="/" element={<NewJob />} />
          <Route path="/job/:id" element={<JobDetail />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'var(--ink)',
              color: 'var(--paper)',
              border: '1px solid var(--muted)',
            },
          }}
        />
      </div>
    </BrowserRouter>
  )
}

export default App
