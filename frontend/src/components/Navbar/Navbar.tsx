// src/components/Navbar/Navbar.tsx

import React, { useEffect, useState } from 'react';
import { Navbar, Nav, NavDropdown, Badge, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { fetchMessagesCount, fetchNotificationsCount } from '../../services/api';
import SearchBar from '../Search/SearchBar';
import NotificationsDropdown from './NotificationsDropdown';
import MessagesDropdown from './MessagesDropdown';
import './Navbar.css'; // Ensure you have proper styles

const CustomNavbar: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [unreadMessages, setUnreadMessages] = useState<number>(0);
  const [unreadNotifications, setUnreadNotifications] = useState<number>(0);

  // Fetch unread messages count
  useEffect(() => {
    const fetchUnreadMessages = async () => {
      if (isAuthenticated) {
        try {
          const count = await fetchMessagesCount();
          setUnreadMessages(count);
        } catch (error) {
          console.error('Failed to fetch unread messages count:', error);
        }
      } else {
        setUnreadMessages(0);
      }
    };

    fetchUnreadMessages();
  }, [isAuthenticated]);

  // Fetch unread notifications count
  useEffect(() => {
    const fetchUnreadNotifications = async () => {
      if (isAuthenticated) {
        try {
          const count = await fetchNotificationsCount();
          setUnreadNotifications(count);
        } catch (error) {
          console.error('Failed to fetch unread notifications count:', error);
        }
      } else {
        setUnreadNotifications(0);
      }
    };

    fetchUnreadNotifications();
  }, [isAuthenticated]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" fixed="top">
      <Container>
        <LinkContainer to="/">
          <Navbar.Brand>My Social Network</Navbar.Brand>
        </LinkContainer>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          {/* SearchBar Integration */}
          {isAuthenticated && (
            <Nav className="me-auto">
              <SearchBar />
            </Nav>
          )}

          <Nav className="ms-auto">
            {isAuthenticated ? (
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

                {/* Notifications Dropdown */}
                <NotificationsDropdown
                  unreadCount={unreadNotifications}
                  setUnreadCount={setUnreadNotifications}
                />

                {/* Messages Dropdown */}
                <MessagesDropdown
                  unreadCount={unreadMessages}
                  setUnreadCount={setUnreadMessages}
                />

                {/* More Dropdown */}
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
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
