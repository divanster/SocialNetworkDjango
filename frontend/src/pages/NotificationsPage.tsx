import React, { useCallback, useEffect, useState } from 'react';
import { Container } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import NotificationList from '../components/Notifications/NotificationList';
import {
  listNotifications,
  markAllNotificationsAsRead,
  markNotificationAsRead,
  NotificationItem,
} from '../services/notificationsService';
import {
  NotificationDestination,
  resolveNotificationDestination,
} from '../utils/notificationDestinationResolver';
import useWebSocket from '../hooks/useWebSocket';
import './NotificationsPage.css';

interface Props {
  onUnreadCountChange?: (count: number) => void;
}

const NotificationsPage: React.FC<Props> = ({ onUnreadCountChange }) => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const mergeById = useCallback((items: NotificationItem[]) => {
    const map = new Map<string, NotificationItem>();
    items.forEach((item) => map.set(item.id, item));
    return Array.from(map.values()).sort(
      (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
    );
  }, []);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listNotifications();
      const deduped = mergeById(data);
      setNotifications(deduped);
      onUnreadCountChange?.(deduped.filter((item) => !item.read).length);
    } catch {
      setError('Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  }, [mergeById, onUnreadCountChange]);

  useEffect(() => {
    reload();
  }, [reload]);

  useWebSocket<any>('notifications', {
    onMessage: (payload) => {
      const incoming = payload?.type === 'notification' ? payload.data : payload?.data;
      if (!incoming || !incoming.id) return;
      setNotifications((prev) => {
        const merged = mergeById([incoming as NotificationItem, ...prev]);
        onUnreadCountChange?.(merged.filter((item) => !item.read).length);
        return merged;
      });
    },
  });

  const handleMarkAllRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications((prev) => prev.map((item) => ({ ...item, read: true })));
      onUnreadCountChange?.(0);
    } catch {
      setError('Failed to mark all notifications as read.');
    }
  };

  const handleSelectNotification = async (
    notification: NotificationItem,
    destination: NotificationDestination
  ) => {
    if (!notification.read) {
      try {
        await markNotificationAsRead(notification.id);
        setNotifications((prev) =>
          prev.map((item) => (item.id === notification.id ? { ...item, read: true } : item))
        );
      } catch {
        setError('Failed to mark notification as read.');
      }
    }

    if (destination.canNavigate && destination.path) {
      navigate(destination.path);
    }
  };

  return (
    <Container className="notifications-page py-3">
      <h1 className="notifications-page__title">Notifications</h1>
      <NotificationList
        notifications={notifications}
        loading={loading}
        error={error}
        onRetry={reload}
        onSelect={handleSelectNotification}
        onMarkAllRead={handleMarkAllRead}
        canMarkAllRead={notifications.some((item) => !item.read)}
        resolveDestination={resolveNotificationDestination}
      />
    </Container>
  );
};

export default NotificationsPage;
