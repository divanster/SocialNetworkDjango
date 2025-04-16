// frontend/src/components/Messenger/ContactsSidebar.tsx
import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Alert } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import { useAuth } from '../../contexts/AuthContext';  // <-- import where you get the logged-in user
import './ContactsSidebar.css';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend }) => {
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
        return (
          <ListGroup.Item
            key={friend.id}
            action
            onClick={() => onSelectFriend(friend)}
          >
            <div className="contact-item d-flex align-items-center">
              {friend.profile_picture ? (
                <img
                  src={friend.profile_picture}
                  alt={friend.username}
                  className="contact-avatar"
                />
              ) : (
                <div className="contact-avatar placeholder">?</div>
              )}
              <div className="contact-name ms-2">
                {friend.full_name || friend.username}
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
