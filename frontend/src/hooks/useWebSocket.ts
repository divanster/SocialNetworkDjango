// frontend/src/hooks/useWebSocket.ts

import { useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface UseWebSocketProps {
  groupName: string;
  onMessage: (data: any) => void;
}

const useWebSocket = ({ groupName, onMessage }: UseWebSocketProps) => {
  const { token } = useAuth();
  const ws = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef<number>(0);
  const maxReconnectAttempts = 5;

  useEffect(() => {
    if (!token) {
      console.error('No token available for WebSocket connection.');
      return;
    }

    const connect = () => {
      // Ensure the WebSocket URL is correctly formatted
      const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';
      const normalizedBaseUrl = baseUrl.endsWith('/') ? baseUrl.slice(0, -1) : baseUrl;
      const websocketUrl = `${normalizedBaseUrl}/${groupName}/?token=${token}`;

      console.log(`Attempting to connect to WebSocket at ${websocketUrl}`);
      ws.current = new WebSocket(websocketUrl);

      ws.current.onopen = () => {
        console.log(`WebSocket connected to ${groupName}`);
        reconnectAttempts.current = 0; // Reset on successful connection
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log(`Message received from ${groupName}:`, data);
          onMessage(data); // Delegate message handling to the caller
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.current.onerror = (error) => {
        console.error(`WebSocket error for ${groupName}:`, error);
      };

      ws.current.onclose = (event) => {
        console.warn(`WebSocket connection closed for ${groupName}:`, event);
        if (reconnectAttempts.current < maxReconnectAttempts) {
          const timeout = Math.pow(2, reconnectAttempts.current) * 1000; // Exponential backoff
          console.log(`Reconnecting to ${groupName} in ${timeout / 1000} seconds...`);
          setTimeout(() => {
            reconnectAttempts.current += 1;
            connect();
          }, timeout);
        } else {
          console.error(`Max reconnection attempts reached for ${groupName}.`);
        }
      };
    };

    connect();

    // Cleanup function to close WebSocket when the component unmounts or dependencies change
    return () => {
      if (ws.current) {
        ws.current.close();
        console.log(`WebSocket connection closed for ${groupName}`);
      }
    };
  }, [groupName, token, onMessage]); // Dependencies include onMessage to handle dynamic callbacks

  return ws.current;
};

export default useWebSocket;
