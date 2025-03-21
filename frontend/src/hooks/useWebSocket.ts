import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import jwt_decode from 'jwt-decode';

function isTokenExpired(token: string): boolean {
  try {
    const decoded: any = jwt_decode(token);
    const currentTime = Date.now() / 1000; // current time in seconds
    return decoded.exp < currentTime;
  } catch (error) {
    console.error("Error decoding token:", error);
    return true; // assume expired if decoding fails
  }
}

interface WebSocketHandler<T> {
  onMessage: (data: T) => void;
}

interface UseWebSocketReturn {
  sendMessage: (message: string) => void;
}

const BASE_WS_URL = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';

export default function useWebSocket<T>(
  groupName: string,
  { onMessage }: WebSocketHandler<T>
): UseWebSocketReturn {
  const { token, loading, isAuthenticated } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectAttemptsRef = useRef<number>(0);
  const maxReconnectAttempts = 5;
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
  const isConnecting = useRef(false);

  // Stable message handler reference
  const messageHandlerRef = useRef(onMessage);
  messageHandlerRef.current = onMessage;

  const sendMessage = useCallback((message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    } else {
      console.warn('WebSocket not open, message not sent.');
    }
  }, []);

  const reconnect = useCallback(() => {
    if (reconnectAttemptsRef.current < maxReconnectAttempts) {
      reconnectAttemptsRef.current += 1;
      console.log(`Reconnecting attempt ${reconnectAttemptsRef.current}`);
      connect(); // Try to reconnect
    } else {
      console.error('Max reconnect attempts reached, WebSocket not connected.');
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    // Prevent repeated calls
    if (loading || isConnecting.current) return;

    // No token or user is not authenticated => skip
    if (!token || !isAuthenticated) {
      console.warn('No valid token or not authenticated; skipping WebSocket connect.');
      return;
    }

    // If token is expired, skip connecting. AuthContext should handle refreshing.
    if (isTokenExpired(token)) {
      console.warn('Token is expired; skipping WebSocket connect.');
      return;
    }

    isConnecting.current = true;

    // Clear any previous reconnection attempt
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }

    // Cleanup previous connection
    if (socketRef.current) {
      if (socketRef.current.readyState === WebSocket.OPEN) {
        socketRef.current.close(1000, 'Reconnection initiated');
      }
      socketRef.current = null;
    }

    const wsUrl = new URL(`${BASE_WS_URL}/${groupName}/`);
    wsUrl.searchParams.set('token', token);

    console.log(`Attempting connection to ${wsUrl}`);
    socketRef.current = new WebSocket(wsUrl.toString());

    // Setup heartbeat mechanism
    heartbeatIntervalRef.current = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000);

    socketRef.current.onopen = () => {
      console.log(`Connected to ${groupName}`);
      reconnectAttemptsRef.current = 0;
      isConnecting.current = false;

      // Once connected, we stop the heartbeat setup.
      // (Alternatively, you might want to keep it running at intervals,
      // but let’s clear it here and re-set if needed.)
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
    };

    socketRef.current.onclose = (event: CloseEvent) => {
      console.error('WebSocket closed:', event);
      isConnecting.current = false;

      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }

      if (event.code !== 1000) {
        const delay = Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
        console.log(`Reconnecting in ${delay / 1000} seconds...`);
        reconnectTimeoutRef.current = setTimeout(reconnect, delay);
      }
    };

    socketRef.current.onerror = (error: Event) => {
      console.error(`WebSocket error for ${groupName}:`, error);
      // Attempt reconnection for any error
      // But first close the socket to avoid half-open
      socketRef.current?.close();
    };

    socketRef.current.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        messageHandlerRef.current(data);
      } catch (err) {
        console.error(`Error parsing message for ${groupName}:`, err);
      }
    };
  }, [groupName, token, isAuthenticated, loading, reconnect]);

  useEffect(() => {
    if (!loading && token && isAuthenticated) {
      connect();
    }
    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
        socketRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      isConnecting.current = false;
    };
  }, [connect, token, loading, isAuthenticated]);

  return { sendMessage };
}
