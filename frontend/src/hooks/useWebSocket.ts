import { useEffect, useRef } from 'react';
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

  useEffect(() => {
    if (!token || !groupName) return;

    const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000';
    const wsUrl = `${baseUrl}/ws/${groupName}/?token=${token}`;
    console.log(`Attempting WebSocket: ${wsUrl}`);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log(`WebSocket connected -> ${groupName}`);
    };

    socket.onmessage = (event) => {
      try {
        const data: T = JSON.parse(event.data);
        onMessage(data);
      } catch (err) {
        console.error(`Failed to parse WS message for ${groupName}:`, err);
      }
    };

    socket.onerror = (err) => {
      console.error(`WebSocket error for ${groupName}:`, err);
    };

    socket.onclose = (ev) => {
      console.warn(`WebSocket closed -> ${groupName}`, ev);
    };

    return () => {
      socket.close(1000, 'Component unmounted');
    };
  }, [token, groupName, onMessage]);

  const sendMessage = (msg: string) => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(msg);
    } else {
      console.warn(`Cannot send
       message; socket not open -> ${groupName}`);
    }
  };

  return { sendMessage };
}
