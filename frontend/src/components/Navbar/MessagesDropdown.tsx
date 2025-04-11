import React, { useState, useEffect, useCallback } from 'react';
import { NavDropdown, Badge, Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import {
  sendMessageToUser,
  broadcastMessageToAll,
  markMessageAsRead,
  fetchInboxMessages,
  Message,
} from '../../services/messagesService';
import { fetchFriendsList, User } from '../../services/friendsService';
import './MessagesDropdown.css';

interface MessagesDropdownProps {
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

const MessagesDropdown: React.FC<MessagesDropdownProps> = ({ unreadCount, setUnreadCount }) => {
  const { token, user } = useAuth(); // Added user from AuthContext
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Modal state
  const [showModal, setShowModal] = useState<boolean>(false);
  const [friends, setFriends] = useState<User[]>([]);
  const [friendsLoading, setFriendsLoading] = useState<boolean>(false);
  const [friendsError, setFriendsError] = useState<string | null>(null);
  const [selectedReceiver, setSelectedReceiver] = useState<string>(''); // userId or 'all'
  const [messageContent, setMessageContent] = useState<string>('');
  const [sending, setSending] = useState<boolean>(false);
  const [sendError, setSendError] = useState<string | null>(null);

  // Fetch user messages from inbox
  const fetchUserMessages = useCallback(async () => {
    if (!token) {
      setError('Authentication token is missing.');
      setLoading(false);
      return;
    }
    try {
      setLoading(true);
      const fetchedMessages: Message[] = await fetchInboxMessages();
      setMessages(fetchedMessages);

      // Calculate unread messages count
      const unread = fetchedMessages.filter((msg) => !msg.read).length;
      setUnreadCount(unread);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch messages:', err);
      setError('Failed to load messages.');
    } finally {
      setLoading(false);
    }
  }, [token, setUnreadCount]);

  // Fetch friends list (Fixed: Pass the current user's id)
  const fetchFriends = useCallback(async () => {
    setFriendsLoading(true);
    try {
      if (!user) {
        throw new Error("User not authenticated");
      }
      // Convert user.id to string if needed
      const data = await fetchFriendsList(String(user.id));
      setFriends(Array.isArray(data) ? data : []);
      setFriendsError(null);
    } catch (err) {
      console.error('Failed to fetch friends:', err);
      setFriendsError('Failed to load friends.');
    } finally {
      setFriendsLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchUserMessages();
    fetchFriends();
  }, [fetchUserMessages, fetchFriends]);

  // Mark message as read
  const markAsReadHandler = async (id: string) => {
    try {
      await markMessageAsRead(id);
      setMessages((prev) =>
        prev.map((msg) => (msg.id === id ? { ...msg, read: true } : msg))
      );
      setUnreadCount((prev) => Math.max(prev - 1, 0));
    } catch (err) {
      console.error('Failed to mark message as read:', err);
    }
  };

  // Handle sending message
  const handleSendMessage = async () => {
    if (!selectedReceiver || !messageContent.trim()) {
      setSendError('Please select a recipient and enter a message.');
      return;
    }
    setSending(true);
    setSendError(null);
    try {
      if (selectedReceiver === 'all') {
        // Broadcast message to all users
        await broadcastMessageToAll(messageContent.trim());
      } else {
        // Send a message to a specific user (convert selectedReceiver to number)
        await sendMessageToUser(Number(selectedReceiver), messageContent.trim());
      }
      // Refresh messages after sending
      await fetchUserMessages();
      // Close modal and reset fields
      setShowModal(false);
      setSelectedReceiver('');
      setMessageContent('');
    } catch (err: any) {
      console.error('Failed to send message:', err);
      setSendError('Error sending message.');
    } finally {
      setSending(false);
    }
  };

  return (
    <>
      <NavDropdown
        title={
          <>
            Messages {unreadCount > 0 && <Badge bg="danger">{unreadCount}</Badge>}
          </>
        }
        id="messages-dropdown"
        align="end"
      >
        <NavDropdown.Header className="d-flex justify-content-between align-items-center">
          <span>Messages</span>
          <Button variant="link" onClick={() => setShowModal(true)}>
            Send
          </Button>
        </NavDropdown.Header>
        <NavDropdown.Divider />
        {loading ? (
          <NavDropdown.ItemText>
            <Spinner animation="border" size="sm" className="me-2" /> Loading...
          </NavDropdown.ItemText>
        ) : error ? (
          <NavDropdown.ItemText className="text-danger">{error}</NavDropdown.ItemText>
        ) : messages.length === 0 ? (
          <NavDropdown.ItemText>No messages.</NavDropdown.ItemText>
        ) : (
          messages.map((msg) => (
            <NavDropdown.Item
              key={msg.id}
              as={Link}
              to={`/messages/${msg.id}`}
              onClick={() => !msg.read && markAsReadHandler(msg.id)}
              className={msg.read ? 'read' : 'unread'}
            >
              <div className="d-flex align-items-center">
                {msg.sender.profile_picture ? (
                  <img
                    src={msg.sender.profile_picture}
                    alt={msg.sender.username}
                    className="profile-picture me-2"
                  />
                ) : (
                  <div className="profile-placeholder me-2">?</div>
                )}
                <div>
                  <strong>{msg.sender.full_name}</strong>
                  <div className="text-truncate" style={{ maxWidth: '200px' }}>
                    {msg.content}
                  </div>
                  <small className="text-muted">
                    {new Date(msg.created_at).toLocaleString()}
                  </small>
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
          {sendError && <Alert variant="danger">{sendError}</Alert>}
          <Form>
            <Form.Group className="mb-3" controlId="recipientSelect">
              <Form.Label>Recipient</Form.Label>
              {friendsLoading ? (
                <div className="d-flex align-items-center">
                  <Spinner animation="border" size="sm" className="me-2" /> Loading friends...
                </div>
              ) : friendsError ? (
                <Alert variant="danger">{friendsError}</Alert>
              ) : (
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
              )}
            </Form.Group>
            <Form.Group className="mb-3" controlId="messageContent">
              <Form.Label>Message</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
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
