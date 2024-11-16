// src/components/Navbar/Navbar.tsx

import React, { useEffect, useState } from 'react';
import { Navbar, Nav, NavDropdown, Badge } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { fetchMessagesCount } from '../../services/api'; // Ensure this is correctly imported

const CustomNavbar: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadCount, setUnreadCount] = useState<number>(0);

  useEffect(() => {
    if (isAuthenticated) {
      const fetchUnreadMessagesCount = async () => {
        try {
          const count = await fetchMessagesCount(); // No longer need to pass token
          setUnreadCount(count);
        } catch (error) {
          console.error('Failed to fetch unread messages count:', error);
        }
      };

      fetchUnreadMessagesCount();
    } else {
      setUnreadCount(0); // Reset unread count when not authenticated
    }
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <LinkContainer to="/">
        <Navbar.Brand>My Social Network</Navbar.Brand>
      </LinkContainer>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="me-auto">
          {isAuthenticated && (
            <>
              <LinkContainer to="/feed">
                <Nav.Link>Feed</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/profile">
                <Nav.Link>Profile</Nav.Link>
              </LinkContainer>
              <li className="nav-item mx-2">
                <a
                  className="nav-link"
                  href="http://127.0.0.1:8000/api/docs/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  API Docs
                </a>
              </li>
            </>
          )}
        </Nav>
        <Nav>
          {isAuthenticated ? (
            <>
              <LinkContainer to="/notifications">
                <Nav.Link>Notifications</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/messages">
                <Nav.Link>
                  Messages {unreadCount > 0 && <Badge bg="danger">{unreadCount}</Badge>}
                </Nav.Link>
              </LinkContainer>
              <NavDropdown title="More" id="basic-nav-dropdown">
                <LinkContainer to="/settings">
                  <NavDropdown.Item>Settings</NavDropdown.Item>
                </LinkContainer>
                <NavDropdown.Divider />
                <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
              </NavDropdown>
            </>
          ) : (
            <>
              <LinkContainer to="/login">
                <Nav.Link>Login</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/signup">
                <Nav.Link>Signup</Nav.Link>
              </LinkContainer>
            </>
          )}
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
};

export default CustomNavbar;
