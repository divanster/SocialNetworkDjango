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

  // Add a user to the list of online users and store their username
  const addUser = (userId: string, username: string) => {
    setOnlineUsers((prev) => [...new Set([...prev, userId])]);
    setUserDetails((prev) => ({ ...prev, [userId]: username }));
  };

  // Remove a user from the list of online users
  const removeUser = (userId: string) => {
    setOnlineUsers((prev) => prev.filter((id) => id !== userId));
    setUserDetails((prev) => {
      const newDetails = { ...prev };
      delete newDetails[userId];
      return newDetails;
    });
  };

  // Fetch the list of online users from the backend API
  const fetchOnlineUsers = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL}/get_online_users/`);
      const onlineIds = response.data.map((user: any) => user.id);
      const details = response.data.reduce(
        (acc: any, user: any) => ({
          ...acc,
          [user.id]: user.username,
        }),
        {}
      );
      setOnlineUsers(onlineIds);
      setUserDetails(details);
    } catch (error) {
      console.error('Error fetching online users:', error);
    }
  };

  // Effect to subscribe to the WebSocket channel for online status updates
  useEffect(() => {
  subscribe('users');  // Subscribe to the "users" WebSocket group

  const handleOnlineStatus = (event: CustomEvent) => {
    const message = event.detail;
    if (message.type === 'user_online') {
      addUser(message.user_id, message.username);
    } else if (message.type === 'user_offline') {
      removeUser(message.user_id);
    }
  };

  window.addEventListener('ws-user_online', handleOnlineStatus);
  window.addEventListener('ws-user_offline', handleOnlineStatus);

  return () => {
    unsubscribe('users');  // Unsubscribe from the "users" group when the component unmounts
    window.removeEventListener('ws-user_online', handleOnlineStatus);
    window.removeEventListener('ws-user_offline', handleOnlineStatus);
  };
}, [subscribe, unsubscribe]);


  // Effect to fetch initial online users
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

// Custom hook to access the context
export const useOnlineStatus = () => {
  const context = useContext(OnlineStatusContext);
  if (!context) throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  return context;
};
