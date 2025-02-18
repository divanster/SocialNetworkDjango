import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

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
  const isConnecting = useRef(false); // Prevent redundant connections

  // Stable message handler reference
  const messageHandlerRef = useRef(onMessage);
  messageHandlerRef.current = onMessage;

  // Send messages through WebSocket
  const sendMessage = useCallback((message: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(message);
    }
  }, []);

  // Connect to WebSocket
  const connect = useCallback(() => {
    if (loading || !token || !isAuthenticated || isConnecting.current) return;

    // Cleanup previous connection if exists
    if (socketRef.current) {
      socketRef.current.close(1000, 'Reconnecting');
      socketRef.current = null;
    }
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }

    isConnecting.current = true;

    const wsUrl = new URL(`${BASE_WS_URL}/${groupName}/`);
    wsUrl.searchParams.set('token', token);

    console.log(`Connecting to WebSocket at: ${wsUrl.toString()}`);
    socketRef.current = new WebSocket(wsUrl.toString());

    socketRef.current.onopen = () => {
      console.log(`WebSocket connected to group: ${groupName}`);
      reconnectAttemptsRef.current = 0;
      isConnecting.current = false;
    };

    socketRef.current.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        messageHandlerRef.current(data);
      } catch (error) {
        console.error(`Error parsing message for ${groupName}:`, error);
      }
    };

    socketRef.current.onerror = (error: Event) => {
      console.error(`WebSocket error for ${groupName}:`, error);

      // Check for ECONNREFUSED error
      if ((error as ErrorEvent).message && (error as ErrorEvent).message.includes('ECONNREFUSED')) {
        console.error("Connection refused. Attempting to reconnect...");
        reconnect();
      } else {
        console.error("Unknown WebSocket error.");
        reconnect();
      }
    };

    socketRef.current.onclose = (event: CloseEvent) => {
      console.warn(`WebSocket closed for ${groupName}:`, event);
      if (event.code === 1006) {
        console.warn("WebSocket closed with error code 1006. Attempting reconnect...");
        reconnect();
      }

      // Attempt reconnection logic for any non-clean closures
      if (event.code !== 1000 && reconnectAttemptsRef.current < maxReconnectAttempts) {
        const timeout = Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, timeout);
      }
    };
  }, [groupName, token, loading, isAuthenticated]);

  // Reconnection logic
  const reconnect = () => {
    if (reconnectAttemptsRef.current < maxReconnectAttempts) {
      connect();
    } else {
      console.error('Max reconnect attempts reached, WebSocket not connected.');
    }
  };

  // Trigger connection once loading is false and token is available
  useEffect(() => {
    if (!loading && token && isAuthenticated) {
      connect();
    }

    // Cleanup on component unmount
    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
        socketRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      isConnecting.current = false;
    };
  }, [connect, token, loading, isAuthenticated]);

  return { sendMessage };
}
