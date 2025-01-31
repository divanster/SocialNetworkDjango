// frontend/src/components/Navbar/NotificationsDropdown.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { NavDropdown, Badge } from 'react-bootstrap';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import './NotificationsDropdown.css';

interface Notification {
  id: string;
  notification_type: string;
  text: string;
  read: boolean;
  created_at: string;
  sender_username: string;
  receiver_username: string;
  content_object_url: string | null;
}

interface NotificationsDropdownProps {
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const NotificationsDropdown: React.FC<NotificationsDropdownProps> = ({ unreadCount, setUnreadCount }) => {
  const { token } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user notifications with useCallback to memoize the function
  const fetchUserNotifications = useCallback(async () => {
    if (!token) {
      setError('Authentication token is missing.');
      setLoading(false);
      return;
    }

    try {
      const response = await axios.get(`${API_URL}/notifications/`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Handle paginated response
      const fetchedNotifications: Notification[] = response.data.results || response.data;

      setNotifications(fetchedNotifications);

      // Update unread count based on fetched data
      const unread = fetchedNotifications.filter((notif) => !notif.read).length;
      setUnreadCount(unread);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch notifications:', err);
      if (err.response) {
        setError(`Error ${err.response.status}: ${err.response.data.detail || 'Failed to load notifications.'}`);
      } else if (err.request) {
        setError('No response from server. Please check your network connection.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [token, setUnreadCount]);

  useEffect(() => {
    fetchUserNotifications();
  }, [fetchUserNotifications]);

  // Handle real-time updates via WebSocket
  useWebSocket<Notification>('notifications', {
    onMessage: (data) => {
      setNotifications((prev) => [data, ...prev]);
      setUnreadCount((prev) => prev + 1);
    }
  });

  // Mark a notification as read
  const markAsRead = async (id: string) => {
    try {
      await axios.post(
        `${API_URL}/notifications/${id}/mark-as-read/`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setNotifications((prev) =>
        prev.map((notif) =>
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
      setUnreadCount((prev) => Math.max(prev - 1, 0));
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
      // Optionally, display a notification to the user
    }
  };

  return (
    <NavDropdown
      title={
        <>
          Notifications{' '}
          {unreadCount > 0 && <Badge bg="danger">{unreadCount}</Badge>}
        </>
      }
      id="notifications-dropdown"
      align="end"
      className="notifications-dropdown"
    >
      {loading ? (
        <NavDropdown.ItemText>Loading...</NavDropdown.ItemText>
      ) : error ? (
        <NavDropdown.ItemText className="text-danger">{error}</NavDropdown.ItemText>
      ) : notifications.length === 0 ? (
        <NavDropdown.ItemText>No new notifications.</NavDropdown.ItemText>
      ) : (
        notifications.map((notif) => (
          <NavDropdown.Item
            key={notif.id}
            as={Link}
            to={`/notifications/${notif.id}`} // Route to detailed notification page
            onClick={() => !notif.read && markAsRead(notif.id)}
            className={notif.read ? 'read' : 'unread'}
          >
            <div className="notification-content">
              <div className="notification-details">
                <span>{notif.text}</span>
                <small className="text-muted">{new Date(notif.created_at).toLocaleString()}</small>
              </div>
            </div>
          </NavDropdown.Item>
        ))
      )}
    </NavDropdown>
  );
};

export default NotificationsDropdown;
