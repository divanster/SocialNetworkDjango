// frontend/src/contexts/OnlineStatusContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import useWebSocket from '../hooks/useWebSocket';
import { useAuth } from './AuthContext';

interface PresenceEvent {
  event?: string;
  type?: string;
  user_id: string;
  username: string;
}

// define the shape of your context value
interface OnlineStatusValue {
  onlineUsers: string[];
  // if you also need details (e.g. usernames), add:
  userDetails?: Record<string, string>;
}

const OnlineStatusContext = createContext<OnlineStatusValue | undefined>(undefined);

export const OnlineStatusProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, token } = useAuth();
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [userDetails, setUserDetails] = useState<Record<string,string>>({});

  // initial fetch
  useEffect(() => {
    if (!token) return;
    (async () => {
      const res = await fetch(`${process.env.REACT_APP_API_URL}/get_online_users/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const { users, details }: { users: string[]; details?: Record<string,string> } = await res.json();
      setOnlineUsers(users);
      if (details) setUserDetails(details);
    })().catch(console.error);
  }, [token]);

  // websocket logic as before...
  useWebSocket<PresenceEvent>('presence', {
    onOpen: () => {
      if (user?.id && user.username) {
        window.dispatchEvent(new CustomEvent('ws-users', {
          detail: { type: 'user_online', user_id: user.id, username: user.username }
        }));
      }
    },
    onMessage: (data) => {
      const raw = data.event ?? data.type ?? '';
      const evType = raw.replace(/\./g, '_');
      if (evType === 'user_online') {
        setOnlineUsers(prev => Array.from(new Set([...prev, data.user_id])));
        setUserDetails(d => ({ ...d, [data.user_id]: data.username }));
      }
      if (evType === 'user_offline') {
        setOnlineUsers(prev => prev.filter(id => id !== data.user_id));
        // optionally: remove details[data.user_id]
      }
    }
  });

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, userDetails }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = () => {
  const ctx = useContext(OnlineStatusContext);
  if (!ctx) throw new Error('useOnlineStatus must be inside <OnlineStatusProvider>');
  return ctx;
};
