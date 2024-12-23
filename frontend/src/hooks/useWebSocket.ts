// frontend/src/hooks/useWebSocket.ts

import { useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketHandler {
  onMessage: (data: any) => void;
}

export default function useWebSocket(
  groupName: string,
  { onMessage }: WebSocketHandler
): void {
  const { token, loading } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (loading) {
      // Authentication is still loading; do not attempt to connect yet
      return;
    }

    if (!token) {
      console.warn(`No token -> WebSocket connection for ${groupName} not established.`);
      return;
    }

    const connect = () => {
      const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';
      const normalizedBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
      const websocketUrl = `${normalizedBaseUrl}/${groupName}/?token=${token}`;

      console.log(`Connecting to WebSocket at: ${websocketUrl}`);
      socketRef.current = new WebSocket(websocketUrl);

      socketRef.current.onopen = () => {
        console.log(`WebSocket connected to group: ${groupName}`);
        reconnectAttemptsRef.current = 0;
      };

      socketRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error(`Error parsing WebSocket message for group ${groupName}:`, error);
        }
      };

      socketRef.current.onerror = (error) => {
        console.error(`WebSocket error for ${groupName}:`, error);
      };

      socketRef.current.onclose = (event) => {
        console.warn(`WebSocket connection closed for group: ${groupName}:`, event);
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const timeout = Math.pow(2, reconnectAttemptsRef.current) * 1000;
          console.log(`Reconnecting to ${groupName} in ${timeout / 1000} seconds...`);
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
}
