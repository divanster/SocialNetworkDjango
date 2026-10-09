import React, { useCallback, useEffect, useMemo, useRef, useState, FormEvent } from 'react';
import { Button, Form, Spinner, Alert } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import useWebSocket from '../../hooks/useWebSocket';
import {
  fetchMessages,
  markMessageAsRead,
  Message as MessageType,
  sendMessageToUser,
  transformMessage,
} from '../../services/messagesService';
import UserIdentityLink from '../Common/UserIdentityLink';
import Avatar from '../Common/Avatar';
import './ChatWindow.css';

interface ChatWindowProps {
  friendId: string;
  friendName: string;
  friendProfilePicture?: string | null;
}

const sortByCreatedAt = (items: MessageType[]): MessageType[] =>
  [...items].sort((left, right) => new Date(left.created_at).getTime() - new Date(right.created_at).getTime());

const ChatWindow: React.FC<ChatWindowProps> = ({ friendId, friendName, friendProfilePicture }) => {
  const { user } = useAuth();
  const { onlineUsers } = useOnlineStatus();
  const [messages, setMessages] = useState<MessageType[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [sending, setSending] = useState<boolean>(false);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const shouldStickToBottomRef = useRef(true);

  const isFriendOnline = onlineUsers.includes(friendId);

  const mergeMessages = useCallback((previous: MessageType[], incoming: MessageType[]) => {
    const byId = new Map<string, MessageType>();
    [...previous, ...incoming].forEach((item) => {
      byId.set(item.id, item);
    });
    return sortByCreatedAt(Array.from(byId.values()));
  }, []);

  const shouldAutoScroll = useCallback(() => {
    const node = messagesContainerRef.current;
    if (!node) return true;
    const distanceFromBottom = node.scrollHeight - node.scrollTop - node.clientHeight;
    return distanceFromBottom < 48;
  }, []);

  const scrollToBottom = useCallback(() => {
    const node = messagesContainerRef.current;
    if (!node) return;
    node.scrollTop = node.scrollHeight;
  }, []);

  const markIncomingAsRead = useCallback(async (incoming: MessageType[]) => {
    if (!user) return;
    const unreadIncoming = incoming.filter(
      (item) => item.receiver.id === user.id && item.sender.id === friendId && !item.read
    );
    if (unreadIncoming.length === 0) return;
    await Promise.allSettled(unreadIncoming.map((item) => markMessageAsRead(item.id)));
  }, [friendId, user]);

  const fetchConversation = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const allMessages = await fetchMessages();
      const conversation = allMessages.filter((msg) => (
        (msg.sender.id === friendId && msg.receiver.id === user.id) ||
        (msg.sender.id === user.id && msg.receiver.id === friendId)
      ));
      const deduped = mergeMessages([], conversation);
      setMessages(deduped);
      await markIncomingAsRead(deduped);
    } catch {
      setError('Failed to load conversation.');
    } finally {
      setLoading(false);
    }
  }, [friendId, markIncomingAsRead, mergeMessages, user]);

  const handleSocketMessage = useCallback((payload: any) => {
    if (!user) return;
    const eventType = payload?.type;
    const raw = eventType === 'messenger.message' ? payload?.data : payload?.data;
    if (!raw || !raw.id) return;
    const incomingMsg: MessageType = typeof raw.sender === 'string' ? transformMessage(raw) : raw;
    if (!incomingMsg.sender || !incomingMsg.receiver) return;
    const isInConversation = (
      (incomingMsg.sender.id === friendId && incomingMsg.receiver.id === user.id) ||
      (incomingMsg.sender.id === user.id && incomingMsg.receiver.id === friendId)
    );
    if (!isInConversation) return;
    shouldStickToBottomRef.current = shouldAutoScroll();
    setMessages((prev) => mergeMessages(prev, [incomingMsg]));
    if (incomingMsg.receiver.id === user.id && !incomingMsg.read) {
      markMessageAsRead(incomingMsg.id).catch(() => undefined);
    }
  }, [friendId, mergeMessages, shouldAutoScroll, user]);

  useWebSocket('messenger', { onMessage: handleSocketMessage });

  useEffect(() => {
    fetchConversation();
  }, [fetchConversation]);

  useEffect(() => {
    if (shouldStickToBottomRef.current) {
      scrollToBottom();
    }
  }, [messages, scrollToBottom]);

  const handleSend = async (event: FormEvent) => {
    event.preventDefault();
    if (!user) return;
    if (!newMessage.trim() || sending) return;
    setSending(true);
    setError(null);
    shouldStickToBottomRef.current = true;
    try {
      const sentMessage = await sendMessageToUser(friendId, newMessage.trim());
      setMessages((prev) => mergeMessages(prev, [sentMessage]));
      setNewMessage('');
    } catch {
      setError('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  const emptyMessageDisabled = useMemo(
    () => sending || newMessage.trim().length === 0,
    [newMessage, sending]
  );

  return (
    <div className="chat-window">
      <div className="chat-header d-flex align-items-center justify-content-between">
        <h5 className="mb-0 d-flex align-items-center gap-2">
          <Avatar
            size={32}
            src={friendProfilePicture || undefined}
            name={friendName}
            alt={`${friendName} avatar`}
            showOnline={isFriendOnline}
          />
          <UserIdentityLink userId={friendId}>{friendName}</UserIdentityLink>
        </h5>
        <span
          className={isFriendOnline ? 'online-indicator' : 'offline-indicator'}
          aria-live="polite"
        >
          {isFriendOnline ? 'Online' : 'Offline'}
        </span>
      </div>

      <div
        className="chat-messages"
        ref={messagesContainerRef}
        onScroll={() => {
          shouldStickToBottomRef.current = shouldAutoScroll();
        }}
      >
        {loading ? (
          <div className="text-center py-3" role="status" aria-live="polite">
            <Spinner animation="border" size="sm" className="me-2" />
            Loading messages...
          </div>
        ) : (
          <>
            {error && (
              <Alert variant="danger" className="mb-2 d-flex justify-content-between align-items-center">
                <span>{error}</span>
                <Button size="sm" variant="outline-danger" onClick={fetchConversation}>
                  Retry
                </Button>
              </Alert>
            )}
            {messages.length === 0 && <div className="text-muted">No messages yet. Say hello.</div>}
            {messages.map((msg) => {
              const mine = msg.sender.id === user?.id;
              return (
                <div
                  key={msg.id}
                  className={`message-item mb-2 ${mine ? 'message-mine' : 'message-theirs'}`}
                >
                  <div className="message-bubble">
                    <div>{msg.content}</div>
                    <small className="text-muted">{new Date(msg.created_at).toLocaleTimeString()}</small>
                  </div>
                </div>
              );
            })}
          </>
        )}
      </div>

      <div className="chat-input">
        <Form onSubmit={handleSend} className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder={`Message ${friendName}`}
            value={newMessage}
            onChange={(event) => setNewMessage(event.target.value)}
            aria-label="Message text"
          />
          <Button variant="primary" type="submit" disabled={emptyMessageDisabled}>
            {sending ? 'Sending...' : 'Send'}
          </Button>
        </Form>
      </div>
    </div>
  );
};

export default ChatWindow;
