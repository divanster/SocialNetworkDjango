import React, { useEffect, useMemo, useState } from 'react';
import { Alert, Button, Card, Col, Container, Form, Row, Spinner } from 'react-bootstrap';
import { useNavigate } from 'react-router-dom';
import Avatar from '../components/Common/Avatar';
import RelationshipActions from '../components/Social/RelationshipActions';
import UserIdentityLink from '../components/Common/UserIdentityLink';
import { useSocialGraph } from '../hooks/useSocialGraph';
import { CompactUser, fetchUserSuggestions, searchUsers } from '../services/socialGraphService';
import { buildMessengerPathForUser } from '../utils/profileRoutes';
import './FriendsPage.css';

interface UserCardProps {
  user: CompactUser;
  subtitle?: string;
  children: React.ReactNode;
}

const FriendCard: React.FC<UserCardProps> = ({ user, subtitle, children }) => (
  <Card className="friend-card">
    <Card.Body>
      <div className="friend-card__header">
        <UserIdentityLink userId={user.id} className="friend-card__identity">
          <Avatar
            size={44}
            src={user.profile_picture || undefined}
            name={user.full_name || user.username}
            alt={`${user.username} avatar`}
          />
          <div>
            <div className="friend-card__name">{user.full_name || user.username}</div>
            <div className="friend-card__username">@{user.username}</div>
          </div>
        </UserIdentityLink>
        {subtitle && <span className="friend-card__subtitle">{subtitle}</span>}
      </div>
      <div className="friend-card__actions">{children}</div>
    </Card.Body>
  </Card>
);

const FriendsPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentUserId,
    friendRequests,
    friendships,
    blocks,
    loading,
    error,
    actionError,
    actionLoading,
    refresh,
    deriveRelationship,
    addFriend,
    cancelOutgoingRequest,
    acceptIncomingRequest,
    rejectIncomingRequest,
    removeFriend,
    follow,
    unfollow,
    block,
    unblock,
  } = useSocialGraph();

  const [suggestions, setSuggestions] = useState<CompactUser[]>([]);
  const [suggestionsLoading, setSuggestionsLoading] = useState<boolean>(true);
  const [suggestionsError, setSuggestionsError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<CompactUser[]>([]);
  const [searchError, setSearchError] = useState<string | null>(null);

  const loadSuggestions = async () => {
    setSuggestionsLoading(true);
    setSuggestionsError(null);
    try {
      const items = await fetchUserSuggestions();
      setSuggestions(items);
    } catch (err) {
      setSuggestionsError('Failed to load suggestions.');
      setSuggestions([]);
    } finally {
      setSuggestionsLoading(false);
    }
  };

  useEffect(() => {
    loadSuggestions();
  }, []);

  useEffect(() => {
    loadSuggestions();
  }, [friendships.length, friendRequests.length, blocks.length]);

  const incomingRequests = useMemo(
    () =>
      friendRequests.filter(
        (item) => item.status === 'pending' && item.receiver?.id === currentUserId
      ),
    [friendRequests, currentUserId]
  );

  const outgoingRequests = useMemo(
    () =>
      friendRequests.filter(
        (item) => item.status === 'pending' && item.sender?.id === currentUserId
      ),
    [friendRequests, currentUserId]
  );

  const friends = useMemo(
    () =>
      friendships.map((item) => (item.user1.id === currentUserId ? item.user2 : item.user1)),
    [friendships, currentUserId]
  );

  const blockedUsers = useMemo(() => blocks.map((item) => item.blocked), [blocks]);

  const runSearch = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }
    setSearchLoading(true);
    setSearchError(null);
    try {
      const users = await searchUsers(searchQuery.trim());
      setSearchResults(users);
    } catch (err) {
      setSearchError('Search failed. Please retry.');
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const sectionState = (emptyText: string, itemsLength: number, list: React.ReactNode) => {
    if (loading) {
      return (
        <div className="friends-state" aria-live="polite">
          <Spinner size="sm" animation="border" role="status" />
          <span>Loading...</span>
        </div>
      );
    }
    if (itemsLength === 0) {
      return <p className="text-muted mb-0">{emptyText}</p>;
    }
    return list;
  };

  return (
    <Container className="friends-page py-4">
      <header className="friends-page__header">
        <h1 className="h3 mb-0">Friends</h1>
        <Button type="button" variant="outline-secondary" onClick={() => navigate('/')}>Back to Home</Button>
      </header>

      {error && (
        <Alert variant="danger" role="alert">
          {error} <Button size="sm" variant="outline-danger" onClick={refresh}>Retry</Button>
        </Alert>
      )}
      {actionError && <Alert variant="danger" role="alert">{actionError}</Alert>}

      <Card className="friends-section-card mb-3">
        <Card.Body>
          <h2 className="h5">Find users</h2>
          <Form onSubmit={runSearch} className="friends-search-form">
            <Form.Control
              aria-label="Search users"
              placeholder="Search by username or name"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
            />
            <Button type="submit" disabled={searchLoading}>
              {searchLoading ? 'Searching...' : 'Search'}
            </Button>
          </Form>
          {searchError && <Alert variant="danger" className="mt-2 mb-0">{searchError}</Alert>}
          {searchResults.length > 0 && (
            <div className="friends-grid mt-3">
              {searchResults.map((item) => (
                <FriendCard key={item.id} user={item}>
                  <RelationshipActions
                    relationship={deriveRelationship(item.id)}
                    targetUserId={item.id}
                    actionLoading={actionLoading}
                    actionError={null}
                    onAddFriend={addFriend}
                    onCancelRequest={cancelOutgoingRequest}
                    onAcceptRequest={acceptIncomingRequest}
                    onRejectRequest={rejectIncomingRequest}
                    onRemoveFriend={removeFriend}
                    onFollow={follow}
                    onUnfollow={unfollow}
                    onBlock={block}
                    onUnblock={unblock}
                    onMessage={() => navigate(buildMessengerPathForUser(item.id))}
                  />
                </FriendCard>
              ))}
            </div>
          )}
        </Card.Body>
      </Card>

      <Row className="g-3">
        <Col xs={12} xl={6}>
          <Card className="friends-section-card h-100">
            <Card.Body>
              <h2 className="h5">Current friends</h2>
              {sectionState(
                'You have no friends yet.',
                friends.length,
                <div className="friends-grid">
                  {friends.map((item) => (
                    <FriendCard key={item.id} user={item}>
                      <Button
                        type="button"
                        variant="outline-primary"
                        onClick={() => navigate(buildMessengerPathForUser(item.id))}
                      >
                        Message
                      </Button>
                      <RelationshipActions
                        relationship={deriveRelationship(item.id)}
                        targetUserId={item.id}
                        actionLoading={actionLoading}
                        actionError={null}
                        onAddFriend={addFriend}
                        onCancelRequest={cancelOutgoingRequest}
                        onAcceptRequest={acceptIncomingRequest}
                        onRejectRequest={rejectIncomingRequest}
                        onRemoveFriend={removeFriend}
                        onFollow={follow}
                        onUnfollow={unfollow}
                        onBlock={block}
                        onUnblock={unblock}
                        hideMessage
                      />
                    </FriendCard>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col xs={12} xl={6}>
          <Card className="friends-section-card h-100">
            <Card.Body>
              <h2 className="h5">Incoming requests</h2>
              {sectionState(
                'No incoming requests.',
                incomingRequests.length,
                <div className="friends-grid">
                  {incomingRequests.map((item) => (
                    <FriendCard key={item.id} user={item.sender}>
                      <RelationshipActions
                        relationship={deriveRelationship(item.sender.id)}
                        targetUserId={item.sender.id}
                        actionLoading={actionLoading}
                        actionError={null}
                        onAddFriend={addFriend}
                        onCancelRequest={cancelOutgoingRequest}
                        onAcceptRequest={acceptIncomingRequest}
                        onRejectRequest={rejectIncomingRequest}
                        onRemoveFriend={removeFriend}
                        onFollow={follow}
                        onUnfollow={unfollow}
                        onBlock={block}
                        onUnblock={unblock}
                        onMessage={() => navigate(buildMessengerPathForUser(item.sender.id))}
                      />
                    </FriendCard>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col xs={12} xl={6}>
          <Card className="friends-section-card h-100">
            <Card.Body>
              <h2 className="h5">Outgoing requests</h2>
              {sectionState(
                'No outgoing pending requests.',
                outgoingRequests.length,
                <div className="friends-grid">
                  {outgoingRequests.map((item) => (
                    <FriendCard key={item.id} user={item.receiver}>
                      <RelationshipActions
                        relationship={deriveRelationship(item.receiver.id)}
                        targetUserId={item.receiver.id}
                        actionLoading={actionLoading}
                        actionError={null}
                        onAddFriend={addFriend}
                        onCancelRequest={cancelOutgoingRequest}
                        onAcceptRequest={acceptIncomingRequest}
                        onRejectRequest={rejectIncomingRequest}
                        onRemoveFriend={removeFriend}
                        onFollow={follow}
                        onUnfollow={unfollow}
                        onBlock={block}
                        onUnblock={unblock}
                        onMessage={() => navigate(buildMessengerPathForUser(item.receiver.id))}
                      />
                    </FriendCard>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col xs={12} xl={6}>
          <Card className="friends-section-card h-100">
            <Card.Body>
              <h2 className="h5">Suggestions</h2>
              {suggestionsLoading ? (
                <div className="friends-state" aria-live="polite">
                  <Spinner size="sm" animation="border" role="status" />
                  <span>Loading suggestions...</span>
                </div>
              ) : suggestionsError ? (
                <Alert variant="danger" className="mb-0">
                  {suggestionsError}{' '}
                  <Button size="sm" variant="outline-danger" onClick={loadSuggestions}>Retry</Button>
                </Alert>
              ) : suggestions.length === 0 ? (
                <p className="text-muted mb-0">No suggestions available right now.</p>
              ) : (
                <div className="friends-grid">
                  {suggestions.map((item) => (
                    <FriendCard key={item.id} user={item}>
                      <RelationshipActions
                        relationship={deriveRelationship(item.id)}
                        targetUserId={item.id}
                        actionLoading={actionLoading}
                        actionError={null}
                        onAddFriend={addFriend}
                        onCancelRequest={cancelOutgoingRequest}
                        onAcceptRequest={acceptIncomingRequest}
                        onRejectRequest={rejectIncomingRequest}
                        onRemoveFriend={removeFriend}
                        onFollow={follow}
                        onUnfollow={unfollow}
                        onBlock={block}
                        onUnblock={unblock}
                        onMessage={() => navigate(buildMessengerPathForUser(item.id))}
                      />
                    </FriendCard>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      <Card className="friends-section-card mt-3">
        <Card.Body>
          <h2 className="h5">Blocked users</h2>
          {sectionState(
            'You have not blocked anyone.',
            blockedUsers.length,
            <div className="friends-grid">
              {blocks.map((item) => (
                <FriendCard key={item.id} user={item.blocked}>
                  <Button
                    type="button"
                    variant="outline-warning"
                    disabled={actionLoading.unblock}
                    onClick={async () => {
                      if (!window.confirm('Unblock this user?')) return;
                      await unblock(item.id);
                    }}
                  >
                    {actionLoading.unblock ? 'Unblocking...' : 'Unblock'}
                  </Button>
                </FriendCard>
              ))}
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
};

export default FriendsPage;
