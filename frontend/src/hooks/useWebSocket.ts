// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketHandler<T> {
  onMessage: (data: T) => void;
}

export interface UseWebSocketReturn {
  sendMessage: (msg: string) => void;
}

export default function useWebSocket<T>(
  groupName: string,
  { onMessage }: WebSocketHandler<T>
): UseWebSocketReturn {
  const { token } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = useCallback(() => {
    if (!token || !groupName) return;

    const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000/ws';
    const wsUrl = `${baseUrl}/${groupName}/?token=${token}`;
    console.log(`Attempting WebSocket connection to ${wsUrl}`);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log(`✅ WebSocket connected (${groupName})`);
    };

    socket.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error(`❌ Failed to parse message (${groupName}):`, err);
      }
    };

    socket.onerror = (error) => {
      console.error(`⚠️ WebSocket error (${groupName}):`, error);
    };

    socket.onclose = (event) => {
      console.warn(`🚧 WebSocket closed (${groupName})`, event);
      if (event.code !== 1000) {
        reconnectTimer.current = setTimeout(connectWebSocket, 5000);
      }
    };
  }, [token, groupName, onMessage]);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Component unmounted');
        socketRef.current = null;
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };
  }, [connectWebSocket]);

  const sendMessage = useCallback((msg: string) => {
    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(msg);
    } else {
      console.warn(`🚫 Cannot send message; WebSocket not open (${groupName})`);
    }
  }, [groupName]);

  return { sendMessage };
}
