// src/contexts/WebSocketContext.tsx
import React, {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  useCallback,
} from 'react';
import { useAuth } from './AuthContext';

interface WebSocketContextType {
  isConnected: boolean;
  subscribe: (group: string) => void;
  unsubscribe: (group: string) => void;
  on: (event: string, handler: (data: any) => void) => void;
  off: (event: string, handler: (data: any) => void) => void;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();
  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const manuallyClosed = useRef<boolean>(false);
  const attemptRef = useRef<number>(0);
  const eventCallbacks = useRef<Record<string, Set<(data: any) => void>>>({});
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const pendingGroupSubs = useRef<Record<string, boolean>>({});
  const pingIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const connectWebSocket = useCallback(() => {
    if (!token) return;
    // Example endpoint – adjust as needed.
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/users/?token=${token}`;
    console.log(`Attempting WebSocket connection to ${wsUrl}`);
    const socket = new WebSocket(wsUrl);
    socketRef.current = socket;
    manuallyClosed.current = false;

    socket.onopen = () => {
      console.log('WebSocket connection established');
      setIsConnected(true);
      attemptRef.current = 0;
      Object.keys(pendingGroupSubs.current).forEach((group) => {
        if (pendingGroupSubs.current[group] && socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ action: 'subscribe', group }));
          console.log(`Subscribed to group: ${group}`);
        }
      });
      pingIntervalRef.current = setInterval(() => {
        try {
          socket.send(JSON.stringify({ action: 'ping' }));
        } catch (e) {
          console.error('WebSocket ping failed', e);
        }
      }, 30000);
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const eventName = data.event;
        if (eventName && eventCallbacks.current[eventName]) {
          eventCallbacks.current[eventName].forEach((callback) => callback(data));
        }
      } catch (err) {
        console.warn('Failed to parse WebSocket message', event.data);
      }
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    socket.onclose = (event) => {
      console.log(`WebSocket connection closed (code: ${event.code})`);
      setIsConnected(false);
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = null;
      }
      socketRef.current = null;
      // Only attempt reconnect if token still exists
      if (!manuallyClosed.current && token) {
        attemptRef.current += 1;
        const reconnectDelay = Math.min(1000 * 2 ** attemptRef.current, 30000);
        console.log(`Reconnecting WebSocket in ${reconnectDelay} ms (attempt #${attemptRef.current})`);
        reconnectTimer.current = setTimeout(connectWebSocket, reconnectDelay);
      }
    };
  }, [token]);

  useEffect(() => {
    if (token && !socketRef.current) {
      connectWebSocket();
    }
    if (!token && socketRef.current) {
      console.log('Closing WebSocket due to missing token');
      manuallyClosed.current = true;
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
      socketRef.current.close();
    }
    return () => {
      if (socketRef.current) {
        manuallyClosed.current = true;
        socketRef.current.close();
      }
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
      }
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
    };
  }, [token, connectWebSocket]);

  // Listen for logout events to immediately close the WebSocket.
  useEffect(() => {
    const handleUserLogout = () => {
      if (socketRef.current) {
        console.log('Closing WebSocket due to user logout event');
        manuallyClosed.current = true;
        if (reconnectTimer.current) {
          clearTimeout(reconnectTimer.current);
          reconnectTimer.current = null;
        }
        socketRef.current.close();
      }
    };
    window.addEventListener('user-logout', handleUserLogout);
    return () => {
      window.removeEventListener('user-logout', handleUserLogout);
    };
  }, []);

  const subscribe = useCallback((group: string) => {
    if (!group) return;
    pendingGroupSubs.current[group] = true;
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ action: 'subscribe', group }));
      console.log(`Subscribe request sent for group: ${group}`);
    }
  }, []);

  const unsubscribe = useCallback((group: string) => {
    if (!group) return;
    delete pendingGroupSubs.current[group];
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({ action: 'unsubscribe', group }));
      console.log(`Unsubscribe request sent for group: ${group}`);
    }
  }, []);

  const on = useCallback((eventName: string, handler: (data: any) => void) => {
    if (!eventCallbacks.current[eventName]) {
      eventCallbacks.current[eventName] = new Set();
    }
    eventCallbacks.current[eventName].add(handler);
  }, []);

  const off = useCallback((eventName: string, handler: (data: any) => void) => {
    eventCallbacks.current[eventName]?.delete(handler);
  }, []);

  const contextValue: WebSocketContextType = {
    isConnected,
    subscribe,
    unsubscribe,
    on,
    off,
  };

  return <WebSocketContext.Provider value={contextValue}>{children}</WebSocketContext.Provider>;
};

export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

// Backwards compatibility alias:
export const useWebSocketContext = useWebSocket;
