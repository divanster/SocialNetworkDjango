// frontend/src/contexts/WebSocketManager.tsx

import React, { createContext, useContext, useRef } from 'react';
import { useAuth } from './AuthContext';

interface WebSocketContextType {
  getSocket: (url: string) => WebSocket | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const sockets = useRef<{ [key: string]: WebSocket }>({});

  const getSocket = (url: string): WebSocket | null => {
    if (!token) {
      console.error('No authentication token available.');
      return null;
    }

    const fullUrl = `${url}?token=${token}`;
    if (!sockets.current[fullUrl]) {
      const ws = new WebSocket(fullUrl);
      ws.onopen = () => console.log(`WebSocket connected to ${fullUrl}`);
      ws.onclose = () => {
        console.log(`WebSocket disconnected from ${fullUrl}`);
        delete sockets.current[fullUrl];
      };
      ws.onerror = (error) => console.error(`WebSocket error on ${fullUrl}`, error);
      sockets.current[fullUrl] = ws;
    }
    return sockets.current[fullUrl];
  };

  return (
    <WebSocketContext.Provider value={{ getSocket }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
