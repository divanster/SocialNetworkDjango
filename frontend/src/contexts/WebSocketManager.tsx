import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface WebSocketContextType {
  getSocket: (url: string) => WebSocket | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sockets, setSockets] = useState<{ [url: string]: WebSocket }>({});

  const getSocket = (url: string): WebSocket | null => {
    if (sockets[url]) {
      return sockets[url];
    }

    const ws = new WebSocket(url);
    ws.onopen = () => {
      console.log(`WebSocket connection opened for ${url}`);
    };

    ws.onmessage = (event) => {
      console.log(`Message from ${url}:`, event.data);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for ${url}:`, error);
    };

    ws.onclose = (event) => {
      console.log(`WebSocket connection closed for ${url}:`, event);
      delete sockets[url];
      setSockets((prev) => {
        const { [url]: _, ...rest } = prev;
        return rest;
      });
    };

    setSockets((prev) => ({ ...prev, [url]: ws }));
    return ws;
  };

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
