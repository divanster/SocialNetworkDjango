// frontend/src/pages/Messages.tsx

import React, { useEffect, useState } from 'react';
import {
  fetchInboxMessagesService,
  sendMessageService,
  broadcastMessageService,
  markMessageAsRead
} from '../services/messagesService';
import { fetchFriendsList } from '../services/friendsService';
import { useAuth } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';
import { Button, Modal, Form, Alert, Spinner } from 'react-bootstrap';
import MessagesList from '../components/Messages/MessagesList'; // Ensure this path is correct
import './Messages.css'; // Assuming CSS is handled separately

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

const Messages: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [selectedReceiver, setSelectedReceiver] = useState<string>(''); // User ID or 'all'
  const [friends, setFriends] = useState<User[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);
  const [isLoadingFriends, setIsLoadingFriends] = useState<boolean>(false);
  const [showModal, setShowModal] = useState<boolean>(false);
  const [sendError, setSendError] = useState<string | null>(null);
  const [sendSuccess, setSendSuccess] = useState<string | null>(null);
  const { isAuthenticated, token } = useAuth(); // Extract token from useAuth

  useEffect(() => {
    if (isAuthenticated && token) {
      // Fetch messages when authenticated
      const fetchMessagesAsync = async () => {
        setIsLoadingMessages(true);
        try {
          const fetchedMessages: Message[] = await fetchInboxMessagesService();
          setMessages(fetchedMessages);
        } catch (error) {
          console.error('Error fetching messages:', error);
          // Optionally, display a notification to the user
        } finally {
          setIsLoadingMessages(false);
        }
      };

      // Fetch friends list
      const fetchFriendsAsync = async () => {
        setIsLoadingFriends(true);
        try {
          const fetchedFriends: User[] = await fetchFriendsList();
          setFriends(fetchedFriends);
        } catch (error) {
          console.error('Error fetching friends:', error);
          // Optionally, display a notification to the user
        } finally {
          setIsLoadingFriends(false);
        }
      };

      fetchMessagesAsync();
      fetchFriendsAsync();
    }
  }, [isAuthenticated, token]);

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!selectedReceiver || !newMessage.trim()) {
      setSendError('Please select a recipient and enter a message.');
      return;
    }

    setSendError(null);
    setSendSuccess(null);

    try {
      if (selectedReceiver === 'all') {
        // Broadcast message
        await broadcastMessageService(newMessage.trim());
      } else {
        // Send to a specific user
        await sendMessageService(Number(selectedReceiver), newMessage.trim());
      }
      // Refresh messages after sending
      const updatedMessages: Message[] = await fetchInboxMessagesService();
      setMessages(updatedMessages);
      // Clear form
      setNewMessage('');
      setSelectedReceiver('');
      setSendSuccess('Message sent successfully!');
      setShowModal(false);
    } catch (error: any) {
      console.error('Error sending message:', error);
      setSendError(error.response?.data?.error || 'Failed to send message.');
    }
  };

  // Handle marking a message as read
  const handleMarkAsRead = async (messageId: string) => {
    try {
      await markMessageAsRead(messageId);
      // Update message state to mark it as read
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === messageId ? { ...msg, read: true } : msg
        )
      );
    } catch (error) {
      console.error('Error marking message as read:', error);
      // Optionally, display a notification to the user
    }
  };

  return (
    <div className="messages-container container mt-4">
      <h2>Messages</h2>

      <div className="messages-header d-flex justify-content-between align-items-center mb-3">
        <Button variant="primary" onClick={() => setShowModal(true)}>
          Send Message
        </Button>
      </div>

      {isLoadingMessages ? (
        <div className="text-center">
          <Spinner animation="border" role="status" />
          <span className="ms-2">Loading messages...</span>
        </div>
      ) : messages.length === 0 ? (
        <Alert variant="info">No messages to display.</Alert>
      ) : (
        <MessagesList
          messages={messages}
          isLoading={isLoadingMessages}
          handleMarkAsRead={handleMarkAsRead}
        />
      )}

      {/* Send Message Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Send a Message</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {sendError && <Alert variant="danger">{sendError}</Alert>}
          {sendSuccess && <Alert variant="success">{sendSuccess}</Alert>}
          <Form>
            <Form.Group controlId="recipientSelect" className="mb-3">
              <Form.Label>Recipient</Form.Label>
              <Form.Select
                value={selectedReceiver}
                onChange={(e) => setSelectedReceiver(e.target.value)}
                aria-label="Select recipient"
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
                value={newMessage}
                onChange={(e) => setNewMessage(e.target.value)}
                placeholder="Type your message here..."
                aria-label="Message content"
              />
            </Form.Group>
            <Button variant="primary" onClick={handleSendMessage} disabled={!newMessage.trim() || !selectedReceiver}>
              Send Message
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default Messages;
