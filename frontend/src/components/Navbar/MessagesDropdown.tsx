// frontend/src/components/Navbar/MessagesDropdown.tsx

import React, { useState, useEffect } from 'react';
import { NavDropdown, Badge } from 'react-bootstrap';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import './MessagesDropdown.css';

interface Message {
  id: number;
  sender: {
    id: number;
    username: string;
    full_name: string;
    profile_picture: string;
  };
  content: string;
  created_at: string;
  read: boolean;
}

interface MessagesDropdownProps {
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const MessagesDropdown: React.FC<MessagesDropdownProps> = ({ unreadCount, setUnreadCount }) => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch messages
  const fetchUserMessages = async () => {
    if (!token) return;

    try {
      const response = await axios.get(`${API_URL}/messages/inbox/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages(response.data);
      // Update unread count based on fetched data
      const unread = response.data.filter((msg: Message) => !msg.read).length;
      setUnreadCount(unread);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch messages:', err);
      setError('Failed to load messages.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserMessages();
    // Optionally, set up WebSocket or polling to fetch messages in real-time
    // For example, using WebSockets:
    // const ws = new WebSocket(`${API_URL.replace(/^http/, 'ws')}/ws/messages/`);
    // ws.onmessage = (event) => { /* handle incoming messages */ };
    // return () => { ws.close(); };
  }, [token]);

  // Mark a message as read
  const markAsRead = async (id: number) => {
    try {
      await axios.patch(
        `${API_URL}/messages/${id}/`,
        { read: true },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === id ? { ...msg, read: true } : msg
        )
      );
      setUnreadCount((prev) => prev - 1);
    } catch (err) {
      console.error('Failed to mark message as read:', err);
    }
  };

  return (
    <NavDropdown
      title={
        <>
          Messages{' '}
          {unreadCount > 0 && <Badge bg="danger">{unreadCount}</Badge>}
        </>
      }
      id="messages-dropdown"
      align="end"
      className="messages-dropdown"
    >
      {loading ? (
        <NavDropdown.ItemText>Loading...</NavDropdown.ItemText>
      ) : error ? (
        <NavDropdown.ItemText className="text-danger">{error}</NavDropdown.ItemText>
      ) : messages.length === 0 ? (
        <NavDropdown.ItemText>No messages.</NavDropdown.ItemText>
      ) : (
        messages.map((msg) => (
          <NavDropdown.Item
            key={msg.id}
            as={Link}
            to={`/messages/${msg.id}`} // Route to detailed message page
            onClick={() => !msg.read && markAsRead(msg.id)}
            className={msg.read ? 'read' : 'unread'}
          >
            <div className="message-content">
              <img src={msg.sender.profile_picture} alt={`${msg.sender.username}'s profile`} />
              <div>
                <strong>{msg.sender.full_name}</strong>
                <span>{msg.content}</span>
                <small className="text-muted">{new Date(msg.created_at).toLocaleString()}</small>
              </div>
            </div>
          </NavDropdown.Item>
        ))
      )}
    </NavDropdown>
  );
};

export default MessagesDropdown;
