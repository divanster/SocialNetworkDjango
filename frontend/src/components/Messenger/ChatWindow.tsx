import React, { useEffect, useState, useCallback, FormEvent } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import {
  sendMessageToUser,
  fetchInboxMessages,
  broadcastMessageToAll,
  Message as MessageType,
  transformMessage
} from '../../services/messagesService';
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

  // Memoize onMessage callback so that the WebSocket hook doesn't reinitialize on every keystroke.
  const handleSocketMessage = useCallback((data: any) => {
    // Expect data as { "message": { ... } }
    if (data.message && user) {
      const incomingMsg: MessageType = data.message;
      // Only process if the message is for this conversation
      if (
        (incomingMsg.sender.id === friendId && incomingMsg.receiver.id === user.id) ||
        (incomingMsg.sender.id === user.id && incomingMsg.receiver.id === friendId)
      ) {
        setMessages((prev) => [...prev, incomingMsg]);
      }
    }
  }, [friendId, user]);

  // Use the WebSocket hook for the "messenger" group.
  // This hook connects using the provided token and group name.
  const { sendMessage: sendWSMessage } = useWebSocket<MessageType>(
    'messenger',
    { onMessage: handleSocketMessage }
  );

  // Fetch past conversation via REST when the component mounts
  const fetchConversation = useCallback(async () => {
    if (!token || !user) return;
    setLoading(true);
    try {
      const response = await axios.get('/messenger/inbox/', {
        headers: { Authorization: `Bearer ${token}` },
      });
      let allMessages: MessageType[] = Array.isArray(response.data.results)
        ? response.data.results.map(transformMessage)
        : response.data;
      // Filter messages for the current conversation (1-on-1)
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

  // Handle sending a message via REST and then broadcasting it via WebSocket.
  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!token || !user || !newMessage.trim()) return;
    try {
      let sentMsg: MessageType;
      if (friendId === 'all') {
        const broadcastedMessages = await broadcastMessageToAll(newMessage.trim());
        sentMsg = broadcastedMessages[broadcastedMessages.length - 1];
      } else {
        sentMsg = await sendMessageToUser(friendId, newMessage.trim());
      }
      // Update the UI with the new message immediately.
      setMessages((prev) => [...prev, sentMsg]);
      setNewMessage('');

      // Broadcast the new message via WebSocket.
      // Note that we are stringifying the payload into the expected format.
      sendWSMessage(JSON.stringify({ message: sentMsg }));
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
