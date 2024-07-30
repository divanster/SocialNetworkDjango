// frontend/src/components/Navbar/Navbar.tsx
import React from 'react';
import { Navbar, Nav, Form, FormControl, Button, Badge } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { FaBell, FaEnvelope } from 'react-icons/fa';

const CustomNavbar: React.FC = () => {
    const notificationsCount = 5; // Replace with dynamic data
    const messagesCount = 3; // Replace with dynamic data

    return (
        <Navbar bg="light" expand="lg" className="border-bottom mb-4">
            <Navbar.Brand as={Link} to="/">Social Network</Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse id="basic-navbar-nav">
                <Nav className="mr-auto">
                    <Nav.Link as={Link} to="/">Home</Nav.Link>
                    <Nav.Link as={Link} to="/feed">Feed</Nav.Link>
                </Nav>
                <Form className="d-flex">
                    <FormControl type="text" placeholder="Search" className="mr-sm-2" />
                    <Button variant="outline-success">Search</Button>
                </Form>
                <Nav>
                    <Nav.Link href="#">
                        <FaBell size={20} />
                        {notificationsCount > 0 && <Badge pill bg="danger" className="position-absolute top-0 start-100 translate-middle">{notificationsCount}</Badge>}
                    </Nav.Link>
                    <Nav.Link href="#">
                        <FaEnvelope size={20} />
                        {messagesCount > 0 && <Badge pill bg="danger" className="position-absolute top-0 start-100 translate-middle">{messagesCount}</Badge>}
                    </Nav.Link>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    );
};

export default CustomNavbar;
