// frontend/src/components/Messages/MessagesList.tsx

import React from 'react';
import { Link } from 'react-router-dom';
import { Button, Alert, Spinner } from 'react-bootstrap';
import './MessagesList.css'; // Create this CSS file as needed

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

interface MessagesListProps {
  messages: Message[];
  isLoading: boolean;
  handleMarkAsRead: (id: string) => void;
}

const MessagesList: React.FC<MessagesListProps> = ({ messages, isLoading, handleMarkAsRead }) => {
  if (isLoading) {
    return (
      <div className="text-center">
        <Spinner animation="border" role="status" />
        <span className="ms-2">Loading messages...</span>
      </div>
    );
  }

  if (messages.length === 0) {
    return <Alert variant="info">No messages to display.</Alert>;
  }

  return (
    <div className="messages-list">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={`message-item d-flex align-items-center p-2 mb-2 ${msg.read ? 'read' : 'unread'}`}
        >
          <div className="profile-picture me-3">
            {msg.sender.profile_picture ? (
              <img
                src={msg.sender.profile_picture}
                alt={`${msg.sender.username}'s profile`}
                className="rounded-circle"
                width="50"
                height="50"
              />
            ) : (
              <div
                className="bg-secondary text-white rounded-circle d-flex align-items-center justify-content-center"
                style={{ width: '50px', height: '50px' }}
              >
                {msg.sender.full_name.charAt(0)}
              </div>
            )}
          </div>
          <div className="message-content flex-grow-1">
            <Link to={`/messages/${msg.id}`} className="message-sender">
              <strong>{msg.sender.full_name}</strong>
            </Link>
            <p className="mb-1">
              {msg.content.substring(0, 50)}
              {msg.content.length > 50 ? '...' : ''}
            </p>
            <small className="text-muted">{new Date(msg.created_at).toLocaleString()}</small>
          </div>
          {!msg.read && (
            <Button variant="outline-success" size="sm" onClick={() => handleMarkAsRead(msg.id)}>
              Mark as Read
            </Button>
          )}
        </div>
      ))}
    </div>
  );
};

export default MessagesList;
