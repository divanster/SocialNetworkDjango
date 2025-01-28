// frontend/src/components/Navbar/NotificationsDropdown.tsx

import React, { useState, useEffect } from 'react';
import { NavDropdown, Badge } from 'react-bootstrap';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './NotificationsDropdown.css';

interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

interface Notification {
  id: number;
  type: string;
  content: string;
  read: boolean;
  created_at: string;
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

  // Fetch user notifications
  const fetchUserNotifications = async () => {
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
  };

  useEffect(() => {
    fetchUserNotifications();
    // Optionally, set up WebSocket or polling for real-time updates
    // Example with WebSocket:
    // const ws = new WebSocket(`${API_URL.replace(/^http/, 'ws')}/ws/notifications/`);
    // ws.onmessage = (event) => { /* handle incoming notifications */ };
    // return () => { ws.close(); };
  }, [token]);

  // Mark a notification as read
  const markAsRead = async (id: number) => {
    try {
      await axios.patch(
        `${API_URL}/notifications/${id}/`,
        { is_read: true }, // Send 'is_read' as expected by the backend
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
                <span>{notif.content}</span>
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
