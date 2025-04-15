// frontend/src/components/Messenger/ContactsSidebar.tsx
import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Alert } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import './ContactsSidebar.css';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend }) => {
  const [friends, setFriends] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { onlineUsers } = useOnlineStatus(); // onlineUsers is an array of string IDs

  useEffect(() => {
    const loadFriends = async () => {
      try {
        // Replace "currentUserId" with the actual current user's id if available.
        const data = await fetchFriendsList("currentUserId");
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
  }, []);

  if (loading) {
    return (
      <div className="contacts-sidebar-loading text-center">
        <Spinner animation="border" size="sm" /> Loading...
      </div>
    );
  }
  if (error) return <Alert variant="danger">{error}</Alert>;

  return (
    <ListGroup className="contacts-sidebar">
      {friends.map((friend) => {
        const isOnline = onlineUsers.includes(friend.id);
        return (
          <ListGroup.Item key={friend.id} action onClick={() => onSelectFriend(friend)}>
            <div className="contact-item d-flex align-items-center">
              {friend.profile_picture ? (
                <img src={friend.profile_picture} alt={friend.username} className="contact-avatar" />
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
