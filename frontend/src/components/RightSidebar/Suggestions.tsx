// frontend/src/components/RightSidebar/Suggestions.tsx

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import './Suggestions.css';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';

interface SuggestedUser {
  id: string;
  username: string;
  full_name: string;
  profile_picture: string | null;
  mutual_friends_count: number;
}

const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1').replace(/\/+$/, '');

const Suggestions: React.FC = () => {
  const { token } = useAuth();
  const [suggestedUsers, setSuggestedUsers] = useState<SuggestedUser[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [friendRequestsSent, setFriendRequestsSent] = useState<string[]>([]);

  useEffect(() => {
    const fetchSuggestions = async () => {
      if (!token) {
        setSuggestedUsers([]);
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get(`${API_URL}/users/suggestions/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setSuggestedUsers(Array.isArray(response.data) ? response.data : []);
        setError(null);
      } catch (err: any) {
        console.error('Failed to fetch user suggestions:', err);
        setError('Failed to load suggestions.');
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [token]);

  const sendFriendRequest = async (userId: string) => {
    try {
      await axios.post(
        `${API_URL}/friends/friend-requests/`,
        { receiver_id: userId },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      setFriendRequestsSent((prev) => [...prev, userId]);
      setToast({ show: true, message: 'Friend request sent!', variant: 'success' });
    } catch (error) {
      console.error('Error sending friend request:', error);
      setToast({ show: true, message: 'Failed to send friend request.', variant: 'danger' });
    }
  };

  // Toast state
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
              onClick={() => sendFriendRequest(user.id)}
              disabled={friendRequestsSent.includes(user.id)}
              className="friend-request-button"
            >
              {friendRequestsSent.includes(user.id) ? 'Request Sent' : 'Add Friend'}
            </button>
          </li>
        ))}
      </ul>

      {/* Toast Notifications */}
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
