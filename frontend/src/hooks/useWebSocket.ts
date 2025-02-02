// src/hooks/useWebSocket.ts

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
  const { token, loading } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 5;

  const sendMessage = useCallback((message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    } else {
      console.error('WebSocket is not open. Cannot send message.');
    }
  }, []);

  useEffect(() => {
    if (loading) return;        // Wait for auth to finish
    if (!token) {
      console.warn(`No token -> no WebSocket for group: ${groupName}`);
      return;
    }

    const connect = () => {
      // build final URL: e.g. "ws://localhost:8000/ws/posts/?token=<JWT>"
      const wsUrl = `${BASE_WS_URL}/${groupName}/?token=${token}`;
      console.log(`Connecting to WebSocket at: ${wsUrl}`);
      socketRef.current = new WebSocket(wsUrl);

      socketRef.current.onopen = () => {
        console.log(`WebSocket connected to group: ${groupName}`);
        reconnectAttemptsRef.current = 0;
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data: T = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error(`Error parsing WebSocket message for ${groupName}:`, error);
        }
      };

      socketRef.current.onerror = (error) => {
        console.error(`WebSocket error for group ${groupName}:`, error);
      };

      socketRef.current.onclose = (event) => {
        console.warn(`WebSocket closed for group: ${groupName} ->`, event);
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const timeout = Math.pow(2, reconnectAttemptsRef.current) * 1000; // exponential backoff
          console.log(`Reconnecting to ${groupName} in ${timeout / 1000}s...`);
          setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, timeout);
        } else {
          console.error(`Max reconnection attempts reached for ${groupName}.`);
        }
      };
    };

    connect();

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
        console.log(`WebSocket connection closed for group: ${groupName}`);
      }
    };
  }, [groupName, token, loading, onMessage]);

  return { sendMessage };
}
