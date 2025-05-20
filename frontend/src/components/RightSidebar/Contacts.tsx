import React, { useEffect, useState } from 'react';
import { fetchUsers } from '../../services/api';    // your API helper
import { useOnlineStatus } from '../../contexts/OnlineStatusContext';

interface User {
  id: string;
  username: string;
  email: string;
}

const Contacts: React.FC = () => {
  const { onlineUsers } = useOnlineStatus();
  const [allUsers, setAllUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    fetchUsers()
      .then(users => {
        if (!mounted) return;
        setAllUsers(
          users.map((u: any) => ({
            id: String(u.id),
            username: u.username,
            email: u.email,
          }))
        );
      })
      .catch(err => {
        console.error('Contacts.fetchUsers error', err);
        if (mounted) setError('Failed to load contacts.');
      })
      .finally(() => mounted && setLoading(false));

    return () => { mounted = false; };
  }, []);

  if (loading) return <div>Loading contacts…</div>;
  if (error)   return <div className="text-danger">{error}</div>;

  return (
    <div className="contacts">
      <h5>Contacts</h5>
      <ul className="list-unstyled">
        {allUsers.map(u => {
          const isOnline = onlineUsers.includes(u.id);
          return (
            <li key={u.id} className="d-flex align-items-center mb-2">
              <span
                style={{
                  display: 'inline-block',
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: isOnline ? 'green' : 'red',
                  marginRight: 8,
                }}
              />
              <div>
                <div><strong>{u.username}</strong></div>
                <div className="text-muted" style={{ fontSize: '0.85em' }}>
                  {u.email}
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default Contacts;
