import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from 'react';
import { useAuth } from './AuthContext';

interface PresenceWebSocketContextType {
  isConnected: boolean;
}

const PresenceWebSocketContext = createContext<PresenceWebSocketContextType | undefined>(undefined);

export const PresenceWebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);

  const connectWebSocket = useCallback(() => {
    if (!token) return;
    // Use the environment variable so that we connect to ws://localhost:8000/ws
    // Note: REACT_APP_WEBSOCKET_URL should be set to "ws://localhost:8000/ws" in your .env file.
    const baseWsUrl = process.env.REACT_APP_WEBSOCKET_URL;
    if (!baseWsUrl) {
      console.error('No REACT_APP_WEBSOCKET_URL set');
      return;
    }
    // Build the URL for the "users" endpoint
    const wsUrl = `${baseWsUrl}/users/?token=${token}`;
    console.log('PresenceWebSocket: Connecting to', wsUrl);

    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;

    socket.onopen = () => {
      console.log('PresenceWebSocket: connected');
      setIsConnected(true);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        // Expect events with types "user_online" and "user_offline"
        if (data.event === 'user_online' || data.event === 'user_offline') {
          window.dispatchEvent(
            new CustomEvent('ws-users', {
              detail: {
                type: data.event,
                user_id: data.user_id,
                username: data.username,
              },
            })
          );
        }
      } catch (err) {
        console.warn('PresenceWebSocket: Error parsing message:', event.data);
      }
    };

    socket.onerror = (error) => {
      console.error('PresenceWebSocket error:', error);
    };

    socket.onclose = (closeEvent) => {
      console.log('PresenceWebSocket closed:', closeEvent.code, closeEvent.reason);
      setIsConnected(false);
      socketRef.current = null;
      // Optionally, implement reconnection logic here
    };
  }, [token]);

  useEffect(() => {
    if (token && !socketRef.current) {
      connectWebSocket();
    }
    if (!token && socketRef.current) {
      socketRef.current.close();
      socketRef.current = null;
    }
    return () => {
      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [token, connectWebSocket]);

  return (
    <PresenceWebSocketContext.Provider value={{ isConnected }}>
      {children}
    </PresenceWebSocketContext.Provider>
  );
};

export const usePresenceWebSocket = () => {
  const context = useContext(PresenceWebSocketContext);
  if (!context) {
    throw new Error('usePresenceWebSocket must be used within PresenceWebSocketProvider');
  }
  return context;
};
