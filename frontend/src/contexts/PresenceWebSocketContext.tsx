import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback
} from 'react';
import { useAuth } from './AuthContext';

interface PresenceWebSocketContextType {
  isConnected: boolean;
}

const PresenceWebSocketContext = createContext<PresenceWebSocketContextType | undefined>(undefined);

export const PresenceWebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<number | null>(null);

  // open socket once when token appears
  const connectWebSocket = useCallback(() => {
    if (!token || socketRef.current) return;

    const baseWsUrl = process.env.REACT_APP_WEBSOCKET_URL;
    if (!baseWsUrl) {
      console.error('PresenceWebSocket ▶ no REACT_APP_WEBSOCKET_URL defined');
      return;
    }

    // hit /presence/ on the root
    const wsUrl = `${baseWsUrl}/presence/?token=${token}`;
    console.log('PresenceWebSocket ▶ connecting to', wsUrl);

    const sock = new WebSocket(wsUrl);
    socketRef.current = sock;

    sock.onopen = () => {
      console.log('PresenceWebSocket ▶ connected');
      setIsConnected(true);
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    sock.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        const rawType = data.event ?? data.type;
        const evType = rawType.replace(/\./g, '_');
        if (evType === 'user_online' || evType === 'user_offline') {
          window.dispatchEvent(new CustomEvent('ws-users', {
            detail: {
              type: evType,
              user_id: String(data.user_id),
              username: data.username,
            },
          }));
        }
      } catch {
        console.warn('PresenceWebSocket ▶ malformed message', ev.data);
      }
    };

    sock.onerror = (err) => {
      console.error('PresenceWebSocket ▶ error', err);
    };

    sock.onclose = (closeEvent) => {
      if (closeEvent.code !== 1000) {
        console.warn(
          `PresenceWebSocket ▶ closed code=${closeEvent.code} reason="${closeEvent.reason}"`
        );
        reconnectTimer.current = window.setTimeout(connectWebSocket, 5000);
      } else {
        console.log('PresenceWebSocket ▶ closed normally');
      }
      setIsConnected(false);
      socketRef.current = null;
    };
  }, [token]);

  // open/close lifecycle
  useEffect(() => {
    if (token) {
      connectWebSocket();
    } else if (socketRef.current) {
      socketRef.current.close(1000, 'Logging out');
      socketRef.current = null;
    }
    return () => {
      if (socketRef.current) {
        socketRef.current.close(1000, 'Unmount');
        socketRef.current = null;
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
    };
  }, [token, connectWebSocket]);

  // once connected and user loads, announce ourselves
  useEffect(() => {
    if (isConnected && user?.id && user.username) {
      window.dispatchEvent(new CustomEvent('ws-users', {
        detail: {
          type: 'user_online',
          user_id: String(user.id),
          username: user.username,
        },
      }));
    }
  }, [isConnected, user]);

  return (
    <PresenceWebSocketContext.Provider value={{ isConnected }}>
      {children}
    </PresenceWebSocketContext.Provider>
  );
};

export const usePresenceWebSocket = () => {
  const ctx = useContext(PresenceWebSocketContext);
  if (!ctx) throw new Error('usePresenceWebSocket must be used within PresenceWebSocketProvider');
  return ctx;
};
