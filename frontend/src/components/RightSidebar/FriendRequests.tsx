import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';

interface FriendRequestUser {
  id: string;
  username: string;
  full_name?: string;
  profile_picture?: string | null;
}

interface FriendRequestItem {
  id: string;
  sender: FriendRequestUser;
  receiver: FriendRequestUser;
  status: string;
}

const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1').replace(/\/+$/, '');

const FriendRequests: React.FC = () => {
  const { token, user } = useAuth();
  const [requests, setRequests] = useState<FriendRequestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token || !user?.id) {
      setRequests([]);
      setLoading(false);
      return;
    }

    let mounted = true;
    setLoading(true);

    axios.get(`${API_URL}/friends/friend-requests/`)
      .then((response) => {
        if (!mounted) return;
        const items = response.data?.results || response.data || [];
        setRequests(Array.isArray(items) ? items : []);
        setError(null);
      })
      .catch((err) => {
        console.error('Failed to load friend requests', err);
        if (mounted) setError('Failed to load friend requests.');
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, [token, user?.id]);

  const incomingRequests = useMemo(
    () => requests.filter((item) => item.status === 'pending' && item.receiver?.id === user?.id),
    [requests, user?.id]
  );

  const handleRequestAction = async (requestId: string, action: 'accept' | 'reject') => {
    if (!token) return;
    try {
      await axios.post(`${API_URL}/friends/friend-requests/${requestId}/${action}/`, {});
      setRequests((prev) => prev.filter((item) => item.id !== requestId));
    } catch (err) {
      console.error(`Failed to ${action} friend request`, err);
      setError(`Failed to ${action} friend request.`);
    }
  };

  if (loading) return <div className="card-section">Loading friend requests...</div>;
  if (error) return <div className="card-section text-danger">{error}</div>;
  if (!incomingRequests.length) return null;

  return (
    <div className="card-section">
      <h5 className="section-title">Friend Requests</h5>
      <ul className="contacts-list">
        {incomingRequests.map((request) => {
          const displayName = request.sender.full_name || request.sender.username;
          return (
            <li key={request.id} className="mb-2">
              <div className="d-flex align-items-center gap-2 mb-2">
                <UserIdentityLink
                  userId={request.sender.id}
                  className="d-flex align-items-center gap-2"
                  ariaLabel={`Open ${displayName} profile`}
                >
                  <Avatar
                    size={32}
                    name={displayName}
                    src={request.sender.profile_picture || undefined}
                    alt={`${displayName} avatar`}
                  />
                  <span className="contact-name">{displayName}</span>
                </UserIdentityLink>
              </div>
              <div className="d-flex gap-2">
                <button
                  type="button"
                  className="btn btn-sm btn-primary"
                  onClick={() => handleRequestAction(request.id, 'accept')}
                >
                  Accept
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => handleRequestAction(request.id, 'reject')}
                >
                  Reject
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default FriendRequests;
