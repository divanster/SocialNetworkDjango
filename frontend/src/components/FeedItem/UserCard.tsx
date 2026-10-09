import React, { useState } from 'react';
import { Alert, Button } from 'react-bootstrap';
import { followUser, sendFriendRequest } from '../../services/socialGraphService';

interface UserCardProps {
  userId: string;
  username: string;
  fullName: string;
  isFriend: boolean;
  isFollowed: boolean;
}

const UserCard: React.FC<UserCardProps> = ({ userId, username, fullName, isFriend, isFollowed }) => {
  const [isSendingRequest, setIsSendingRequest] = useState(false);
  const [isFollowing, setIsFollowing] = useState(isFollowed);
  const [status, setStatus] = useState<{ type: 'success' | 'danger'; message: string } | null>(null);

  const handleSendFriendRequest = async () => {
    if (isSendingRequest) return;
    setIsSendingRequest(true);
    setStatus(null);
    try {
      await sendFriendRequest(userId);
      setStatus({ type: 'success', message: 'Friend request sent.' });
    } catch {
      setStatus({ type: 'danger', message: 'Failed to send request.' });
    } finally {
      setIsSendingRequest(false);
    }
  };

  const handleFollow = async () => {
    if (isFollowing) return;
    setStatus(null);
    try {
      await followUser(userId);
      setIsFollowing(true);
      setStatus({ type: 'success', message: 'User followed.' });
    } catch {
      setStatus({ type: 'danger', message: 'Failed to follow user.' });
    }
  };

  return (
    <div className="user-card">
      <h5>{fullName} ({username})</h5>
      {status && <Alert variant={status.type} className="py-1 px-2 my-2">{status.message}</Alert>}
      {isFriend ? (
        <Button disabled>Already Friends</Button>
      ) : (
        <Button onClick={handleSendFriendRequest} disabled={isSendingRequest}>
          {isSendingRequest ? 'Sending Request...' : 'Send Friend Request'}
        </Button>
      )}
      {!isFollowing ? (
        <Button onClick={handleFollow}>Follow</Button>
      ) : (
        <Button disabled>Following</Button>
      )}
    </div>
  );
};

export default UserCard;
