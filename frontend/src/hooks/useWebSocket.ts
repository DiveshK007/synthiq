import { useEffect, useRef, useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE || 'http://localhost:8080'

interface UseWebSocketOptions {
  jobId: string | null
  enabled: boolean
  onMessage: (data: any) => void
  onError?: (error: Event) => void
}

export function useWebSocket({ jobId, enabled, onMessage, onError }: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  
  useEffect(() => {
    if (!enabled || !jobId) {
      if (wsRef.current) {
        wsRef.current.close()
        wsRef.current = null
        setIsConnected(false)
      }
      return
    }
    
    // Convert http to ws
    const wsUrl = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://')
    const ws = new WebSocket(`${wsUrl}/ws/jobs/${jobId}`)
    wsRef.current = ws
    
    ws.onopen = () => {
      setIsConnected(true)
      console.log('WebSocket connected')
    }
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) {
        onError(error)
      }
    }
    
    ws.onclose = () => {
      setIsConnected(false)
      console.log('WebSocket disconnected')
    }
    
    return () => {
      if (ws) {
        ws.close()
      }
    }
  }, [jobId, enabled, onMessage, onError])
  
  return { isConnected }
}

