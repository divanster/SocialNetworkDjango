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

const BASE_WS_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { token } = useAuth();
  const socketsRef = useRef<{ [groupName: string]: WebSocket }>({});
  const reconnectAttemptsRef = useRef<{ [groupName: string]: number }>({});
  const maxReconnectAttempts = 5;

  const createWebSocket = useCallback(
    (groupName: string, onMessage: ((this: WebSocket, ev: MessageEvent<any>) => any) | null) => {
      if (!token) {
        console.error(`No token -> cannot create WebSocket for group: ${groupName}`);
        return;
      }
      const websocketUrl = `${BASE_WS_URL}/${groupName}/?token=${token}`;
      console.log(`Connecting to WebSocket at ${websocketUrl}`);

      const socket = new WebSocket(websocketUrl);
      socketsRef.current[groupName] = socket;
      reconnectAttemptsRef.current[groupName] = reconnectAttemptsRef.current[groupName] || 0;

      socket.onopen = () => {
        console.log(`WebSocket connected to group: ${groupName}`);
        reconnectAttemptsRef.current[groupName] = 0; // reset attempts
      };

      if (onMessage) {
        socket.onmessage = onMessage;
      }

      socket.onerror = (error) => {
        console.error(`WebSocket error for group ${groupName}:`, error);
      };

      socket.onclose = (event) => {
        console.warn(`WebSocket closed for group: ${groupName}:`, event);
        delete socketsRef.current[groupName];
        if (reconnectAttemptsRef.current[groupName] < maxReconnectAttempts) {
          const backoff = Math.pow(2, reconnectAttemptsRef.current[groupName]) * 1000;
          console.log(`Reconnecting to ${groupName} in ${backoff / 1000}s...`);
          setTimeout(() => {
            reconnectAttemptsRef.current[groupName] += 1;
            createWebSocket(groupName, onMessage);
          }, backoff);
        } else {
          console.error(`Max reconnection attempts for ${groupName}`);
        }
      };
    },
    [token]
  );

  const getSocket = useCallback(
    (groupName: string, onMessage: (data: any) => void): WebSocket => {
      if (!socketsRef.current[groupName]) {
        createWebSocket(groupName, (event: MessageEvent<any>) => {
          try {
            const data = JSON.parse(event.data);
            onMessage(data);
          } catch (err) {
            console.error(`Error parsing WS message for group ${groupName}:`, err);
          }
        });
      }
      return socketsRef.current[groupName];
    },
    [createWebSocket]
  );

  const sendMessage = useCallback((groupName: string, message: string) => {
    const socket = socketsRef.current[groupName];
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(message);
    } else {
      console.error(`WebSocket for group ${groupName} is not open. Cannot send message.`);
    }
  }, []);

  useEffect(() => {
    return () => {
      Object.entries(socketsRef.current).forEach(([groupName, socket]) => {
        socket.close(1000, 'Unmounted');
        console.log(`Closed WS for group: ${groupName}`);
      });
    };
  }, []);

  return (
    <WebSocketManagerContext.Provider value={{ getSocket, sendMessage }}>
      {children}
    </WebSocketManagerContext.Provider>
  );
};

export const useWebSocketManager = (): WebSocketManagerContextType => {
  const ctx = useContext(WebSocketManagerContext);
  if (!ctx) {
    throw new Error('useWebSocketManager must be used within a WebSocketProvider');
  }
  return ctx;
};
