// frontend/src/components/Navbar/Navbar.tsx
import React, { useEffect, useState } from 'react';
import { Navbar, Nav, Form, FormControl, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaBell, FaEnvelope } from 'react-icons/fa';
import { fetchNotificationsCount, fetchMessagesCount } from '../../services/api';

const CustomNavbar: React.FC = () => {
    const [notificationsCount, setNotificationsCount] = useState(0);
    const [messagesCount, setMessagesCount] = useState(0);

    useEffect(() => {
        const getCounts = async () => {
            try {
                const notifications = await fetchNotificationsCount();
                const messages = await fetchMessagesCount();
                setNotificationsCount(notifications);
                setMessagesCount(messages);
            } catch (error) {
                console.error('Error fetching counts', error);
            }
        };
        getCounts();
    }, []);

    return (
        <Navbar bg="light" expand="lg">
            <Navbar.Brand as={Link} to="/">MyApp</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <Nav.Link as={Link} to="/feed">Feed</Nav.Link>
                </Nav>
                <Form className="d-flex">
                    <FormControl type="text" placeholder="Search" className="mr-sm-2" />
                    <Button variant="outline-success">Search</Button>
                </Form>
                <Nav>
                    <Nav.Link href="#">
                        <FaBell size={20} />
                        {notificationsCount > 0 && <Badge pill bg="danger">{notificationsCount}</Badge>}
                    </Nav.Link>
                    <Nav.Link href="#">
                        <FaEnvelope size={20} />
                        {messagesCount > 0 && <Badge pill bg="danger">{messagesCount}</Badge>}
                    </Nav.Link>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    );
};

export default CustomNavbar;
