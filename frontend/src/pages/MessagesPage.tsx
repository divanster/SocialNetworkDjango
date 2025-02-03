// frontend/src/pages/MessagesPage.tsx

import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { fetchMessageById, markMessageAsRead } from '../services/messagesService';
import { useAuth } from '../contexts/AuthContext';
import { Card, Button, Spinner, Alert } from 'react-bootstrap';

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

const MessagesPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { token } = useAuth();
  const navigate = useNavigate();
  const [message, setMessage] = useState<Message | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [markingRead, setMarkingRead] = useState<boolean>(false);

  useEffect(() => {
    if (id && token) {
      const fetchMessageAsync = async () => {
        setLoading(true);
        try {
          const fetchedMessage: Message = await fetchMessageById(id);
          setMessage(fetchedMessage);
          // If the message is unread, mark it as read
          if (!fetchedMessage.read) {
            setMarkingRead(true);
            await markMessageAsRead(id);
            setMessage({ ...fetchedMessage, read: true });
            setMarkingRead(false);
          }
          setError(null);
        } catch (err: any) {
          console.error('Error fetching message:', err);
          setError(err.message || 'Failed to fetch message.');
        } finally {
          setLoading(false);
        }
      };

      fetchMessageAsync();
    }
  }, [id, token]);

  if (loading) {
    return (
      <div className="text-center mt-5">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading message...</span>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger" className="mt-5 text-center">{error}</Alert>;
  }

  if (!message) {
    return <Alert variant="info" className="mt-5 text-center">No message found.</Alert>;
  }

  return (
    <div className="messages-page container mt-5">
      <Card>
        <Card.Header className="d-flex justify-content-between align-items-center">
          <div className="d-flex align-items-center">
            {message.sender.profile_picture ? (
              <img
                src={message.sender.profile_picture}
                alt={`${message.sender.username}'s profile`}
                className="profile-picture me-2"
                width="50"
                height="50"
              />
            ) : (
              <div
                className="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center me-2"
                style={{ width: '50px', height: '50px' }}
              >
                {message.sender.full_name?.charAt(0) || '?'}
              </div>
            )}
            <strong>{message.sender.full_name || 'Unknown'} ({message.sender.username})</strong>
          </div>
          <span className="text-muted">{new Date(message.created_at).toLocaleString()}</span>
        </Card.Header>
        <Card.Body>
          <Card.Text>{message.content}</Card.Text>
        </Card.Body>
        <Card.Footer>
          <Button variant="secondary" onClick={() => navigate(-1)}>
            Back
          </Button>
        </Card.Footer>
      </Card>
    </div>
  );
};

export default MessagesPage;
