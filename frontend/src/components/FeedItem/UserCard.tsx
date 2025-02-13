import React, { useState } from 'react';
import { Button } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface UserCardProps {
  userId: string;
  username: string;
  fullName: string;
  isFriend: boolean;
  isFollowed: boolean;
}

const UserCard: React.FC<UserCardProps> = ({ userId, username, fullName, isFriend, isFollowed }) => {
  const { token } = useAuth();
  const [isSendingRequest, setIsSendingRequest] = useState(false);

  const sendFriendRequest = async () => {
    if (!token) return;
    setIsSendingRequest(true);
    try {
      await axios.post(
        `${API_URL}/friends/friend-requests/`,
        { receiver_id: userId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('Friend request sent!');
    } catch (err) {
      console.error('Error sending friend request:', err);
      alert('Failed to send request.');
    } finally {
      setIsSendingRequest(false);
    }
  };

  const followUser = async () => {
    if (!token) return;
    try {
      await axios.post(
        `${API_URL}/follows/`,
        { user_id: userId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert('User followed!');
    } catch (err) {
      console.error('Error following user:', err);
      alert('Failed to follow user.');
    }
  };

  return (
    <div className="user-card">
      <h5>{fullName} ({username})</h5>
      {isFriend ? (
        <Button disabled>Already Friends</Button>
      ) : (
        <Button onClick={sendFriendRequest} disabled={isSendingRequest}>
          {isSendingRequest ? 'Sending Request...' : 'Send Friend Request'}
        </Button>
      )}
      {!isFollowed ? (
        <Button onClick={followUser}>Follow</Button>
      ) : (
        <Button disabled>Following</Button>
      )}
    </div>
  );
};

export default UserCard;
