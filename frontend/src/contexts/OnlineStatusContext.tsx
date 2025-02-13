import React, { createContext, useContext, useState, ReactNode } from 'react';

// Define types for online users and context
interface OnlineStatusContextType {
  onlineUsers: string[];
  addUser: (userId: string) => void;
  removeUser: (userId: string) => void;
}

const OnlineStatusContext = createContext<OnlineStatusContextType | undefined>(undefined);

// Type for the provider props
interface OnlineStatusProviderProps {
  children: ReactNode;
}

export const OnlineStatusProvider: React.FC<OnlineStatusProviderProps> = ({ children }) => {
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);

  const addUser = (userId: string) => {
    setOnlineUsers((prev) => [...prev, userId]);
  };

  const removeUser = (userId: string) => {
    setOnlineUsers((prev) => prev.filter((id) => id !== userId));
  };

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, addUser, removeUser }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = (): OnlineStatusContextType => {
  const context = useContext(OnlineStatusContext);
  if (!context) {
    throw new Error('useOnlineStatus must be used within an OnlineStatusProvider');
  }
  return context;
};
