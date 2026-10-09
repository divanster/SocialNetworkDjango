// frontend/src/pages/Messenger.tsx
import React, { useEffect, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import { useSearchParams } from 'react-router-dom';
import ContactsSidebar from '../components/Messenger/ContactsSidebar';
import ChatWindow from '../components/Messenger/ChatWindow';
import { User } from '../services/friendsService';
import { fetchUserById } from '../services/api';
import './Messenger.css';

const Messenger: React.FC = () => {
  const [selectedFriend, setSelectedFriend] = useState<User | null>(null);
  const [searchParams, setSearchParams] = useSearchParams();
  const selectedUserIdFromQuery = searchParams.get('userId');

  useEffect(() => {
    const userId = selectedUserIdFromQuery;
    if (!userId) return;

    let mounted = true;
    fetchUserById(userId)
      .then((data) => {
        if (!mounted) return;
        const fullName = data.full_name || `${data.profile?.first_name || ''} ${data.profile?.last_name || ''}`.trim();
        setSelectedFriend({
          id: data.id,
          username: data.username,
          full_name: fullName || data.username,
          profile_picture: data.profile?.profile_picture || null,
        });
      })
      .catch(() => {
        if (mounted) {
          setSelectedFriend(null);
        }
      });

    return () => {
      mounted = false;
    };
  }, [selectedUserIdFromQuery]);

  const handleSelectFriend = (friend: User) => {
    setSelectedFriend(friend);
    setSearchParams({ userId: friend.id });
  };

  return (
    <Container fluid className="mt-3 messenger-page">
      <Row>
        <Col md={4} className="contacts-column">
          <h4>Contacts</h4>
          <ContactsSidebar
            selectedFriendId={selectedFriend?.id || null}
            onSelectFriend={handleSelectFriend}
          />
        </Col>
        <Col md={8} className="chat-column">
          {selectedFriend ? (
            <ChatWindow
              friendId={selectedFriend.id}
              friendName={selectedFriend.full_name || selectedFriend.username}
            />
          ) : (
            <div className="no-selection">Please select a friend to start a conversation.</div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Messenger;
