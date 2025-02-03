// frontend/src/pages/Messages.tsx

import React, { useEffect, useState } from 'react';
import { Spinner, Alert } from 'react-bootstrap';
import { fetchInboxMessages, Message } from '../services/messagesService';
import { useAuth } from '../contexts/AuthContext';

const Messages: React.FC = () => {
  const { token } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadMessages = async () => {
      if (!token) {
        setError('Not authenticated');
        setLoading(false);
        return;
      }
      try {
        const data = await fetchInboxMessages();
        setMessages(data);
      } catch (err) {
        console.error('Error fetching messages:', err);
        setError('Failed to fetch messages.');
      } finally {
        setLoading(false);
      }
    };
    loadMessages();
  }, [token]);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" />
        <span className="ms-2">Loading messages...</span>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;
  }

  return (
    <div className="container mt-5">
      <h2>Inbox Messages</h2>
      {messages.length === 0 ? (
        <Alert variant="info">No messages found.</Alert>
      ) : (
        messages.map((msg) => (
          <div key={msg.id} className="mb-3 p-2 border rounded">
            <strong>From: {msg.sender.full_name}</strong>
            <p>{msg.content}</p>
            <small>{new Date(msg.created_at).toLocaleString()}</small>
          </div>
        ))
      )}
    </div>
  );
};

export default Messages;
