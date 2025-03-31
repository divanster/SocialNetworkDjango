import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react';
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
  const { token, refreshToken } = useAuth();
  const { subscribe, unsubscribe } = useWebSocketContext();

  // Helper functions to update state.
  const addUser = (userId: string, username: string) => {
    setOnlineUsers(prev => [...new Set([...prev, userId])]);
    setUserDetails(prev => ({ ...prev, [userId]: username }));
    console.log(`User added: ${userId} (${username})`);
  };

  const removeUser = (userId: string) => {
    setOnlineUsers(prev => prev.filter(id => id !== userId));
    setUserDetails(prev => {
      const newDetails = { ...prev };
      delete newDetails[userId];
      return newDetails;
    });
    console.log(`User removed: ${userId}`);
  };

  // Fetch online users from your REST endpoint.
  const fetchOnlineUsers = async () => {
    try {
      if (!token) {
        console.error('No token found.');
        return;
      }
      // Refresh token if nearing expiry.
      const tokenPayload = decodeToken(token);
      const expiryTime = tokenPayload.exp * 1000;
      const currentTime = Date.now();
      if (expiryTime - currentTime < 60000) {
        await refreshToken();
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
  };

  // Listen for custom events dispatched by WebSocketContext.
  useEffect(() => {
  const handleUsersEvent = (event: Event) => {
    const customEvent = event as CustomEvent<any>;
    // Now you can access customEvent.detail safely.
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
  }, [token]);

  // Helper to decode JWT.
  const decodeToken = (token: string) => {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  };

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, userDetails, addUser, removeUser, fetchOnlineUsers }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = () => {
  const context = useContext(OnlineStatusContext);
  if (!context) {
    throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  }
  return context;
};
