// frontend/src/hooks/useWebSocket.ts
import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

interface WebSocketHandler<T> {
  onOpen?: () => void;
  onMessage: (data: T) => void;
  onClose?: (ev: CloseEvent) => void;
  onError?: (err: Event) => void;
}

export interface UseWebSocketReturn {
  sendMessage: (msg: string) => void;
}

export default function useWebSocket<T>(
  groupName: string,
  handlers: WebSocketHandler<T>
): UseWebSocketReturn {
  const { token } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);
  const handlersRef = useRef(handlers);
  const isMounted = useRef(true);

  // keep the latest handlers in a ref
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const connect = useCallback(() => {
    if (!token || !groupName || !isMounted.current) return;

    const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000';
    const url = `${baseUrl}/${groupName}/?token=${token}`;
    console.log(`Attempting WebSocket connection to ${url}`);

    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`✅ WebSocket connected (${groupName})`);
      handlersRef.current.onOpen?.();
    };

    ws.onmessage = (evt) => {
      try {
        const data: T = JSON.parse(evt.data);
        handlersRef.current.onMessage(data);
      } catch (err) {
        console.error(`❌ Failed to parse message (${groupName}):`, err);
      }
    };

    ws.onerror = (err) => {
      console.error(`⚠️ WebSocket error (${groupName}):`, err);
      handlersRef.current.onError?.(err);
    };

    ws.onclose = (evt) => {
      console.warn(`🚧 WebSocket closed (${groupName})`, evt);
      handlersRef.current.onClose?.(evt);
      if (evt.code !== 1000 && isMounted.current) {
        reconnectTimer.current = window.setTimeout(connect, 5000);
      }
    };
  }, [token, groupName]);

  useEffect(() => {
    isMounted.current = true;
    connect();
    return () => {
      isMounted.current = false;
      socketRef.current?.close(1000, 'Component unmounted');
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  const sendMessage = useCallback(
    (msg: string) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(msg);
      } else {
        console.warn(`🚫 Cannot send message; WebSocket not open (${groupName})`);
      }
    },
    [groupName]
  );

  return { sendMessage };
}
