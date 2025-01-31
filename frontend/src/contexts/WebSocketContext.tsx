import React, { createContext, useContext, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './AuthContext';
import jwt_decode from 'jwt-decode';


interface WebSocketContextType {
  subscribe: (groupName: string) => void;
  unsubscribe: (groupName: string) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, refreshToken } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 10;
  const subscribedGroupsRef = useRef<Set<string>>(new Set());

  const connectWebSocket = useCallback(async () => {
    if (!token) {
      console.warn('No token provided for WebSocket connection.');
      return;
    }

    // Check if the token has expired and refresh it if necessary
    if (isTokenExpired(token)) {
      console.log('Token expired. Refreshing token...');
      const newToken = await refreshToken();
      if (!newToken) {
        console.error('Unable to refresh token');
        return;
      }
    }

    const wsUrl = `${process.env.REACT_APP_WEBSOCKET_URL}/?token=${token}`;
    console.log(`Connecting to WebSocket at: ${wsUrl}`);
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connection established.');
      reconnectAttemptsRef.current = 0;

      // Resubscribe to existing groups
      subscribedGroupsRef.current.forEach((group) => {
        ws.send(JSON.stringify({ action: 'subscribe', group }));
        console.log(`Resubscribed to group: ${group}`);
      });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.group && data.message) {
          // Dispatch a custom event based on the group name
          const eventName = `ws-${data.group}`;
          const customEvent = new CustomEvent(eventName, { detail: data.message });
          window.dispatchEvent(customEvent);
          console.log(`Received message for group ${data.group}:`, data.message);
        } else {
          console.warn('Received malformed message:', data);
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
      console.warn(`WebSocket connection closed:`, event);
      if (event.code !== 1000) {
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const timeout = Math.min(10000, Math.pow(2, reconnectAttemptsRef.current) * 1000); // Max 10 seconds
          console.log(`Reconnecting in ${timeout / 1000} seconds...`);
          setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connectWebSocket();
          }, timeout);
        } else {
          console.error('Max reconnection attempts reached. Giving up.');
        }
      }
    };
  }, [token, refreshToken]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        console.log('Closing WebSocket connection.');
        socketRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [token, connectWebSocket]);

  const subscribe = (groupName: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn(`WebSocket is not open. Cannot subscribe to group: ${groupName}`);
      return;
    }

    if (subscribedGroupsRef.current.has(groupName)) {
      console.warn(`Already subscribed to group: ${groupName}`);
      return;
    }

    socketRef.current.send(JSON.stringify({ action: 'subscribe', group: groupName }));
    subscribedGroupsRef.current.add(groupName);
    console.log(`Subscribed to group: ${groupName}`);
  };

  const unsubscribe = (groupName: string) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.warn(`WebSocket is not open. Cannot unsubscribe from group: ${groupName}`);
      return;
    }

    if (!subscribedGroupsRef.current.has(groupName)) {
      console.warn(`Not subscribed to group: ${groupName}`);
      return;
    }

    socketRef.current.send(JSON.stringify({ action: 'unsubscribe', group: groupName }));
    subscribedGroupsRef.current.delete(groupName);
    console.log(`Unsubscribed from group: ${groupName}`);
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


// Define the interface for the JWT payload
interface JwtPayload {
  exp: number;  // expiration time
  iat: number;  // issued at time
  sub: string;  // subject (optional)
  // Add other properties based on your JWT payload
}

function isTokenExpired(token: string): boolean {
  try {
    // Decode the token with the correct type
    const decoded = jwt_decode<JwtPayload>(token);

    const currentTime = Date.now() / 1000;  // in seconds
    return decoded.exp < currentTime;
  } catch (error) {
    console.error("Error decoding token:", error);
    return true;  // Return `true` if decoding fails, implying the token is invalid or expired.
  }
}
