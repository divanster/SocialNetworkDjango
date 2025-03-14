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
  const { subscribe, unsubscribe } = useWebSocketContext();
  const { token, refreshToken } = useAuth();

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
      if (!token) {
        console.error('No token found in localStorage.');
        return;
      }

      // Check if the token has expired
      const tokenPayload = decodeToken(token);
      const expiryTime = tokenPayload.exp * 1000; // Convert to milliseconds
      const currentTime = Date.now();
      const timeLeft = expiryTime - currentTime;

      if (timeLeft < 60000) {
        await refreshToken(); // Refresh token if less than 1 minute is left
      }

      const response = await axios.get(`${process.env.REACT_APP_API_URL}/get_online_users/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      const onlineIds = response.data.map((user: any) => user.id);
      const details = response.data.reduce((acc: any, user: any) => ({
        ...acc,
        [user.id]: user.username,
      }), {});
      setOnlineUsers(onlineIds);
      setUserDetails(details);
    } catch (error) {
      console.error('Error fetching online users:', error);
    }
  };

  useEffect(() => {
    subscribe('users');
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
      unsubscribe('users');
      window.removeEventListener('ws-user_online', handleOnlineStatus);
      window.removeEventListener('ws-user_offline', handleOnlineStatus);
    };
  }, [subscribe, unsubscribe]);

  useEffect(() => {
    fetchOnlineUsers();
  }, [token]);

  const decodeToken = (token: string) => {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(function (c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        })
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
  if (!context) throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  return context;
};
