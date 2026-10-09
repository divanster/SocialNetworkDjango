import React, { useEffect, useMemo, useState } from 'react';
import { fetchUsers } from '../../services/api';
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';
import { useAuth } from '../../contexts/AuthContext';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';

interface User {
  id: string;
  username: string;
}

const Contacts: React.FC = () => {
  const { onlineUsers, userDetails } = useOnlineStatus();
  const { user: currentUser } = useAuth();
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    fetchUsers()
      .then((users) => {
        if (!mounted) return;
        setAllUsers(
          users.map((u: any) => ({
            id: String(u.id),
            username: u.username,
          }))
        );
      })
      .catch((err) => {
        console.error('Contacts.fetchUsers error', err);
        if (mounted) setError('Failed to load contacts.');
      })
      .finally(() => mounted && setLoading(false));

    return () => {
      mounted = false;
    };
  }, []);

  const visibleUsers = useMemo(
    () => allUsers.filter((u) => u.id !== currentUser?.id),
    [allUsers, currentUser?.id]
  );

  if (loading) return <div className="card-section contacts-card">Loading contacts...</div>;
  if (error) return <div className="card-section contacts-card text-danger">{error}</div>;
  if (!visibleUsers.length) return null;

  return (
    <div className="card-section contacts-card">
      <h5 className="section-title">Contacts</h5>
      <ul className="contacts-list">
        {visibleUsers.map((u) => {
          const isOnline = onlineUsers.includes(u.id);
          const displayName = userDetails[u.id] || u.username;
          return (
            <li key={u.id}>
              <UserIdentityLink
                userId={u.id}
                className="contact-item"
                ariaLabel={`Open ${displayName} profile`}
              >
                <Avatar
                  size={34}
                  name={displayName}
                  alt={`${displayName} avatar`}
                  showOnline={isOnline}
                />
                <span className="contact-name">{displayName}</span>
              </UserIdentityLink>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Contacts;
