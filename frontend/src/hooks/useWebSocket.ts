// frontend/src/hooks/useWebSocket.ts

import { useEffect, useRef } from 'react';
import { useAuth } from '../contexts/AuthContext';

const useWebSocket = (groupName: string) => {
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
      const websocketUrl = `${process.env.REACT_APP_WEBSOCKET_URL}${groupName}/?token=${token}`;
      console.log(`Attempting to connect to WebSocket at ${websocketUrl}`);
      ws.current = new WebSocket(websocketUrl);

      ws.current.onopen = () => {
        console.log(`WebSocket connected to ${groupName}`);
        reconnectAttempts.current = 0; // Reset on successful connection
      };

      ws.current.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log(`Message received from ${groupName}:`, data);
        // Handle incoming messages
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

    return () => {
      if (ws.current) {
        ws.current.close();
        console.log(`WebSocket connection closed for ${groupName}`);
      }
    };
  }, [groupName, token]);

  return ws.current;
};

export default useWebSocket;
