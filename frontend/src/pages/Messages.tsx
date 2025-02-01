// src/pages/Messages.tsx

import React, { useEffect, useState } from 'react';
import { fetchInboxMessages } from '../services/messagesService';
import { Card, Button, Spinner, Alert } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';

interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

interface Message {
  id: string;
  sender: User;
  receiver: User;
  content: string;
  read: boolean;
  created_at: string;
}

const Messages: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchMessagesAsync = async () => {
      setLoading(true);
      try {
        const data = await fetchInboxMessages();
        setMessages(data);
        setError(null);
      } catch (err: any) {
        console.error('Error fetching messages:', err);
        setError(err.message || 'Failed to fetch messages.');
      } finally {
        setLoading(false);
      }
    };

    fetchMessagesAsync();
  }, []);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading messages...</span>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;
  }

  return (
    <div className="container mt-5">
      <h2>Inbox</h2>
      {messages.length === 0 ? (
        <p>No messages found.</p>
      ) : (
        messages.map((msg) => (
          <Card key={msg.id} className="mb-3">
            <Card.Body>
              <Card.Title>
                {msg.sender.full_name} ({msg.sender.username})
              </Card.Title>
              <Card.Text>
                {msg.content}
              </Card.Text>
              <Button variant="primary" onClick={() => navigate(`/messages/${msg.id}`)}>
                View Message
              </Button>
            </Card.Body>
          </Card>
        ))
      )}
    </div>
  );
};

export default Messages;
