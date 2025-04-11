import React, { useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import ContactsSidebar from '../components/Messenger/ContactsSidebar';
import ChatWindow from '../components/Messenger/ChatWindow';
import { User } from '../services/friendsService';
import './Messenger.css';

const Messenger: React.FC = () => {
  const [selectedFriend, setSelectedFriend] = useState<User | null>(null);

  return (
    <Container fluid className="mt-3 messenger-page">
      <Row>
        <Col md={4} className="contacts-column">
          <h4>Contacts</h4>
          <ContactsSidebar onSelectFriend={(friend) => setSelectedFriend(friend)} />
        </Col>
        <Col md={8} className="chat-column">
          {selectedFriend ? (
            // Pass the friend's id (as string) and name to ChatWindow
            <ChatWindow friendId={selectedFriend.id} friendName={selectedFriend.full_name || selectedFriend.username} />
          ) : (
            <div className="no-selection">Please select a friend to start a conversation.</div>
          )}
        </Col>
      </Row>
    </Container>
  );
};

export default Messenger;
