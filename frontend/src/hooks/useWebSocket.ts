import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketHandler<T> {
  onMessage: (data: T) => void;
}

interface UseWebSocketReturn {
  sendMessage: (message: string) => void;
}

const BASE_WS_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';

export default function useWebSocket<T>(
  groupName: string,
  { onMessage }: WebSocketHandler<T>
): UseWebSocketReturn {
  const { token, loading, isAuthenticated } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 5;
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  // Stable message handler reference
  const messageHandlerRef = useRef(onMessage);
  messageHandlerRef.current = onMessage;

  const sendMessage = useCallback((message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    }
  }, []);

  const connect = useCallback(() => {
    if (loading || !token || !isAuthenticated) {
      console.warn(`No token provided – no WebSocket connection for group: ${groupName}`);
      return;
    }

    const wsUrl = new URL(`${BASE_WS_URL}/${groupName}/`);
    wsUrl.searchParams.set('token', token);

    console.log(`Connecting to WebSocket at: ${wsUrl.toString()}`);
    socketRef.current = new WebSocket(wsUrl.toString());

    socketRef.current.onopen = () => {
      console.log(`WebSocket connected to group: ${groupName}`);
      reconnectAttemptsRef.current = 0;
    };

    socketRef.current.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        messageHandlerRef.current(data);
      } catch (error) {
        console.error(`Error parsing message for ${groupName}:`, error);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error(`WebSocket error for ${groupName}:`, error);
    };

    socketRef.current.onclose = (event) => {
      console.warn(`WebSocket closed for ${groupName}:`, event);
      if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
        const timeout = Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
        console.log(`Reconnecting to ${groupName} in ${timeout/1000}s...`);

        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, timeout);
      }
    };
  }, [groupName, token, loading, isAuthenticated]);

  useEffect(() => {
    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
        socketRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect, token, loading, isAuthenticated]);

  return { sendMessage };
}
