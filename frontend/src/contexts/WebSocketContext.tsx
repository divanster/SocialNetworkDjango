// src/contexts/WebSocketContext.tsx
import React, { createContext, useContext, useEffect, useRef, useCallback, ReactNode } from 'react';
import { useAuth } from './AuthContext';
import jwt_decode from 'jwt-decode';

interface JwtPayload {
  exp: number;
  iat: number;
  sub: string;
}

export interface WebSocketContextType {
  subscribe: (groupName: string) => void;
  unsubscribe: (groupName: string) => void;
  sendMessage: (message: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

const isTokenExpired = (token: string): boolean => {
  try {
    const decoded = jwt_decode<JwtPayload>(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error('Error decoding token:', error);
    return true;
  }
};

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { token, refreshToken } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 10;
  const subscribedGroupsRef = useRef<Set<string>>(new Set());
  const queuedActions = useRef<Array<() => void>>([]);
  const HEARTBEAT_INTERVAL = 30000;

  const connectWebSocket = useCallback(async () => {
    if (!token) {
      console.warn('No token provided for WebSocket connection.');
      return;
    }
    let currentToken = token;
    if (isTokenExpired(token)) {
      const newToken = await refreshToken();
      if (!newToken) {
        console.error('Unable to refresh token');
        return;
      }
      currentToken = newToken;
    }
    // Change default endpoint as needed; here we use "/ws/users" so subscriptions work.
    const wsUrl = `${process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws/users'}/?token=${currentToken}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    const heartbeatInterval = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, HEARTBEAT_INTERVAL);

    ws.onopen = () => {
      reconnectAttemptsRef.current = 0;
      queuedActions.current.forEach(action => action());
      queuedActions.current = [];
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.group && data.message) {
          const eventName = `ws-${data.group}`;
          const customEvent = new CustomEvent(eventName, { detail: data.message });
          window.dispatchEvent(customEvent);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      ws.close();
      console.error('WebSocket encountered error:', error);
    };

    ws.onclose = (event) => {
      clearInterval(heartbeatInterval);
      if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
        setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connectWebSocket();
        }, Math.min(10000, Math.pow(2, reconnectAttemptsRef.current) * 1000));
      }
    };
  }, [token, refreshToken]);

  useEffect(() => {
    connectWebSocket();
    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [token, connectWebSocket]);

  const subscribe = (groupName: string) => {
    if (subscribedGroupsRef.current.has(groupName)) return;
    const performSubscribe = () => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ action: 'subscribe', group: groupName }));
        subscribedGroupsRef.current.add(groupName);
      } else {
        queuedActions.current.push(() => {
          socketRef.current?.send(JSON.stringify({ action: 'subscribe', group: groupName }));
          subscribedGroupsRef.current.add(groupName);
        });
      }
    };
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      performSubscribe();
    } else {
      queuedActions.current.push(performSubscribe);
    }
  };

  const unsubscribe = (groupName: string) => {
    if (!subscribedGroupsRef.current.has(groupName)) return;
    const performUnsubscribe = () => {
      socketRef.current?.send(JSON.stringify({ action: 'unsubscribe', group: groupName }));
      subscribedGroupsRef.current.delete(groupName);
    };
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      performUnsubscribe();
    } else {
      queuedActions.current.push(performUnsubscribe);
    }
  };

  const sendMessage = (message: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    } else {
      console.warn('WebSocket is not open; message not sent.');
    }
  };

  return (
    <WebSocketContext.Provider value={{ subscribe, unsubscribe, sendMessage }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
};
