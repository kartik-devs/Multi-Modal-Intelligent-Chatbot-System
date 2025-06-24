import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Navbar, Nav, Container, Button, NavDropdown } from 'react-bootstrap';

const Navigation = () => {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/">Multi-Modal Intelligent Chatbot</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Home</Nav.Link>
            {currentUser && (
              <>
                <Nav.Link as={Link} to="/chat">Chat</Nav.Link>
                <Nav.Link as={Link} to="/documents">Documents</Nav.Link>
                <Nav.Link as={Link} to="/scraper">Web Scraper</Nav.Link>
              </>
            )}
          </Nav>
          <Nav>
            {currentUser ? (
              <div className="d-flex align-items-center">
                <NavDropdown title={currentUser.username || currentUser.email} id="user-dropdown" align="end">
                  <NavDropdown.Item as={Link} to="/api-settings">
                    <i className="bi bi-key me-2"></i>API Settings
                  </NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item onClick={handleLogout}>
                    <i className="bi bi-box-arrow-right me-2"></i>Logout
                  </NavDropdown.Item>
                </NavDropdown>
              </div>
            ) : (
              <>
                <Nav.Link as={Link} to="/login">Login</Nav.Link>
                <Nav.Link as={Link} to="/register">Register</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation; 