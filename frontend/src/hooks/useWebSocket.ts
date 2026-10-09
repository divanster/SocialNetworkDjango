import { useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';

export interface WebSocketHandler<T> {
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
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;

  // always keep handlersRef up to date
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const connect = useCallback(() => {
    if (!token || !groupName || !isMounted.current) return;
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) return;

    const rawBase = process.env.REACT_APP_WEBSOCKET_URL;
    if (!rawBase) {
      return;
    }
    const cleanBase = rawBase.replace(/\/ws\/?$/, "");
    const url = `${cleanBase}/ws/${groupName}/?token=${token}`;
    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onopen = () => {
      reconnectAttempts.current = 0;
      handlersRef.current.onOpen?.();
    };
    ws.onmessage = (evt) => {
      if (evt.data === 'ping' || evt.data === 'pong') {
        return;
      }
      try {
        handlersRef.current.onMessage(JSON.parse(evt.data));
      } catch {
        // Ignore non-JSON payloads to avoid crashing realtime handlers.
      }
    };
    ws.onerror = (err) => {
      handlersRef.current.onError?.(err);
    };
    ws.onclose = (ev) => {
      handlersRef.current.onClose?.(ev);
      socketRef.current = null;
      if (!token) return;
      if (ev.code !== 1000 && isMounted.current) {
        if (reconnectAttempts.current >= MAX_RECONNECT_ATTEMPTS) {
          return;
        }
        reconnectAttempts.current += 1;
        const delayMs = Math.min(30000, 1000 * Math.pow(2, reconnectAttempts.current - 1));
        reconnectTimer.current = window.setTimeout(connect, delayMs);
      }
    };
  }, [token, groupName, MAX_RECONNECT_ATTEMPTS]);

  useEffect(() => {
    isMounted.current = true;
    connect();
    return () => {
      isMounted.current = false;
      socketRef.current?.close(1000, "Component unmount");
      socketRef.current = null;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      reconnectAttempts.current = 0;
    };
  }, [connect]);

  return {
    sendMessage: (msg: string) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(msg);
      }
    },
  };
}
