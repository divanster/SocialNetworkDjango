import { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function useNotificationsSocket() {
  const { token } = useAuth();

  useEffect(() => {
    if (!token) return;

    const baseUrl = process.env.REACT_APP_WEBSOCKET_URL || 'ws://localhost:8000';
    const ws = new WebSocket(`${baseUrl}/ws/notifications/?token=${token}`);

    ws.onopen = () => console.debug('[WS] notifications connected');
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        console.log('🔔 incoming WS notification:', msg);
      } catch (err) {
        console.error('WS parse error', err);
      }
    };
    ws.onclose = () => console.debug('[WS] notifications closed');

    return () => ws.close();
  }, [token]);
}
