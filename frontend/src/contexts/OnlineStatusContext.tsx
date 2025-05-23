// frontend/src/contexts/OnlineStatusContext.tsx
import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
  useCallback,
} from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';
import useWebSocket from '../hooks/useWebSocket';

interface PresenceEvent {
  event?: string;   // e.g. 'user_online'
  type?: string;    // fallback 'user.online'
  user_id: string;
  username: string;
}

interface OnlineStatusValue {
  onlineUsers: string[];
  userDetails: Record<string,string>;
  refresh: () => Promise<void>;
}

const defaultCtx: OnlineStatusValue = {
  onlineUsers: [],
  userDetails: {},
  refresh: async () => {},
};

const OnlineStatusContext = createContext<OnlineStatusValue>(defaultCtx);

export const OnlineStatusProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { token, loading: authLoading } = useAuth();
  const [onlineUsers, setOnlineUsers] = useState<string[]>([]);
  const [userDetails, setUserDetails] = useState<Record<string,string>>({});

  // REST fetch
  const refresh = useCallback(async () => {
    if (!token) return;
    try {
      const { data } = await axios.get(
        `${process.env.REACT_APP_API_URL}/get_online_users/`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const ids = data.map((u:any) => u.id);
      const details = Object.fromEntries(data.map((u:any) => [u.id, u.username]));
      setOnlineUsers(ids);
      setUserDetails(details);
      console.log('🔄 Refreshed onlineUsers:', ids);
    } catch (err) {
      console.error('❌ fetch online users failed', err);
    }
  }, [token]);

  // WebSocket => listen for server-side user_online / user_offline
  useWebSocket<PresenceEvent>(
    'users',
    {
      onMessage: ({ event, type, user_id, username }) => {
        const raw = event ?? type ?? '';
        const ev = raw.replace(/\./g, '_');
        if (ev === 'user_online') {
          setOnlineUsers((prev) => Array.from(new Set([...prev, user_id])));
          setUserDetails((d) => ({ ...d, [user_id]: username }));
        } else if (ev === 'user_offline') {
          setOnlineUsers((prev) => prev.filter((id) => id !== user_id));
          setUserDetails((d) => {
            const c = { ...d };
            delete c[user_id];
            return c;
          });
        }
      },
    }
  );

  // Only kick off after Auth is finished loading **and** we have a token
  useEffect(() => {
    if (authLoading || !token) return;
    refresh();
  }, [authLoading, token, refresh]);

  return (
    <OnlineStatusContext.Provider value={{ onlineUsers, userDetails, refresh }}>
      {children}
    </OnlineStatusContext.Provider>
  );
};

export const useOnlineStatus = () => {
  const ctx = useContext(OnlineStatusContext);
  if (!ctx) {
    throw new Error('useOnlineStatus must be used within OnlineStatusProvider');
  }
  return ctx;
};
