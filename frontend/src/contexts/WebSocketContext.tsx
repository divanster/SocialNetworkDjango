import React, { createContext, useContext, useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from './AuthContext';
import jwt_decode from 'jwt-decode';

interface JwtPayload {
  exp: number;
  iat: number;
  sub: string;
}

interface WebSocketContextType {
  subscribe: (groupName: string) => void;
  unsubscribe: (groupName: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

function isTokenExpired(token: string): boolean {
  try {
    const decoded = jwt_decode<JwtPayload>(token);
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  } catch (error) {
    console.error("Error decoding token:", error);
    return true;
  }
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, refreshToken } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 10;
  const subscribedGroupsRef = useRef<Set<string>>(new Set());
  const HEARTBEAT_INTERVAL = 30000;
  const queuedActions = useRef<Array<() => void>>([]);

  const connectWebSocket = useCallback(async () => {
    if (!token) {
      console.warn('No token provided for WebSocket connection.');
      return;
    }

    let currentToken = token;
    if (isTokenExpired(token)) {
      console.log('Token expired. Refreshing token...');
      const newToken = await refreshToken();
      if (!newToken) {
        console.error('Unable to refresh token');
        return;
      }
      currentToken = newToken;
    }

    const baseWsUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws/users';
    const wsUrl = `${baseWsUrl}/?token=${currentToken}`;
    console.log(`Connecting to WebSocket at: ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    const heartbeatInterval = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ action: 'ping' }));
      }
    }, HEARTBEAT_INTERVAL);

    ws.onopen = () => {
      console.log('WebSocket connection established.');
      reconnectAttemptsRef.current = 0;

      queuedActions.current.forEach(action => action());
      queuedActions.current = [];
    };

    ws.onmessage = (event) => {
      try {
        console.log("Received WebSocket message:", event.data);
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
      console.error('WebSocket encountered error:', error);
      ws.close();
    };

    ws.onclose = (event) => {
      clearInterval(heartbeatInterval);
      console.warn('WebSocket connection closed:', event);

      if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
        const timeout = Math.min(10000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
        console.log(`Reconnecting in ${timeout / 1000} seconds...`);
        setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connectWebSocket();
        }, timeout);
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
        console.log(`Subscribed to group: ${groupName}`);
      } else {
        queuedActions.current.push(() => {
          socketRef.current?.send(JSON.stringify({ action: 'subscribe', group: groupName }));
          subscribedGroupsRef.current.add(groupName);
          console.log(`Subscribed to group: ${groupName}`);
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
      console.log(`Unsubscribed from group: ${groupName}`);
    };

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      performUnsubscribe();
    } else {
      queuedActions.current.push(performUnsubscribe);
    }
  };

  return (
    <WebSocketContext.Provider value={{ subscribe, unsubscribe }}>
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
