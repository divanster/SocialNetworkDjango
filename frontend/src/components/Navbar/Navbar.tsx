import React, { useEffect, useState } from 'react';
import { Navbar, Nav, NavDropdown, Badge, Container } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useLocation, useNavigate } from 'react-router-dom';
import { BsFillHouseDoorFill, BsPeopleFill, BsMessenger, BsBellFill } from 'react-icons/bs';
import { useAuth } from '../../contexts/AuthContext';
import { API_URL, fetchMessagesCount, fetchNotificationsCount } from '../../services/api';
import SearchBar from '../Search/SearchBar';
import NotificationsDropdown from './NotificationsDropdown';
import MessagesDropdown from './MessagesDropdown';
import Avatar from '../Common/Avatar';
import './Navbar.css';

const CustomNavbar: React.FC = () => {
  const { isAuthenticated, logout, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [unreadMessages, setUnreadMessages] = useState<number>(0);
  const [unreadNotifications, setUnreadNotifications] = useState<number>(0);

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

  const isHome = location.pathname === '/';
  const isMessenger = location.pathname.startsWith('/messenger');
  const docsUrl = `${API_URL.replace(/\/api\/v1$/, '')}/api/docs/`;

  return (
    <Navbar className="app-navbar" expand="lg" sticky="top">
      <Container fluid className="app-navbar__inner">
        <div className="app-navbar__left">
          <LinkContainer to="/">
            <Navbar.Brand className="app-navbar__brand">SocialSphere</Navbar.Brand>
          </LinkContainer>
          {isAuthenticated && <SearchBar />}
        </div>

        <Navbar.Toggle aria-controls="main-navbar-nav" />
        <Navbar.Collapse id="main-navbar-nav" className="justify-content-between">
          {isAuthenticated ? (
            <>
              <Nav className="app-navbar__center">
                <LinkContainer to="/">
                  <Nav.Link className={`icon-link ${isHome ? 'active' : ''}`} aria-label="Home">
                    <BsFillHouseDoorFill />
                  </Nav.Link>
                </LinkContainer>
                <Nav.Link className="icon-link" aria-label="Friends" onClick={() => navigate('/')}>
                  <BsPeopleFill />
                </Nav.Link>
                <LinkContainer to="/messenger">
                  <Nav.Link className={`icon-link ${isMessenger ? 'active' : ''}`} aria-label="Messenger">
                    <span className="icon-badge-wrap">
                      <BsMessenger />
                      {unreadMessages > 0 && <Badge bg="danger">{unreadMessages}</Badge>}
                    </span>
                  </Nav.Link>
                </LinkContainer>
                <Nav.Link className="icon-link" aria-label="Notifications" onClick={() => navigate('/')}>
                  <span className="icon-badge-wrap">
                    <BsBellFill />
                    {unreadNotifications > 0 && <Badge bg="danger">{unreadNotifications}</Badge>}
                  </span>
                </Nav.Link>
              </Nav>

              <Nav className="app-navbar__right">
                <MessagesDropdown
                  unreadCount={unreadMessages}
                  setUnreadCount={setUnreadMessages}
                />
                <NotificationsDropdown
                  unreadCount={unreadNotifications}
                  setUnreadCount={setUnreadNotifications}
                />
                <NavDropdown
                  title={
                    <span className="account-trigger">
                      <Avatar
                        size={30}
                        src={user?.profile?.profile_picture}
                        name={user?.username || 'Account'}
                        alt="Account avatar"
                      />
                      <span className="account-name">{user?.username || 'Account'}</span>
                    </span>
                  }
                  id="account-dropdown"
                  align="end"
                >
                  <NavDropdown.Item
                    href={docsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    API Docs
                  </NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
                </NavDropdown>
              </Nav>
            </>
          ) : (
            <Nav className="ms-auto">
              <LinkContainer to="/login">
                <Nav.Link>Login</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/signup">
                <Nav.Link>Signup</Nav.Link>
              </LinkContainer>
            </Nav>
          )}
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default CustomNavbar;
