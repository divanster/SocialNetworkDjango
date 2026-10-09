// frontend/src/components/Messenger/ContactsSidebar.tsx
import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Alert } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import { useAuth } from '../../contexts/AuthContext';  // <-- import where you get the logged-in user
import UserIdentityLink from '../Common/UserIdentityLink';
import './ContactsSidebar.css';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
  selectedFriendId?: string | null;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend, selectedFriendId }) => {
  const { user } = useAuth();      // <-- get current logged-in user from context
  const [friends, setFriends] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { onlineUsers } = useOnlineStatus(); // onlineUsers is an array of user IDs that are online

  useEffect(() => {
    const loadFriends = async () => {
      // If user is not yet loaded, skip
      if (!user) {
        setLoading(false);
        return;
      }
      try {
        // Pass the *current user’s ID* to fetchFriendsList:
        const data = await fetchFriendsList(user.id);
        setFriends(Array.isArray(data) ? data : []);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch friends:', err);
        setError('Failed to load friends.');
      } finally {
        setLoading(false);
      }
    };

    loadFriends();
  }, [user]);

  if (loading) {
    return (
      <div className="contacts-sidebar-loading text-center">
        <Spinner animation="border" size="sm" /> Loading...
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  return (
    <ListGroup className="contacts-sidebar">
      {friends.map((friend) => {
        const isOnline = onlineUsers.includes(friend.id);
        const displayName = friend.full_name || friend.username;
        return (
          <ListGroup.Item
            key={friend.id}
            action
            onClick={() => onSelectFriend(friend)}
            active={selectedFriendId === friend.id}
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
                {isOnline && <span className="online-indicator"> ●</span>}
              </div>
            </div>
          </ListGroup.Item>
        );
      })}
    </ListGroup>
  );
};

export default ContactsSidebar;
