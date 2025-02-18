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
  const heartbeatIntervalRef = useRef<NodeJS.Timeout>();
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

    // Add heartbeat mechanism
    heartbeatIntervalRef.current = setInterval(() => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(JSON.stringify({ type: 'heartbeat' }));
      }
    }, 30000); // Send heartbeat every 30 seconds

    socketRef.current.onopen = () => {
      console.log(`Connected to ${groupName}`);
      reconnectAttemptsRef.current = 0;
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current); // Stop heartbeat on successful connection
      }
    };

    socketRef.current.onclose = (event: CloseEvent) => {
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current); // Clear heartbeat on close
      }

      if (event.code !== 1000) {  // Only reconnect for abnormal closures
        const delay = Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      }
    };

    socketRef.current.onerror = (error: Event) => {
      console.error(`WebSocket error for ${groupName}:`, error);
      reconnect(); // Attempt reconnection for any error
    };

    socketRef.current.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        messageHandlerRef.current(data);
      } catch (error) {
        console.error(`Error parsing message for ${groupName}:`, error);
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
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current); // Clear heartbeat on cleanup
      }
      isConnecting.current = false;
    };
  }, [connect, token, loading, isAuthenticated]);

  return { sendMessage };
}
