import React, { useEffect, useState, useCallback, FormEvent } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import { sendMessageToUser, fetchInboxMessages, broadcastMessageToAll, Message as MessageType } from '../../services/messagesService';
import { transformMessage } from '../../services/messagesService'; // ако имате такава функция
import './ChatWindow.css';

interface ChatWindowProps {
  friendId: string;
  friendName: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ friendId, friendName }) => {
  const { token, user } = useAuth();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const { sendMessage: sendWSMessage } = useWebSocket('messenger', {
    onMessage: (data: any) => {
      if (data.message && user) {
        if (
          (data.message.sender.id === friendId && data.message.receiver.id === user.id) ||
          (data.message.sender.id === user.id && data.message.receiver.id === friendId)
        ) {
          setMessages(prev => [...prev, data.message]);
        }
      }
    },
  });

  const fetchConversation = useCallback(async () => {
    if (!token || !user) return;
    setLoading(true);
    try {
      const response = await axios.get('/messenger/inbox/', {  // Използвайте правилния URL
        headers: { Authorization: `Bearer ${token}` },
      });
      // Transforming fuction here
      let allMessages: MessageType[] = Array.isArray(response.data.results)
        ? response.data.results.map(transformMessage)
        : response.data;

      // filtering messages in both directions
      const conversation = allMessages.filter((msg) => {
        return (
          (msg.sender.id === friendId && msg.receiver.id === user.id) ||
          (msg.sender.id === user.id && msg.receiver.id === friendId)
        );
      });
      setMessages(conversation);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching conversation:', err);
      setError('Failed to load conversation.');
    } finally {
      setLoading(false);
    }
  }, [token, friendId, user]);

  useEffect(() => {
    fetchConversation();
  }, [fetchConversation]);

  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!token || !user || !newMessage.trim()) return;
    try {
      if (friendId === 'all') {
        await broadcastMessageToAll(newMessage.trim());
      } else {
        const sentMsg = await sendMessageToUser(friendId, newMessage.trim());
        setMessages(prev => [...prev, sentMsg]);
      }
      setNewMessage('');
    } catch (err) {
      console.error('Error sending message', err);
      setError('Error sending message');
    }
  };

  if (!user) {
    return <div>Loading user data...</div>;
  }

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h5>Chat with {friendName}</h5>
      </div>
      <div className="chat-messages" style={{ maxHeight: '400px', overflowY: 'auto', padding: '1rem' }}>
        {loading ? (
          <div className="text-center">
            <Spinner animation="border" size="sm" />
          </div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : messages.length === 0 ? (
          <div>No messages yet.</div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className="message-item mb-2">
              <strong>{msg.sender.id === user.id ? 'You' : friendName}:</strong> {msg.content}
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
