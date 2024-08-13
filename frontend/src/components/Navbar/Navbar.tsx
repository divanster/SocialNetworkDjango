import React, { useState, useEffect } from 'react';
import { Navbar, Nav, NavDropdown, Badge } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { logout } from '../../services/auth';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CustomNavbar: React.FC = () => {
    const navigate = useNavigate();
    const [notificationCount, setNotificationCount] = useState(0);
    const [messageCount, setMessageCount] = useState(0);

    useEffect(() => {
        // Fetch notification count
        const fetchNotificationCount = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/notifications/count/', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`,
                    },
                });
                setNotificationCount(response.data.count);
            } catch (error) {
                console.error('Error fetching notification count:', error);
            }
        };

        // Fetch message count
        const fetchMessageCount = async () => {
            try {
                const response = await axios.get('http://localhost:8000/api/messages/count/', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('token')}`,
                    },
                });
                setMessageCount(response.data.count);
            } catch (error) {
                console.error('Error fetching message count:', error);
            }
        };

        fetchNotificationCount();
        fetchMessageCount();
    }, []);

    const handleLogout = async () => {
        await logout();
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
                    <LinkContainer to="/feed">
                        <Nav.Link>Feed</Nav.Link>
                    </LinkContainer>
                    <LinkContainer to="/profile">
                        <Nav.Link>Profile</Nav.Link>
                    </LinkContainer>
                </Nav>
                <Nav>
                    <LinkContainer to="/notifications">
                        <Nav.Link>
                            Notifications <Badge bg="secondary">{notificationCount}</Badge>
                        </Nav.Link>
                    </LinkContainer>
                    <LinkContainer to="/messages">
                        <Nav.Link>
                            Messages <Badge bg="secondary">{messageCount}</Badge>
                        </Nav.Link>
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
