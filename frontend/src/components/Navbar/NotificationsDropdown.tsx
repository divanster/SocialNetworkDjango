// frontend/src/components/Navbar/NotificationsDropdown.tsx

import React, { useState, useEffect } from 'react';
import { NavDropdown, Badge } from 'react-bootstrap';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { fetchNotifications } from '../../services/api'; // Ensure this API exists
import './NotificationsDropdown.css';

interface Notification {
  id: number;
  type: string;
  content: string;
  created_at: string;
  read: boolean;
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

  // Fetch notifications
  const fetchUserNotifications = async () => {
    if (!token) return;

    try {
      const response = await axios.get(`${API_URL}/notifications/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setNotifications(response.data);
      // Update unread count based on fetched data
      const unread = response.data.filter((notif: Notification) => !notif.read).length;
      setUnreadCount(unread);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch notifications:', err);
      setError('Failed to load notifications.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserNotifications();
    // Optionally, set up WebSocket or polling to fetch notifications in real-time
    // For example, using WebSockets:
    // const ws = new WebSocket(`${API_URL.replace(/^http/, 'ws')}/ws/notifications/`);
    // ws.onmessage = (event) => { /* handle incoming notifications */ };
    // return () => { ws.close(); };
  }, [token]);

  // Mark a notification as read
  const markAsRead = async (id: number) => {
    try {
      await axios.patch(
        `${API_URL}/notifications/${id}/`,
        { read: true },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setNotifications((prev) =>
        prev.map((notif) =>
          notif.id === id ? { ...notif, read: true } : notif
        )
      );
      setUnreadCount((prev) => prev - 1);
    } catch (err) {
      console.error('Failed to mark notification as read:', err);
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
              <span>{notif.content}</span>
              <small className="text-muted">{new Date(notif.created_at).toLocaleString()}</small>
            </div>
          </NavDropdown.Item>
        ))
      )}
    </NavDropdown>
  );
};

export default NotificationsDropdown;
