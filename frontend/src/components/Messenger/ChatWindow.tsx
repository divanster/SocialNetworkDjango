import React, { useEffect, useState, useCallback, FormEvent } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import {
  sendMessageToUser,
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

  // 1) Memoize the incoming‐message handler so the socket doesn't reconnect on each keystroke
  const handleSocketMessage = useCallback((data: any) => {
    if (data.message && user) {
      const incoming: MessageType = data.message;
      const isRelevant =
        (incoming.sender.id === friendId && incoming.receiver.id === user.id) ||
        (incoming.sender.id === user.id && incoming.receiver.id === friendId);
      if (!isRelevant) return;

      setMessages((prev) => {
        // dedupe
        if (prev.find(m => m.id === incoming.id)) return prev;
        return [...prev, incoming];
      });
    }
  }, [friendId, user]);

  // 2) Open a single WS to the 'messenger' group, wire up our handler
  const { sendMessage: sendWSMessage } = useWebSocket<MessageType>(
    'messenger',
    { onMessage: handleSocketMessage }
  );

  // 3) Fetch history once
  useEffect(() => {
    if (!token || !user) return;
    (async () => {
      setLoading(true);
      try {
        const res = await axios.get('/messenger/inbox/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const all: MessageType[] = Array.isArray(res.data.results)
          ? res.data.results.map(transformMessage)
          : res.data;
        setMessages(
          all.filter(m =>
            (m.sender.id === friendId && m.receiver.id === user.id) ||
            (m.sender.id === user.id && m.receiver.id === friendId)
          )
        );
        setError(null);
      } catch (e) {
        console.error(e);
        setError('Failed to load conversation.');
      } finally {
        setLoading(false);
      }
    })();
  }, [token, friendId, user]);

  // 4) On send: POST → local state → WS broadcast
  const handleSend = async (e: FormEvent) => {
    e.preventDefault();
    if (!token || !user || !newMessage.trim()) return;
    try {
      let sent: MessageType;
      if (friendId === 'all') {
        const allMsgs = await broadcastMessageToAll(newMessage.trim());
        sent = allMsgs[allMsgs.length - 1];
      } else {
        sent = await sendMessageToUser(friendId, newMessage.trim());
      }

      // update UI right away
      setMessages(prev => [...prev, sent]);
      setNewMessage('');

      // broadcast over WS so peer sees it instantly
      sendWSMessage(JSON.stringify({ message: sent }));
    } catch (e) {
      console.error(e);
      setError('Error sending message');
    }
  };

  if (!user) return <div>Loading user data…</div>;

  return (
    <div className="chat-window">
      <div className="chat-header">
        <h5>Chat with {friendName}</h5>
      </div>
      <div
        className="chat-messages"
        style={{ maxHeight: 400, overflowY: 'auto', padding: '1rem' }}
      >
        {loading ? (
          <div className="text-center"><Spinner animation="border" size="sm" /></div>
        ) : error ? (
          <Alert variant="danger">{error}</Alert>
        ) : messages.length === 0 ? (
          <div>No messages yet.</div>
        ) : (
          messages.map(msg => (
            <div key={msg.id} className="message-item mb-2">
              <strong>{msg.sender.id === user.id ? 'You' : friendName}:</strong> {msg.content}
              <br/>
              <small className="text-muted">
                {new Date(msg.created_at).toLocaleTimeString()}
              </small>
            </div>
          ))
        )}
      </div>
      <div className="chat-input">
        <Form onSubmit={handleSend} className="d-flex">
          <Form.Control
            type="text"
            placeholder="Type your message…"
            value={newMessage}
            onChange={e => setNewMessage(e.target.value)}
          />
          <Button type="submit" className="ms-2">Send</Button>
        </Form>
      </div>
    </div>
  );
};

export default ChatWindow;
