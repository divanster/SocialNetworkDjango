// src/components/Auth/Login.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../services/auth';
import { useAuth } from '../../contexts/AuthContext';
import { Form, Button, Card } from 'react-bootstrap';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const { login: authLogin } = useAuth(); // Use the login function from AuthContext

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const data = await login(email, password); // Call the login API
      authLogin(data.access, data.refresh); // Update the authentication state with access and refresh tokens
      navigate('/');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <Card className="my-5 p-3 border-primary">
      <Card.Body>
        <Form onSubmit={handleSubmit}>
          <h2>Login</h2>
          {error && <p className="text-danger">{error}</p>}
          <Form.Group controlId="formBasicEmail">
            <Form.Label>Email address</Form.Label>
            <Form.Control
              type="email"
              placeholder="Enter email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group controlId="formBasicPassword">
            <Form.Label>Password</Form.Label>
            <Form.Control
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </Form.Group>

          <Button variant="primary" type="submit">
            Login
          </Button>
        </Form>
      </Card.Body>
    </Card>
  );
};

export default Login;
