import React, { useMemo, useState } from 'react';
import { Button, Form } from 'react-bootstrap';
import UserIdentityLink from './UserIdentityLink';
import { CompactUser, searchUsers } from '../../services/socialGraphService';

interface UserTagPickerProps {
  selectedUsers: CompactUser[];
  onChange: (users: CompactUser[]) => void;
  label?: string;
}

const UserTagPicker: React.FC<UserTagPickerProps> = ({
  selectedUsers,
  onChange,
  label = 'Tag users',
}) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CompactUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  const selectedMap = useMemo(
    () => new Set(selectedUsers.map((item) => item.id)),
    [selectedUsers]
  );

  const runSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const users = await searchUsers(query.trim());
      setResults(users);
    } catch (err) {
      setError('Could not search users.');
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const addUser = (user: CompactUser) => {
    if (selectedMap.has(user.id)) return;
    onChange([...selectedUsers, user]);
  };

  const removeUser = (id: string) => {
    onChange(selectedUsers.filter((item) => item.id !== id));
  };

  return (
    <div className="user-tag-picker">
      <Form.Label>{label}</Form.Label>
      <Form onSubmit={runSearch} className="d-flex gap-2 mb-2">
        <Form.Control
          aria-label="Search users to tag"
          placeholder="Search users by name"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
        />
        <Button type="submit" variant="outline-primary" disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </Button>
      </Form>
      {error && <div className="text-danger small mb-2">{error}</div>}

      {results.length > 0 && (
        <ul className="list-unstyled mb-2">
          {results.map((user) => (
            <li key={user.id} className="d-flex align-items-center justify-content-between py-1">
              <span>{user.full_name || user.username}</span>
              <Button
                type="button"
                size="sm"
                variant={selectedMap.has(user.id) ? 'secondary' : 'outline-primary'}
                disabled={selectedMap.has(user.id)}
                onClick={() => addUser(user)}
              >
                {selectedMap.has(user.id) ? 'Added' : 'Add'}
              </Button>
            </li>
          ))}
        </ul>
      )}

      {selectedUsers.length > 0 && (
        <ul className="list-unstyled mb-0">
          {selectedUsers.map((user) => (
            <li key={user.id} className="d-flex align-items-center justify-content-between py-1">
              <UserIdentityLink userId={user.id}>{user.full_name || user.username}</UserIdentityLink>
              <Button type="button" size="sm" variant="outline-danger" onClick={() => removeUser(user.id)}>
                Remove
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default UserTagPicker;
