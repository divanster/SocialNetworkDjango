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

  // Keep handlers fresh even if the user re-renders
  useEffect(() => {
    handlersRef.current = handlers;
  }, [handlers]);

  const connect = useCallback(() => {
    if (!token || !groupName || !isMounted.current) return;

    const base = process.env.REACT_APP_WEBSOCKET_URL!;
    const url = `${base}/${groupName}/?token=${token}`;
    console.log(`🔌 WS→ ${url}`);

    const ws = new WebSocket(url);
    socketRef.current = ws;

    ws.onopen = () => {
      console.log(`✅ WS(${groupName}) opened`);
      handlersRef.current.onOpen?.();
    };

    ws.onmessage = (evt) => {
      try {
        const data: T = JSON.parse(evt.data);
        handlersRef.current.onMessage(data);
      } catch (err) {
        console.error(`❌ WS(${groupName}) parse error`, err);
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
        reconnectTimer.current = window.setTimeout(connect, 5000);
      }
    };
  }, [token, groupName]);

  useEffect(() => {
    isMounted.current = true;
    connect();
    return () => {
      isMounted.current = false;
      socketRef.current?.close(1000, 'Component unmount');
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  const sendMessage = useCallback(
    (msg: string) => {
      if (socketRef.current?.readyState === WebSocket.OPEN) {
        socketRef.current.send(msg);
      } else {
        console.warn(`🚫 WS(${groupName}) not open; cannot send`);
      }
    },
    [groupName]
  );

  return { sendMessage };
}
