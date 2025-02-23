// frontend/src/contexts/OnlineStatusContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
import axios from 'axios';
import { useWebSocketContext } from './WebSocketContext';

interface OnlineStatusContextType {
  onlineUsers: string[];
  userDetails: { [key: string]: string };
  addUser: (userId: string, username: string) => void;
  removeUser: (userId: string) => void;
  fetchOnlineUsers: () => Promise<void>;
}

const OnlineStatusContext = createContext<OnlineStatusContextType | undefined>(undefined);

export const OnlineStatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [userDetails, setUserDetails] = useState<{ [key: string]: string }>({});
  const { subscribe, unsubscribe } = useWebSocketContext();

  const addUser = (userId: string, username: string) => {
    setOnlineUsers(prev => [...new Set([...prev, userId])]);
    setUserDetails(prev => ({ ...prev, [userId]: username }));
  };

  const removeUser = (userId: string) => {
    setOnlineUsers(prev => prev.filter(id => id !== userId));
    setUserDetails(prev => {
      const newDetails = { ...prev };
      delete newDetails[userId];
      return newDetails;
    });
  };

  const fetchOnlineUsers = async () => {
  try {
    const response = await axios.get('/api/v1/users/get_online_users/'); // Corrected endpoint
    const onlineIds = response.data.map((user: any) => user.id);
    const details = response.data.reduce((acc: any, user: any) => ({
      ...acc,
      [user.id]: user.username
    }), {});

    setOnlineUsers(onlineIds);
    setUserDetails(details);
  } catch (error) {
    console.error('Error fetching online users:', error);
  }
};

  useEffect(() => {
    // Setup WebSocket subscriptions
    subscribe('online_status');

    const handleOnlineStatus = (event: Event) => {
      const message = (event as CustomEvent).detail;
      if (message.type === 'USER_ONLINE') {
        addUser(message.userId, message.username);
      } else if (message.type === 'USER_OFFLINE') {
        removeUser(message.userId);
      }
    };

    window.addEventListener('ws-online_status', handleOnlineStatus);

    return () => {
      unsubscribe('online_status');
      window.removeEventListener('ws-online_status', handleOnlineStatus);
    };
  }, [subscribe, unsubscribe]);

  useEffect(() => {
    fetchOnlineUsers();
  }, []);

  return (
    <OnlineStatusContext.Provider
      value={{ onlineUsers, userDetails, addUser, removeUser, fetchOnlineUsers }}
    >
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = () => {
  const context = useContext(OnlineStatusContext);
  if (!context) throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  return context;
};
