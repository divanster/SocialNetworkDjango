// frontend/src/components/NotFound.tsx

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Card, Container } from 'react-bootstrap';

const NotFound: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Container className="py-4 d-flex justify-content-center">
      <Card className="w-100" style={{ maxWidth: 540 }}>
        <Card.Body className="text-center">
          <h1 className="h3">404 - Page Not Found</h1>
          <p className="text-muted mb-3">Sorry, the page you are looking for does not exist.</p>
          <Button type="button" onClick={() => navigate('/')} variant="primary">
            Go to Home
          </Button>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default NotFound;
