import React from 'react';
import { Navbar, Nav, NavDropdown } from 'react-bootstrap';
import { LinkContainer } from 'react-router-bootstrap';

const CustomNavbar: React.FC = () => {
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
                        <LinkContainer to="/logout">
                            <NavDropdown.Item>Logout</NavDropdown.Item>
                        </LinkContainer>
                    </NavDropdown>
                </Nav>
            </Navbar.Collapse>
        </Navbar>
    );
};

export default CustomNavbar;
