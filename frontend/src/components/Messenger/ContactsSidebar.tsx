import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Alert } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useAuth } from '../../contexts/AuthContext';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import './ContactsSidebar.css';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend }) => {
  const { user } = useAuth();
  const { onlineUsers } = useOnlineStatus();
  const [friends, setFriends] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadFriends = async () => {
      try {
        if (!user) {
          throw new Error("User not authenticated");
        }
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
  if (error) return <Alert variant="danger">{error}</Alert>;

  return (
    <ListGroup className="contacts-sidebar">
      {friends.map((friend) => {
        // Check if friend is online (IDs as strings)
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
