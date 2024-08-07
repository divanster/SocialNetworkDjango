import React from 'react';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { logout } from '../../services/auth'; // Adjust the path according to your folder structure
import { useNavigate } from 'react-router-dom'; // Use useNavigate instead of useHistory

const CustomNavbar: React.FC = () => {
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/login'); // Use navigate instead of history.push
    };

    return (
        <Navbar bg="dark" variant="dark" expand="lg">
            <LinkContainer to="/">
                <Navbar.Brand>My Social Network</Navbar.Brand>
            </LinkContainer>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="me-auto">
                    <LinkContainer to="/feed">
                        <Nav.Link>Feed</Nav.Link>
                    </LinkContainer>
                    <LinkContainer to="/profile">
                        <Nav.Link>Profile</Nav.Link>
                    </LinkContainer>
                    <NavDropdown title="More" id="basic-nav-dropdown">
                        <LinkContainer to="/settings">
                            <NavDropdown.Item>Settings</NavDropdown.Item>
                        </LinkContainer>
                        <NavDropdown.Divider />
                        <NavDropdown.Item onClick={handleLogout}>Logout</NavDropdown.Item>
                    </NavDropdown>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    );
};

export default CustomNavbar;
