// WebSocketContext.tsx

import React, { createContext, useEffect, useRef } from 'react';
import { useAuth } from './AuthContext'; // Adjust the path if necessary

interface WebSocketContextType {
  // Define any context values you need
}

export const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (socketRef.current) {
      console.log('Closing existing WebSocket connection.');
      socketRef.current.close();
    }

    if (token) {
      console.log('Connecting to WebSocket with token:', token);
      const wsUrl = `ws://localhost:8000/ws/your_endpoint/?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        console.log('WebSocket connected');
      };

      ws.onmessage = (event) => {
        console.log('Received:', event.data);
      };

      ws.onclose = (event) => {
        console.log('WebSocket connection closed', event);
        // Handle reconnection logic if necessary
      };

      ws.onerror = (error) => {
        console.error('WebSocket error', error);
      };

      socketRef.current = ws;
    }

    return () => {
      if (socketRef.current) {
        console.log('Cleaning up WebSocket connection.');
        socketRef.current.close();
      }
    };
  }, [token]); // Reconnect when the token changes

  return (
    <WebSocketContext.Provider value={{ /* Provide any context values */ }}>
      {children}
    </WebSocketContext.Provider>
  );
};
