/**
 * Hook for monitoring task progress via WebSocket
 */
import { useEffect, useState, useRef } from 'react';

interface TaskProgressEvent {
  event: 'status' | 'progress' | 'completed' | 'failed' | 'error' | 'pong';
  task_id: string;
  status?: string;
  progress_percent?: number;
  current_step?: string;
  result?: any;
  error?: string;
  created_at?: string;
  started_at?: string;
  completed_at?: string;
}

interface TaskProgress {
  status: string;
  progressPercent: number;
  currentStep: string | null;
  result: any | null;
  error: string | null;
  isComplete: boolean;
  isFailed: boolean;
  events: TaskProgressEvent[];
}

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

/**
 * Hook to connect to task progress WebSocket and receive real-time updates
 */
export function useTaskProgress(taskId: string | null): TaskProgress & { connected: boolean } {
  const [progress, setProgress] = useState<TaskProgress>({
    status: 'pending',
    progressPercent: 0,
    currentStep: null,
    result: null,
    error: null,
    isComplete: false,
    isFailed: false,
    events: [],
  });
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!taskId) {
      return;
    }

    let isMounted = true;

    const connect = () => {
      if (!isMounted) return;

      const ws = new WebSocket(`${WS_BASE_URL}/ws/tasks/${taskId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log(`WebSocket connected for task ${taskId}`);
        setConnected(true);

        // Start ping interval to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send('ping');
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const data: TaskProgressEvent = JSON.parse(event.data);

          setProgress((prev) => {
            const newEvents = [...prev.events, data];

            return {
              ...prev,
              status: data.status || prev.status,
              progressPercent: data.progress_percent ?? prev.progressPercent,
              currentStep: data.current_step ?? prev.currentStep,
              result: data.result ?? prev.result,
              error: data.error ?? prev.error,
              isComplete: data.event === 'completed' || prev.isComplete,
              isFailed: data.event === 'failed' || prev.isFailed,
              events: newEvents,
            };
          });

          // Close connection if task is complete or failed
          if (data.event === 'completed' || data.event === 'failed') {
            ws.close();
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnected(false);
      };

      ws.onclose = () => {
        console.log(`WebSocket closed for task ${taskId}`);
        setConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Try to reconnect if not complete and component is still mounted
        if (isMounted && !progress.isComplete && !progress.isFailed) {
          reconnectTimeoutRef.current = setTimeout(() => {
            console.log('Attempting to reconnect...');
            connect();
          }, 5000);
        }
      };
    };

    connect();

    // Cleanup on unmount
    return () => {
      isMounted = false;

      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }

      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
    };
  }, [taskId]);

  return { ...progress, connected };
}
