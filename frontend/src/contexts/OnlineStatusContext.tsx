// frontend/src/contexts/OnlineStatusContext.tsx

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';
import useWebSocket from '../hooks/useWebSocket';

interface UserType { id: string; username: string; }

export const OnlineStatusContext = createContext<{
  onlineUsers: string[];
  userDetails: Record<string,string>;
  refresh: () => Promise<void>;
}>({
  onlineUsers: [],
  userDetails: {},
  refresh: async () => {},
});

export const OnlineStatusProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token, loading: authLoading } = useAuth();
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [userDetails, setUserDetails] = useState<Record<string,string>>({});

  const refresh = useCallback(async () => {
    if (!token) return;
    try {
      const { data } = await axios.get<{ online_users: UserType[] }>(
        `${process.env.REACT_APP_API_URL}/get_online_users/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const list = data.online_users;
      const ids = list.map(u => u.id);
      const details = Object.fromEntries(list.map(u => [u.id, u.username]));
      setOnlineUsers(ids);
      setUserDetails(details);
      console.log('🔄 Refreshed onlineUsers:', ids);
    } catch (err) {
      console.error('❌ fetch online users failed', err);
    }
  }, [token]);

  useWebSocket<{ event?:string; type?:string; user_id:string; username:string }>(
    'presence',
    {
      onMessage: ({ event, type, user_id, username }) => {
        const ev = (event ?? type ?? '').replace(/[.\-]/g, '_');
        if (ev === 'user_online') {
          setOnlineUsers(prev => Array.from(new Set([...prev, user_id])));
          setUserDetails(d => ({ ...d, [user_id]: username }));
        } else if (ev === 'user_offline') {
          setOnlineUsers(prev => prev.filter(id => id !== user_id));
          setUserDetails(d => {
            const { [user_id]: _, ...rest } = d;
            return rest;
          });
        }
      },
    }
  );

  useEffect(() => {
    if (!authLoading && token) refresh();
  }, [authLoading, token, refresh]);

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, userDetails, refresh }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = () => {
  const ctx = useContext(OnlineStatusContext);
  if (!ctx) throw new Error('useOnlineStatus must be under OnlineStatusProvider');
  return ctx;
};
