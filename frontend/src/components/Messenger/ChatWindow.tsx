import React, { useEffect, useState, useCallback, FormEvent } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import './ChatWindow.css';

export interface Message {
  id: string;
  sender: {
    id: string;
    username: string;
    full_name: string;
    profile_picture: string | null;
  };
  receiver: {
    id: string;
    username: string;
    full_name: string;
    profile_picture: string | null;
  };
  content: string;
  read: boolean;
  created_at: string;
}

interface ChatWindowProps {
  friendId: string; // Selected friend’s id (string)
  friendName: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ friendId, friendName }) => {
  const { token, user } = useAuth();
  const [allMessages, setAllMessages] = useState<Message[]>([]);
  const [conversationMessages, setConversationMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Use WebSocket for real‑time updates in the "messenger" group
  const { sendMessage: sendWSMessage } = useWebSocket('messenger', {
    onMessage: (data: any) => {
      const msg: Message = data.message;
      // Check if the message belongs to the conversation between the current user and friend
      if (
        (msg.sender.id === friendId && msg.receiver.id === user?.id) ||
        (msg.sender.id === user?.id && msg.receiver.id === friendId)
      ) {
        setConversationMessages(prev => [...prev, msg]);
      }
    },
  });

  // Fetch all inbox messages
  const fetchInbox = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const response = await axios.get('/messenger/inbox/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      const messages: Message[] = response.data.results || response.data;
      setAllMessages(messages);
      setError(null);
    } catch (err: any) {
      console.error('Failed to fetch inbox messages:', err);
      setError('Failed to load messages.');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Filter messages between the current user and the selected friend
  const filterConversation = useCallback(() => {
    if (!user) return;
    const conversation = allMessages.filter((msg) => {
      return (
        (msg.sender.id === friendId && msg.receiver.id === user.id) ||
        (msg.sender.id === user.id && msg.receiver.id === friendId)
      );
    });
    conversation.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    setConversationMessages(conversation);
  }, [allMessages, friendId, user]);

  useEffect(() => {
    if (token) {
      fetchInbox();
    }
  }, [token, fetchInbox]);

  useEffect(() => {
    filterConversation();
  }, [allMessages, filterConversation]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!token || !newMessage.trim() || !user) return;
    try {
      const response = await axios.post(
        '/messenger/',
        { receiver: friendId, content: newMessage.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const sentMsg: Message = response.data;
      setConversationMessages(prev => [...prev, sentMsg]);
      setNewMessage('');
      // Optionally, you can also trigger a WebSocket update:
      // sendWSMessage({ friendId, message: sentMsg });
    } catch (err) {
      console.error('Error sending message', err);
      setError('Failed to send message.');
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h5>Chat with {friendName}</h5>
      </div>
      <div className="chat-messages">
        {loading ? (
          <div className="text-center">
            <Spinner animation="border" size="sm" />
          </div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : conversationMessages.length === 0 ? (
          <div>No messages yet.</div>
        ) : (
          conversationMessages.map((msg) => (
            <div key={msg.id} className="message-item">
              <strong>{msg.sender.username}:</strong> {msg.content}
              <br />
              <small className="text-muted">{new Date(msg.created_at).toLocaleTimeString()}</small>
            </div>
          ))
        )}
      </div>
      <div className="chat-input">
        <Form onSubmit={handleSend} className="d-flex">
          <Form.Control
            type="text"
            placeholder="Type your message..."
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <Button variant="primary" type="submit" className="ms-2">
            Send
          </Button>
        </Form>
      </div>
    </div>
  );
};

export default ChatWindow;
