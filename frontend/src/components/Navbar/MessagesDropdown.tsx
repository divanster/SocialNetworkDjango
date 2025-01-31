// frontend/src/components/Navbar/MessagesDropdown.tsx

import React, { useState, useEffect, useCallback } from 'react';
import { NavDropdown, Badge, Modal, Button, Form } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import * as api from '../../services/api'; // Corrected import path
import { fetchInboxMessages, markMessageAsRead } from '../../services/messagesService'; // Corrected function names
import { fetchFriendsList } from '../../services/friendsService'; // Corrected import source
import './MessagesDropdown.css';

interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

interface Message {
  id: string; // UUID as string
  sender: User;
  receiver: User;
  content: string;
  read: boolean; // Aliased from 'is_read'
  created_at: string;
}

interface MessagesDropdownProps {
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

const MessagesDropdown: React.FC<MessagesDropdownProps> = ({ unreadCount, setUnreadCount }) => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [showModal, setShowModal] = useState<boolean>(false);
  const [friends, setFriends] = useState<User[]>([]);
  const [selectedReceiver, setSelectedReceiver] = useState<string>(''); // User ID or 'all'
  const [messageContent, setMessageContent] = useState<string>('');
  const [sending, setSending] = useState<boolean>(false);
  const [sendError, setSendError] = useState<string | null>(null);

  // Fetch user messages from inbox
  const fetchUserMessagesFunc = useCallback(async () => {
    if (!token) {
      setError('Authentication token is missing.');
      setLoading(false);
      return;
    }

    try {
      const fetchedMessages: Message[] = await fetchInboxMessages();
      setMessages(fetchedMessages);

      // Update unread count based on fetched data
      const unread = fetchedMessages.filter((msg) => !msg.read).length;
      setUnreadCount(unread);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch messages:', err);
      if (err.response) {
        setError(`Error ${err.response.status}: ${err.response.data.detail || 'Failed to load messages.'}`);
      } else if (err.request) {
        setError('No response from server. Please check your network connection.');
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setLoading(false);
    }
  }, [token, setUnreadCount]);

  // Fetch friends list
  const fetchFriendsListFunc = useCallback(async () => {
    try {
      const fetchedFriends: User[] = await fetchFriendsList();
      setFriends(fetchedFriends);
    } catch (err: any) {
      console.error('Failed to fetch friends:', err);
      // Handle error (optional)
    }
  }, []);

  useEffect(() => {
    fetchUserMessagesFunc();
    fetchFriendsListFunc();
    // Optionally, set up WebSocket or polling for real-time updates
  }, [fetchUserMessagesFunc, fetchFriendsListFunc]);

  // Mark a message as read
  const markAsReadHandler = async (id: string) => {
    try {
      await api.markMessageAsReadAPI(id); // Assuming markMessageAsReadAPI is exported from api.ts
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === id ? { ...msg, read: true } : msg
        )
      );
      setUnreadCount((prev) => Math.max(prev - 1, 0));
    } catch (err) {
      console.error('Failed to mark message as read:', err);
      // Optionally, display a notification to the user
    }
  };

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!selectedReceiver || !messageContent.trim()) {
      setSendError('Please select a recipient and enter a message.');
      return;
    }

    setSending(true);
    setSendError(null);

    try {
      if (selectedReceiver === 'all') {
        // Broadcast message
        await api.broadcastMessage(messageContent.trim());
      } else {
        // Send to a specific user
        await api.sendMessage(Number(selectedReceiver), messageContent.trim());
      }
      // Refresh messages after sending
      await fetchUserMessagesFunc();
      // Close modal and reset form
      setShowModal(false);
      setSelectedReceiver('');
      setMessageContent('');
    } catch (err: any) {
      console.error('Failed to send message:', err);
      setSendError(err.response?.data?.error || 'Failed to send message.');
    } finally {
      setSending(false);
    }
  };

  return (
    <>
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
        <NavDropdown.Header className="d-flex justify-content-between align-items-center">
          <span>Messages</span>
          <Button variant="link" onClick={() => setShowModal(true)}>
            Send
          </Button>
        </NavDropdown.Header>
        <NavDropdown.Divider />
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
              onClick={() => !msg.read && markAsReadHandler(msg.id)}
              className={msg.read ? 'read' : 'unread'}
            >
              <div className="message-content d-flex align-items-center">
                {msg.sender.profile_picture ? (
                  <img src={msg.sender.profile_picture} alt={`${msg.sender.username}'s profile`} className="profile-picture me-2" />
                ) : (
                  <div className="profile-placeholder me-2">?</div>
                )}
                <div className="message-details flex-grow-1">
                  <strong>{msg.sender.full_name}</strong>
                  <span className="d-block">{msg.content.substring(0, 50)}{msg.content.length > 50 ? '...' : ''}</span>
                  <small className="text-muted">{new Date(msg.created_at).toLocaleString()}</small>
                </div>
              </div>
            </NavDropdown.Item>
          ))
        )}
      </NavDropdown>

      {/* Send Message Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Send a Message</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {sendError && <div className="alert alert-danger">{sendError}</div>}
          <Form>
            <Form.Group controlId="recipientSelect" className="mb-3">
              <Form.Label>Recipient</Form.Label>
              <Form.Select
                value={selectedReceiver}
                onChange={(e) => setSelectedReceiver(e.target.value)}
              >
                <option value="">Select a user</option>
                <option value="all">Everyone</option>
                {friends.map((friend) => (
                  <option key={friend.id} value={friend.id}>
                    {friend.full_name} ({friend.username})
                  </option>
                ))}
              </Form.Select>
            </Form.Group>
            <Form.Group controlId="messageContent" className="mb-3">
              <Form.Label>Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
                placeholder="Type your message here..."
              />
            </Form.Group>
            <Button variant="primary" onClick={handleSendMessage} disabled={sending}>
              {sending ? 'Sending...' : 'Send Message'}
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default MessagesDropdown;
