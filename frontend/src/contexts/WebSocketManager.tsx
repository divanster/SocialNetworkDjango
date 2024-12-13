// frontend/src/contexts/WebSocketManager.tsx

import React, { createContext, useContext, useRef, useEffect, ReactNode } from 'react';
import { useAuth } from './AuthContext';

interface WebSocketManagerContextType {
  getSocket: (groupName: string) => WebSocket;
}

const WebSocketManagerContext = createContext<WebSocketManagerContextType | undefined>(undefined);

interface WebSocketProviderProps {
  children: ReactNode;
}

const WEBSOCKET_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws/';

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { token } = useAuth();
  const sockets = useRef<{ [groupName: string]: WebSocket }>({});
  const reconnectAttempts = useRef<{ [groupName: string]: number }>({});
  const maxReconnectAttempts = 5;

  const getSocket = (groupName: string): WebSocket => {
    if (!groupName) {
      console.error('WebSocket group name is undefined.');
      throw new Error('WebSocket group name is required.');
    }

    if (!sockets.current[groupName]) {
      if (!token) {
        console.error('No authentication token provided for WebSocket connection.');
        throw new Error('Authentication token is required.');
      }

      const websocketUrl = `${WEBSOCKET_URL}${groupName}/?token=${token}`;
      console.log(`Connecting to WebSocket at ${websocketUrl}`);
      const socket = new WebSocket(websocketUrl);
      sockets.current[groupName] = socket;
      reconnectAttempts.current[groupName] = 0;

      socket.onopen = () => {
        console.log(`WebSocket connected to ${groupName}`);
        reconnectAttempts.current[groupName] = 0;
      };

      socket.onerror = (error) => {
        console.error(`WebSocket error for ${groupName}:`, error);
      };

      socket.onclose = (event) => {
        console.warn(`WebSocket connection closed for ${groupName}:`, event);
        delete sockets.current[groupName];

        if (!event.wasClean && reconnectAttempts.current[groupName] < maxReconnectAttempts) {
          const timeout = Math.pow(2, reconnectAttempts.current[groupName]) * 1000; // Exponential backoff
          console.log(`Reconnecting to ${groupName} in ${timeout / 1000} seconds...`);
          setTimeout(() => {
            reconnectAttempts.current[groupName] += 1;
            getSocket(groupName);
          }, timeout);
        } else {
          console.error(`Max reconnection attempts reached for ${groupName}.`);
        }
      };
    }

    return sockets.current[groupName];
  };

  useEffect(() => {
    const currentSockets = { ...sockets.current };

    return () => {
      Object.values(currentSockets).forEach((socket) => {
        socket.close();
      });
      console.log('All WebSocket connections closed.');
    };
  }, []);

  return (
    <WebSocketManagerContext.Provider value={{ getSocket }}>
      {children}
    </WebSocketManagerContext.Provider>
  );
};

export const useWebSocketManager = (): WebSocketManagerContextType => {
  const context = useContext(WebSocketManagerContext);
  if (!context) {
    throw new Error('useWebSocketManager must be used within a WebSocketProvider');
  }
  return context;
};

export const useWebSocket = (groupName: string): WebSocket => {
  const { getSocket } = useWebSocketManager();
  return getSocket(groupName); // Pass groupName here
};
