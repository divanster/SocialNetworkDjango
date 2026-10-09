import React, { useEffect, useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import './Suggestions.css';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import { fetchUserSuggestions, sendFriendRequest } from '../../services/socialGraphService';
import { emitSocialGraphUpdated, subscribeSocialGraphUpdated } from '../../utils/socialGraphEvents';

interface SuggestedUser {
  id: string;
  username: string;
  full_name: string;
  profile_picture: string | null;
  mutual_friends_count: number;
}

const Suggestions: React.FC = () => {
  const { token } = useAuth();
  const [suggestedUsers, setSuggestedUsers] = useState<SuggestedUser[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [friendRequestsSent, setFriendRequestsSent] = useState<string[]>([]);
  const [sendingById, setSendingById] = useState<Record<string, boolean>>({});

  const loadSuggestions = async () => {
    if (!token) {
      setSuggestedUsers([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    try {
      const users = await fetchUserSuggestions();
      setSuggestedUsers(Array.isArray(users) ? users : []);
      setError(null);
    } catch (err) {
      setError('Failed to load suggestions.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSuggestions();
    const unsubscribe = subscribeSocialGraphUpdated(() => {
      loadSuggestions();
    });
    return () => {
      unsubscribe();
    };
  }, [token]);

  const handleSendFriendRequest = async (userId: string) => {
    if (sendingById[userId]) return;
    setSendingById((prev) => ({ ...prev, [userId]: true }));
    try {
      await sendFriendRequest(userId);
      setFriendRequestsSent((prev) => [...prev, userId]);
      setToast({ show: true, message: 'Friend request sent!', variant: 'success' });
      emitSocialGraphUpdated();
    } catch (error) {
      setToast({ show: true, message: 'Failed to send friend request.', variant: 'danger' });
    } finally {
      setSendingById((prev) => ({ ...prev, [userId]: false }));
    }
  };

  const [toast, setToast] = useState<{ show: boolean; message: string; variant: string }>({
    show: false,
    message: '',
    variant: 'success',
  });

  if (loading) {
    return <div className="suggestions">Loading suggestions...</div>;
  }

  if (error) {
    return <div className="suggestions error">{error}</div>;
  }

  if (suggestedUsers.length === 0) {
    return <div className="suggestions">No suggestions available.</div>;
  }

  return (
    <div className="suggestions">
      <h4>People You May Know</h4>
      <ul>
        {suggestedUsers.map((user) => (
          <li key={user.id}>
            <UserIdentityLink
              userId={user.id}
              className="suggestion-user-link"
              ariaLabel={`Open ${user.full_name || user.username} profile`}
            >
              <Avatar
                size={40}
                src={user.profile_picture || undefined}
                name={user.full_name || user.username}
                alt={`${user.username} avatar`}
              />
            </UserIdentityLink>
            <div>
              <UserIdentityLink userId={user.id}>
                {user.full_name}
              </UserIdentityLink>
              <span>{user.mutual_friends_count} mutual friends</span>
            </div>
            <button
              onClick={() => handleSendFriendRequest(user.id)}
              disabled={friendRequestsSent.includes(user.id) || Boolean(sendingById[user.id])}
              className="friend-request-button"
            >
              {friendRequestsSent.includes(user.id)
                ? 'Request Sent'
                : sendingById[user.id]
                  ? 'Sending...'
                  : 'Add Friend'}
            </button>
          </li>
        ))}
      </ul>

      <div className="toast-container">
        {toast.show && (
          <div className={`toast ${toast.variant}`} onClick={() => setToast({ ...toast, show: false })}>
            {toast.message}
          </div>
        )}
      </div>
    </div>
  );
};

export default Suggestions;
