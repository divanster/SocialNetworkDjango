// frontend/src/components/Messenger/ContactsSidebar.tsx
import React, { useEffect, useState } from 'react';
import { ListGroup, Spinner, Badge } from 'react-bootstrap';
import { fetchFriendsList, User } from '../../services/friendsService';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import { useAuth } from '../../contexts/AuthContext';

interface ContactsSidebarProps {
  onSelectFriend: (friend: User) => void;
}

const ContactsSidebar: React.FC<ContactsSidebarProps> = ({ onSelectFriend }) => {
  const [friends, setFriends] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const { onlineUsers } = useOnlineStatus();
  const { user } = useAuth(); // Get the current user

  useEffect(() => {
    const getFriends = async () => {
      if (!user) {
        setError('User not authenticated');
        setLoading(false);
        return;
      }
      try {
        const data = await fetchFriendsList(String(user.id));  // Convert number to string here
        setFriends(data);
        setError(null);
      } catch (err: any) {
        setError('Failed to fetch friends.');
      } finally {
        setLoading(false);
      }
    };

  getFriends();
}, [user]);


  if (loading) {
    return (
      <div className="text-center">
        <Spinner animation="border" size="sm" /> Loading friends...
      </div>
    );
  }

  if (error) {
    return <div className="text-danger">{error}</div>;
  }

  return (
    <ListGroup variant="flush">
      {friends.map((friend) => {
        const isOnline = onlineUsers.includes(friend.id);
        return (
          <ListGroup.Item
            key={friend.id}
            action
            onClick={() => onSelectFriend(friend)}
            className="d-flex justify-content-between align-items-center"
          >
            <div>
              {friend.full_name} ({friend.username})
            </div>
            {isOnline ? (
              <Badge bg="success">Online</Badge>
            ) : (
              <Badge bg="secondary">Offline</Badge>
            )}
          </ListGroup.Item>
        );
      })}
    </ListGroup>
  );
};

export default ContactsSidebar;
