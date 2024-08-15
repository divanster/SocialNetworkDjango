// frontend/src/components/Navbar/Navbar.tsx
import React, { useEffect } from 'react';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const CustomNavbar: React.FC = () => {
  const { isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    console.log('Navbar re-rendered. IsAuthenticated:', isAuthenticated);
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
          {isAuthenticated ? (
            <>
              <LinkContainer to="/feed">
                <Nav.Link>Feed</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/profile">
                <Nav.Link>Profile</Nav.Link>
              </LinkContainer>
            </>
          ) : null}
        </Nav>
        <Nav>
          {isAuthenticated ? (
            <>
              <LinkContainer to="/notifications">
                <Nav.Link>Notifications</Nav.Link>
              </LinkContainer>
              <LinkContainer to="/messages">
                <Nav.Link>Messages</Nav.Link>
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
