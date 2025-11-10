import { useEffect, useRef } from 'react'

interface UsePollingOptions<T> {
  id: string
  intervalMs: number
  enabled: boolean
  onData: (data: T) => void
  fetchFn: () => Promise<T>
}

export function usePolling<T>({
  id,
  intervalMs,
  enabled,
  onData,
  fetchFn,
}: UsePollingOptions<T>) {
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const mountedRef = useRef(true)
  
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
    }
  }, [])
  
  useEffect(() => {
    if (!enabled || !id) {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
      return
    }
    
    const poll = async () => {
      if (!mountedRef.current) return
      
      try {
        const data = await fetchFn()
        if (mountedRef.current) {
          onData(data)
        }
      } catch (error) {
        console.error('Polling error:', error)
      }
    }
    
    // Initial fetch
    poll()
    
    // Set up interval
    intervalRef.current = setInterval(poll, intervalMs)
    
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
        intervalRef.current = null
      }
    }
  }, [id, intervalMs, enabled, onData, fetchFn])
}

