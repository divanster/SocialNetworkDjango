// frontend/src/contexts/WebSocketManager.tsx

import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface WebSocketContextType {
  getSocket: (url: string) => WebSocket | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sockets, setSockets] = useState<{ [url: string]: WebSocket }>({});

  const getSocket = (url: string): WebSocket | null => {
    const token = localStorage.getItem('token'); // Get token from localStorage
    const fullUrl = token ? `${url}?token=${token}` : url;

    // Check if WebSocket is already opened and return it if it's active
    if (sockets[fullUrl] && sockets[fullUrl].readyState !== WebSocket.CLOSED) {
      return sockets[fullUrl];
    }

    const ws = new WebSocket(fullUrl);

    ws.onopen = () => {
      console.log(`WebSocket connection opened for ${fullUrl}`);
    };

    ws.onmessage = (event) => {
      console.log(`Message from ${fullUrl}:`, event.data);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for ${fullUrl}:`, error);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket connection closed for ${fullUrl}:`, event);
      delete sockets[fullUrl];
      setSockets((prev) => {
        const { [fullUrl]: _, ...rest } = prev;
        return rest;
      });
    };

    setSockets((prev) => ({ ...prev, [fullUrl]: ws }));
    return ws;
  };

  useEffect(() => {
    return () => {
      // Clean up WebSocket connections when the component unmounts
      Object.values(sockets).forEach((socket) => socket.close());
    };
  }, [sockets]);

  return (
    <WebSocketContext.Provider value={{ getSocket }}>
      {children}
    </WebSocketContext.Provider>
  );
};

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};
