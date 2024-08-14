import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';

interface WebSocketContextType {
  getSocket: (url: string) => WebSocket | null;
}

const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

export const WebSocketProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sockets, setSockets] = useState<{ [url: string]: WebSocket }>({});

  const getSocket = (url: string): WebSocket | null => {
    if (sockets[url] && sockets[url].readyState !== WebSocket.CLOSED) {
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

      // Optional: Implement reconnection logic
      // setTimeout(() => getSocket(url), 5000); // Retry connection after 5 seconds
    };

    setSockets((prev) => ({ ...prev, [url]: ws }));
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
