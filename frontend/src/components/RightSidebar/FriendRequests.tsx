import React, { useEffect, useMemo, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import { acceptFriendRequest, fetchFriendRequests, rejectFriendRequest } from '../../services/socialGraphService';
import { emitSocialGraphUpdated, subscribeSocialGraphUpdated } from '../../utils/socialGraphEvents';

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

const FriendRequests: React.FC = () => {
  const { token, user } = useAuth();
  const [requests, setRequests] = useState<FriendRequestItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoadingById, setActionLoadingById] = useState<Record<string, boolean>>({});

  const loadRequests = async () => {
    if (!token || !user?.id) {
      setRequests([]);
      setLoading(false);
      return;
    }
    setLoading(true);

    try {
      const items = await fetchFriendRequests();
      setRequests(items);
      setError(null);
    } catch (err) {
      setError('Failed to load friend requests.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();

    const unsubscribe = subscribeSocialGraphUpdated(() => {
      loadRequests();
    });

    return () => {
      unsubscribe();
    };
  }, [token, user?.id]);

  const handleRequestAction = async (requestId: string, action: 'accept' | 'reject') => {
    if (!token) return;
    setActionLoadingById((prev) => ({ ...prev, [requestId]: true }));
    try {
      if (action === 'accept') {
        await acceptFriendRequest(requestId);
      } else {
        await rejectFriendRequest(requestId);
      }
      setRequests((prev) => prev.filter((item) => item.id !== requestId));
      emitSocialGraphUpdated();
      setError(null);
    } catch (err) {
      setError(`Failed to ${action} friend request.`);
    } finally {
      setActionLoadingById((prev) => ({ ...prev, [requestId]: false }));
    }
  };

  const incomingRequests = useMemo(
    () => requests.filter((item) => item.status === 'pending' && item.receiver?.id === user?.id),
    [requests, user?.id]
  );

  if (loading) return <div className="card-section">Loading friend requests...</div>;
  if (error) return <div className="card-section text-danger">{error}</div>;
  if (!incomingRequests.length) return null;

  return (
    <div className="card-section">
      <h5 className="section-title">Friend Requests</h5>
      <ul className="contacts-list">
        {incomingRequests.map((request) => {
          const displayName = request.sender.full_name || request.sender.username;
          const busy = Boolean(actionLoadingById[request.id]);
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
                  disabled={busy}
                >
                  {busy ? 'Working...' : 'Accept'}
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => handleRequestAction(request.id, 'reject')}
                  disabled={busy}
                >
                  {busy ? 'Working...' : 'Reject'}
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
