// frontend/src/components/Messenger/ContactsSidebar.tsx
import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Alert, Form, Button } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import { useAuth } from '../../contexts/AuthContext';
import UserIdentityLink from '../Common/UserIdentityLink';
import './ContactsSidebar.css';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
  selectedFriendId?: string | null;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend, selectedFriendId }) => {
  const { user } = useAuth();
  const [friends, setFriends] = useState<User[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { onlineUsers } = useOnlineStatus();

  const loadFriends = async () => {
    if (!user) {
      setLoading(false);
      return;
    }
    setLoading(true);
    try {
      const data = await fetchFriendsList(user.id);
      setFriends(Array.isArray(data) ? data : []);
      setError(null);
    } catch {
      setError('Failed to load contacts.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFriends();
  }, [user]);

  const filteredFriends = friends.filter((friend) => {
    if (!query.trim()) return true;
    const value = query.trim().toLowerCase();
    return (
      friend.username.toLowerCase().includes(value) ||
      (friend.full_name || '').toLowerCase().includes(value)
    );
  });

  if (loading) {
    return (
      <div className="contacts-sidebar-loading text-center">
        <Spinner animation="border" size="sm" /> Loading...
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="danger" className="mb-0">
        <div className="d-flex justify-content-between align-items-center">
          <span>{error}</span>
          <Button size="sm" variant="outline-danger" onClick={loadFriends}>
            Retry
          </Button>
        </div>
      </Alert>
    );
  }

  return (
    <>
      <Form.Group className="mb-2" controlId="messenger-contact-search">
        <Form.Control
          type="search"
          placeholder="Search contacts"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          aria-label="Search contacts"
        />
      </Form.Group>
      <ListGroup className="contacts-sidebar">
      {filteredFriends.map((friend) => {
        const isOnline = onlineUsers.includes(friend.id);
        const displayName = friend.full_name || friend.username;
        return (
          <ListGroup.Item
            key={friend.id}
            action
            type="button"
            onClick={() => onSelectFriend(friend)}
            active={selectedFriendId === friend.id}
            aria-label={`Open conversation with ${displayName}`}
          >
            <div className="contact-item d-flex align-items-center">
              <UserIdentityLink
                userId={friend.id}
                className="d-inline-flex align-items-center"
                ariaLabel={`Open ${displayName} profile`}
                onClick={(event) => event.stopPropagation()}
              >
                {friend.profile_picture ? (
                  <img
                    src={friend.profile_picture}
                    alt={`${displayName} avatar`}
                    className="contact-avatar"
                  />
                ) : (
                  <div className="contact-avatar placeholder" aria-hidden="true">?</div>
                )}
              </UserIdentityLink>
              <div className="contact-name ms-2">
                {displayName}
                <span
                  className={isOnline ? 'online-indicator' : 'offline-indicator'}
                  aria-label={isOnline ? `${displayName} is online` : `${displayName} is offline`}
                >
                  {isOnline ? 'Online' : 'Offline'}
                </span>
              </div>
            </div>
          </ListGroup.Item>
        );
      })}
      {filteredFriends.length === 0 && (
        <ListGroup.Item className="text-muted">No matching contacts.</ListGroup.Item>
      )}
    </ListGroup>
    </>
  );
};

export default ContactsSidebar;
