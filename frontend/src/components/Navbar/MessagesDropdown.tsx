import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { NavDropdown, Badge, Spinner } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import useWebSocket from '../../hooks/useWebSocket';
import {
  fetchInboxMessages,
  markMessageAsRead,
  Message,
  transformMessage,
} from '../../services/messagesService';
import UserIdentityLink from '../Common/UserIdentityLink';
import { buildMessengerPathForUser } from '../../utils/profileRoutes';
import './MessagesDropdown.css';

interface MessagesDropdownProps {
  unreadCount: number;
  setUnreadCount: React.Dispatch<React.SetStateAction<number>>;
}

interface ConversationPreview {
  partnerId: string;
  partnerName: string;
  partnerAvatar?: string | null;
  latestMessage: Message;
  unread: boolean;
}

const MessagesDropdown: React.FC<MessagesDropdownProps> = ({ unreadCount, setUnreadCount }) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const mergeById = useCallback((items: Message[]) => {
    const map = new Map<string, Message>();
    items.forEach((item) => map.set(item.id, item));
    return Array.from(map.values()).sort(
      (left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()
    );
  }, []);

  const refreshMessages = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const fetched = await fetchInboxMessages();
      const deduped = mergeById(fetched);
      setMessages(deduped);
      setUnreadCount(deduped.filter((msg) => !msg.read).length);
    } catch {
      setError('Failed to load messages.');
    } finally {
      setLoading(false);
    }
  }, [mergeById, setUnreadCount]);

  useEffect(() => {
    refreshMessages();
  }, [refreshMessages]);

  useWebSocket<any>('messenger', {
    onMessage: (payload) => {
      const raw = payload?.type === 'messenger.message' ? payload.data : payload?.data;
      if (!raw || !raw.id) return;
      const incoming = typeof raw.sender === 'string' ? transformMessage(raw) : (raw as Message);
      setMessages((prev) => {
        const merged = mergeById([incoming, ...prev]);
        setUnreadCount(merged.filter((item) => !item.read).length);
        return merged;
      });
    },
  });

  const previews = useMemo<ConversationPreview[]>(() => {
    if (!user) return [];
    const byPartnerId = new Map<string, ConversationPreview>();
    messages.forEach((message) => {
      const partner = message.sender.id === user.id ? message.receiver : message.sender;
      if (!partner?.id || partner.id === user.id) return;
      const existing = byPartnerId.get(partner.id);
      if (!existing || new Date(message.created_at).getTime() > new Date(existing.latestMessage.created_at).getTime()) {
        byPartnerId.set(partner.id, {
          partnerId: partner.id,
          partnerName: partner.full_name || partner.username || 'Unknown user',
          partnerAvatar: partner.profile_picture,
          latestMessage: message,
          unread: !message.read && message.receiver.id === user.id,
        });
      } else if (!existing.unread && !message.read && message.receiver.id === user.id) {
        existing.unread = true;
      }
    });

    return Array.from(byPartnerId.values()).sort(
      (left, right) => new Date(right.latestMessage.created_at).getTime() - new Date(left.latestMessage.created_at).getTime()
    );
  }, [messages, user]);

  const handleMarkAsRead = async (messageId: string) => {
    try {
      await markMessageAsRead(messageId);
      setMessages((prev) => {
        const updated = prev.map((message) => (message.id === messageId ? { ...message, read: true } : message));
        setUnreadCount(updated.filter((item) => !item.read).length);
        return updated;
      });
    } catch {
      setError('Failed to mark message as read.');
    }
  };

  return (
    <NavDropdown
      title={
        <>
          Messages {unreadCount > 0 && <Badge bg="danger">{unreadCount}</Badge>}
        </>
      }
      id="messages-dropdown"
      align="end"
      className="messages-dropdown"
    >
      <NavDropdown.Header className="d-flex justify-content-between align-items-center">
        <span>Recent messages</span>
        <Link to="/messenger" className="btn btn-link btn-sm">
          View all messages
        </Link>
      </NavDropdown.Header>
      <NavDropdown.Divider />
      {loading ? (
        <NavDropdown.ItemText role="status" aria-live="polite">
          <Spinner animation="border" size="sm" className="me-2" /> Loading...
        </NavDropdown.ItemText>
      ) : error ? (
        <NavDropdown.ItemText className="text-danger">{error}</NavDropdown.ItemText>
      ) : previews.length === 0 ? (
        <NavDropdown.ItemText>No messages yet.</NavDropdown.ItemText>
      ) : (
        previews.slice(0, 8).map((preview) => (
          <NavDropdown.ItemText key={preview.partnerId} className={preview.unread ? 'unread' : 'read'}>
            <div className="message-content">
              <UserIdentityLink
                userId={preview.partnerId}
                className="me-2"
                ariaLabel={`Open ${preview.partnerName} profile`}
              >
                {preview.partnerAvatar ? (
                  <img src={preview.partnerAvatar} alt={`${preview.partnerName} avatar`} className="profile-picture me-2" />
                ) : (
                  <div className="profile-placeholder me-2" aria-hidden="true">?</div>
                )}
              </UserIdentityLink>
              <div>
                <strong>
                  <UserIdentityLink userId={preview.partnerId}>{preview.partnerName}</UserIdentityLink>
                </strong>
                <button
                  type="button"
                  className="message-open-btn text-truncate d-block"
                  style={{ maxWidth: 200 }}
                  onClick={() => {
                    if (preview.unread && preview.latestMessage.receiver.id === user?.id) {
                      handleMarkAsRead(preview.latestMessage.id);
                    }
                    navigate(buildMessengerPathForUser(preview.partnerId));
                  }}
                  aria-label={`Open conversation with ${preview.partnerName}`}
                >
                  {preview.latestMessage.content}
                </button>
                <small className="text-muted">
                  {new Date(preview.latestMessage.created_at).toLocaleString()}
                </small>
                {preview.unread && <small className="d-block fw-semibold">Unread</small>}
              </div>
            </div>
          </NavDropdown.ItemText>
        ))
      )}
    </NavDropdown>
  );
};

export default MessagesDropdown;
