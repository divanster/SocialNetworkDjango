import React, { useState, useEffect } from 'react';
import { Navbar, Nav, NavDropdown, Badge, Spinner } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';
import { logout } from '../../services/auth';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const CustomNavbar: React.FC = () => {
    const navigate = useNavigate();
    const [notificationCount, setNotificationCount] = useState<number | null>(null);
    const [messageCount, setMessageCount] = useState<number | null>(null);
    const [loadingNotifications, setLoadingNotifications] = useState(true);
    const [loadingMessages, setLoadingMessages] = useState(true);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            setIsAuthenticated(true);
            fetchNotificationCount();
            fetchMessageCount();
        } else {
            setIsAuthenticated(false);
        }
    }, []);

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
        } finally {
            setLoadingNotifications(false);
        }
    };

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
        } finally {
            setLoadingMessages(false);
        }
    };

    const handleLogout = async () => {
        await logout();
        navigate('/login');
        setIsAuthenticated(false);
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
                        </>
                    )}
                </Nav>
                <Nav>
                    {isAuthenticated ? (
                        <>
                            <LinkContainer to="/notifications">
                                <Nav.Link>
                                    Notifications{' '}
                                    {loadingNotifications ? (
                                        <Spinner as="span" animation="border" size="sm" />
                                    ) : (
                                        <Badge bg="secondary">{notificationCount}</Badge>
                                    )}
                                </Nav.Link>
                            </LinkContainer>
                            <LinkContainer to="/messages">
                                <Nav.Link>
                                    Messages{' '}
                                    {loadingMessages ? (
                                        <Spinner as="span" animation="border" size="sm" />
                                    ) : (
                                        <Badge bg="secondary">{messageCount}</Badge>
                                    )}
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
