// src/contexts/OnlineStatusContext.tsx
import React, { createContext, useContext, useState, ReactNode, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useWebSocketContext } from './WebSocketContext';
import { useAuth } from './AuthContext';

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
  const { token } = useAuth();
  const { subscribe, unsubscribe } = useWebSocketContext();

  const addUser = useCallback((userId: string, username: string) => {
    setOnlineUsers((prev) => [...new Set([...prev, userId])]);
    setUserDetails((prev) => ({ ...prev, [userId]: username }));
    console.log(`User added: ${userId} (${username})`);
  }, []);

  const removeUser = useCallback((userId: string) => {
    setOnlineUsers((prev) => prev.filter(id => id !== userId));
    setUserDetails((prev) => {
      const newDetails = { ...prev };
      delete newDetails[userId];
      return newDetails;
    });
    console.log(`User removed: ${userId}`);
  }, []);

  const fetchOnlineUsers = useCallback(async () => {
    try {
      if (!token) {
        console.error('No token found.');
        return;
      }
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL}/get_online_users/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const onlineIds = response.data.map((user: any) => user.id);
      const details = response.data.reduce(
        (acc: any, user: any) => ({ ...acc, [user.id]: user.username }),
        {}
      );
      setOnlineUsers(onlineIds);
      setUserDetails(details);
      console.log('Fetched online users:', onlineIds);
    } catch (error) {
      console.error('Error fetching online users:', error);
    }
  }, [token]);

  // Listen for WebSocket events dispatched via custom events
  useEffect(() => {
    const handleUsersEvent = (event: Event) => {
      const customEvent = event as CustomEvent<any>;
      if (customEvent.detail && customEvent.detail.type === 'user_online') {
        addUser(customEvent.detail.user_id, customEvent.detail.username);
      } else if (customEvent.detail && customEvent.detail.type === 'user_offline') {
        removeUser(customEvent.detail.user_id);
      }
    };

    window.addEventListener('ws-users', handleUsersEvent as EventListener);
    return () => {
      window.removeEventListener('ws-users', handleUsersEvent as EventListener);
    };
  }, [addUser, removeUser]);

  useEffect(() => {
    if (token) {
      fetchOnlineUsers();
    }
  }, [token, fetchOnlineUsers]);

  // Optional: Refresh online users list on tab focus
  useEffect(() => {
    const handleFocus = () => {
      fetchOnlineUsers();
    };
    window.addEventListener('focus', handleFocus);
    return () => {
      window.removeEventListener('focus', handleFocus);
    };
  }, [fetchOnlineUsers]);

  const contextValue: OnlineStatusContextType = {
    onlineUsers,
    userDetails,
    addUser,
    removeUser,
    fetchOnlineUsers,
  };

  return (
    <OnlineStatusContext.Provider value={contextValue}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = (): OnlineStatusContextType => {
  const context = useContext(OnlineStatusContext);
  if (context === undefined) {
    throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  }
  return context;
};
