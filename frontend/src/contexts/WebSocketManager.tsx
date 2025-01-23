// frontend/src/contexts/WebSocketManager.tsx

import React, { createContext, useContext, useRef, useEffect, ReactNode, useCallback } from 'react';
import { useAuth } from './AuthContext';

interface WebSocketManagerContextType {
  getSocket: (groupName: string, onMessage: (data: any) => void) => WebSocket;
  sendMessage: (groupName: string, message: string) => void;
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

  // Callback to handle WebSocket reconnection
  const handleReconnection = useCallback(
    (groupName: string) => {
      if (reconnectAttempts.current[groupName] < maxReconnectAttempts) {
        const timeout = Math.pow(2, reconnectAttempts.current[groupName]) * 1000; // Exponential backoff
        console.log(`Reconnecting to ${groupName} in ${timeout / 1000} seconds...`);
        setTimeout(() => {
          reconnectAttempts.current[groupName] += 1;
          createWebSocket(groupName, sockets.current[groupName]?.onmessage);
        }, timeout);
      } else {
        console.error(`Max reconnection attempts reached for ${groupName}.`);
      }
    },
    [maxReconnectAttempts]
  );

  // Function to create a new WebSocket connection
  const createWebSocket = useCallback(
    (groupName: string, onMessage: ((this: WebSocket, ev: MessageEvent<any>) => any) | null) => {
      if (!token) {
        console.error('No authentication token provided for WebSocket connection.');
        throw new Error('Authentication token is required.');
      }

      const websocketUrl = `${WEBSOCKET_URL}${groupName}/?token=${token}`;
      console.log(`Connecting to WebSocket at ${websocketUrl}`);
      const socket = new WebSocket(websocketUrl);
      sockets.current[groupName] = socket;
      reconnectAttempts.current[groupName] = reconnectAttempts.current[groupName] || 0;

      socket.onopen = () => {
        console.log(`WebSocket connected to group: ${groupName}`);
        reconnectAttempts.current[groupName] = 0; // Reset reconnection attempts on successful connection
      };

      if (onMessage) {
        socket.onmessage = onMessage;
      }

      socket.onerror = (error) => {
        console.error(`WebSocket error for group ${groupName}:`, error);
      };

      socket.onclose = (event) => {
        console.warn(`WebSocket connection closed for group: ${groupName}:`, event);
        delete sockets.current[groupName];
        handleReconnection(groupName);
      };
    },
    [WEBSOCKET_URL, token, handleReconnection]
  );

  // Public method to get or create a WebSocket connection
  const getSocket = useCallback(
    (groupName: string, onMessage: (data: any) => void): WebSocket => {
      if (!groupName) {
        console.error('WebSocket group name is undefined.');
        throw new Error('WebSocket group name is required.');
      }

      if (!sockets.current[groupName]) {
        createWebSocket(groupName, (event: MessageEvent<any>) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (error) {
            console.error(`Error parsing WebSocket message for group ${groupName}:`, error);
          }
        });
      }

      return sockets.current[groupName];
    },
    [createWebSocket]
  );

  // Public method to send a message via a specific WebSocket
  const sendMessage = useCallback((groupName: string, message: string) => {
    const socket = sockets.current[groupName];
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    } else {
      console.error(`WebSocket for group ${groupName} is not open. Cannot send message.`);
    }
  }, []);

  // Cleanup all WebSocket connections on unmount
  useEffect(() => {
    return () => {
      Object.entries(sockets.current).forEach(([groupName, socket]) => {
        socket.close(1000, 'Component unmounted');
        console.log(`WebSocket connection closed for group: ${groupName}`);
      });
      sockets.current = {};
    };
  }, []);

  return (
    <WebSocketManagerContext.Provider value={{ getSocket, sendMessage }}>
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

// Hook to simplify WebSocket usage in components
export const useWebSocket = (groupName: string, onMessage: (data: any) => void): WebSocket => {
  const { getSocket } = useWebSocketManager();
  const socket = getSocket(groupName, onMessage);
  return socket;
};
