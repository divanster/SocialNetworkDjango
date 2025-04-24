import { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function useNotificationsSocket() {
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    // Build the WS URL from your env or default
    const base =
      process.env.REACT_APP_WEBSOCKET_URL ||
      window.location.origin.replace(/^http/, 'ws');
    const ws = new WebSocket(`${base}/ws/notifications/?token=${token}`);

    ws.onopen = () => console.debug('[WS] notifications connected');
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        console.log('🔔 incoming WS notification:', msg);
        // TODO: dispatch into context or state here
      } catch (err) {
        console.error('WS parse error', err);
      }
    };
    ws.onclose = () => console.debug('[WS] notifications closed');

    return () => {
      ws.close();
    };
  }, [token]);
}
