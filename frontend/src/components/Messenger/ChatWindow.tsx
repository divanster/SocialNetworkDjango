// frontend/src/components/Messenger/ChatWindow.tsx
import React, { useEffect, useState, useCallback } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';

export interface Message {
  id: string;
  sender: any;    // Extend or replace 'any' with your proper type
  receiver: any;
  content: string;
  read: boolean;
  created_at: string;
}

interface ChatWindowProps {
  conversationId: string; // For now, you can use the friend's id as conversation id.
  friendName: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ conversationId, friendName }) => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Use the WebSocket hook for real-time updates.
  const { sendMessage: sendWSMessage } = useWebSocket('messenger', {
    onMessage: (data: any) => {
      // Filter messages for the current conversation
      if (data.conversationId === conversationId) {
        setMessages(prev => [...prev, data.message]);
      }
    },
  });

  // Fetch conversation history using API.
  const fetchConversation = useCallback(async () => {
    if (!token) return;
    setLoading(true);
    try {
      const response = await axios.get(`/messenger/conversations/${conversationId}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMessages(response.data.messages || []);
      setError(null);
    } catch (err: any) {
      setError('Failed to load conversation.');
    } finally {
      setLoading(false);
    }
  }, [conversationId, token]);

  useEffect(() => {
    fetchConversation();
  }, [fetchConversation]);

  const handleSend = async () => {
    if (!token || !newMessage.trim()) return;
    try {
      // Send the new message via API (or use WebSocket if available)
      const response = await axios.post(
        `/messenger/conversations/${conversationId}/send/`,
        { content: newMessage.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Update the conversation with the new message
      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
      // Optionally, send a WebSocket event:
      // sendWSMessage({ conversationId, message: response.data });
    } catch (err) {
      console.error('Error sending message', err);
    }
  };

  return (
    <div>
      <h5>Chat with {friendName}</h5>
      <div
        style={{
          maxHeight: '400px',
          overflowY: 'auto',
          border: '1px solid #ccc',
          padding: '10px',
          marginBottom: '1rem',
        }}
      >
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
            <div key={msg.id} className="mb-2">
              <strong>{msg.sender.username}:</strong> {msg.content}
              <br />
              <small className="text-muted">
                {new Date(msg.created_at).toLocaleString()}
              </small>
            </div>
          ))
        )}
      </div>
      <Form onSubmit={(e) => { e.preventDefault(); handleSend(); }}>
        <Form.Control
          type="text"
          placeholder="Type your message..."
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <Button variant="primary" type="submit" className="mt-2">
          Send
        </Button>
      </Form>
    </div>
  );
};

export default ChatWindow;
