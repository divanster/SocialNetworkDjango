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

  // always keep handlersRef up to date
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const connect = useCallback(() => {
    if (!token || !groupName || !isMounted.current) return;

    // strip trailing /ws if your .env accidentally put one on:
    const rawBase = process.env.REACT_APP_WEBSOCKET_URL!;
    const cleanBase = rawBase.replace(/\/ws\/?$/, "");

    // now build exactly one /ws/<groupName> path:
    const url = `${cleanBase}/ws/${groupName}/?token=${token}`;
    console.log(`🔌 WS → ${url}`);
    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`✅ WS(${groupName}) opened`);
      handlersRef.current.onOpen?.();
    };
    ws.onmessage = (evt) => {
      try {
        handlersRef.current.onMessage(JSON.parse(evt.data));
      } catch (e) {
        console.error(`❌ WS(${groupName}) parse error`, e);
      }
    };
    ws.onerror = (err) => {
      console.error(`⚠️ WS(${groupName}) error`, err);
      handlersRef.current.onError?.(err);
    };
    ws.onclose = (ev) => {
      console.warn(`🚧 WS(${groupName}) closed`, ev);
      handlersRef.current.onClose?.(ev);
      if (ev.code !== 1000 && isMounted.current) {
        reconnectTimer.current = window.setTimeout(connect, 5_000);
      }
    };
  }, [token, groupName]);

  useEffect(() => {
    isMounted.current = true;
    connect();
    return () => {
      isMounted.current = false;
      socketRef.current?.close(1000, "Component unmount");
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  return {
    sendMessage: (msg: string) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(msg);
      } else {
        console.warn(`🚫 WS(${groupName}) not open; cannot send`);
      }
    },
  };
}
