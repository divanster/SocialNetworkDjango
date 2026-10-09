import React, { useEffect, useMemo, useState } from 'react';
import { Container, Row, Col, Alert, Button, Spinner } from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import ContactsSidebar from '../components/Messenger/ContactsSidebar';
import ChatWindow from '../components/Messenger/ChatWindow';
import { User } from '../services/friendsService';
import { fetchUserById } from '../services/api';
import './Messenger.css';

const Messenger: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedUserId = searchParams.get('userId');
  const [selectedFriend, setSelectedFriend] = useState<User | null>(null);
  const [loadingSelected, setLoadingSelected] = useState<boolean>(false);
  const [selectionError, setSelectionError] = useState<string | null>(null);
  const [showContactsOnMobile, setShowContactsOnMobile] = useState<boolean>(true);

  useEffect(() => {
    let mounted = true;
    const loadSelectedParticipant = async () => {
      if (!selectedUserId) {
        setSelectedFriend(null);
        setSelectionError(null);
        setLoadingSelected(false);
        return;
      }
      setLoadingSelected(true);
      setSelectionError(null);
      try {
        const data = await fetchUserById(selectedUserId);
        if (!mounted) return;
        const fullName = data.full_name || `${data.profile?.first_name || ''} ${data.profile?.last_name || ''}`.trim();
        setSelectedFriend({
          id: data.id,
          username: data.username,
          full_name: fullName || data.username,
          profile_picture: data.profile?.profile_picture || null,
        });
      } catch {
        if (!mounted) return;
        setSelectedFriend(null);
        setSelectionError('Could not open this conversation. Select a valid contact.');
      } finally {
        if (mounted) setLoadingSelected(false);
      }
    };

    loadSelectedParticipant();
    return () => {
      mounted = false;
    };
  }, [selectedUserId]);

  useEffect(() => {
    if (selectedUserId) {
      setShowContactsOnMobile(false);
    } else {
      setShowContactsOnMobile(true);
    }
  }, [selectedUserId]);

  const handleSelectFriend = (friend: User) => {
    setSelectionError(null);
    setSelectedFriend(friend);
    setSearchParams({ userId: friend.id });
    setShowContactsOnMobile(false);
  };

  const clearSelection = () => {
    setSearchParams({});
    setSelectedFriend(null);
    setSelectionError(null);
    setShowContactsOnMobile(true);
  };

  const chatContent = useMemo(() => {
    if (loadingSelected) {
      return (
        <div className="no-selection" role="status" aria-live="polite">
          <Spinner animation="border" size="sm" className="me-2" />
          Loading conversation...
        </div>
      );
    }
    if (selectionError) {
      return (
        <Alert variant="warning" className="d-flex justify-content-between align-items-center">
          <span>{selectionError}</span>
          <Button variant="outline-warning" size="sm" onClick={clearSelection}>
            Choose contact
          </Button>
        </Alert>
      );
    }
    if (!selectedFriend) {
      return <div className="no-selection">Select a contact to start chatting.</div>;
    }
    return (
      <ChatWindow
        friendId={selectedFriend.id}
        friendName={selectedFriend.full_name || selectedFriend.username}
        friendProfilePicture={selectedFriend.profile_picture}
      />
    );
  }, [clearSelection, loadingSelected, selectedFriend, selectionError]);

  return (
    <Container fluid className="mt-3 messenger-page">
      <Row className="messenger-grid">
        <Col
          md={4}
          className={`contacts-column ${showContactsOnMobile ? 'show-mobile' : 'hide-mobile'}`}
        >
          <h4>Contacts</h4>
          <ContactsSidebar selectedFriendId={selectedFriend?.id || null} onSelectFriend={handleSelectFriend} />
        </Col>
        <Col
          md={8}
          className={`chat-column ${showContactsOnMobile ? 'hide-mobile' : 'show-mobile'}`}
        >
          {!showContactsOnMobile && (
            <Button
              variant="outline-secondary"
              size="sm"
              className="d-md-none messenger-back-btn"
              onClick={() => setShowContactsOnMobile(true)}
              aria-label="Back to contact list"
            >
              Back to contacts
            </Button>
          )}
          {chatContent}
        </Col>
      </Row>
    </Container>
  );
};

export default Messenger;
