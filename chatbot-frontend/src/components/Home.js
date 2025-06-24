import React from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Home = () => {
  const { currentUser } = useAuth();

  return (
    <Container className="py-5">
      <Row className="mb-5">
        <Col>
          <h1 className="text-center">Multi-Modal Intelligent Chatbot</h1>
          <p className="text-center lead">
            A powerful chatbot system that can interact with AI models, manage documents, and scrape web content.
          </p>
        </Col>
      </Row>

      {!currentUser ? (
        <Row className="justify-content-center mb-5">
          <Col md={6} className="text-center">
            <p>Please login or register to use the chatbot.</p>
            <div className="d-flex justify-content-center gap-3">
              <Button as={Link} to="/login" variant="primary">Login</Button>
              <Button as={Link} to="/register" variant="outline-primary">Register</Button>
            </div>
          </Col>
        </Row>
      ) : (
        <Row className="g-4">
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <Card.Title>Chat with AI</Card.Title>
                <Card.Text>
                  Interact with our AI model to get answers to your questions and have natural conversations.
                </Card.Text>
                <Button as={Link} to="/chat" variant="primary">Start Chatting</Button>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <Card.Title>Document Management</Card.Title>
                <Card.Text>
                  Upload and manage documents that the AI can use to provide more accurate and contextual responses.
                </Card.Text>
                <Button as={Link} to="/documents" variant="primary">Manage Documents</Button>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <Card.Title>Web Scraping</Card.Title>
                <Card.Text>
                  Extract content from websites to provide the AI with up-to-date information from the web.
                </Card.Text>
                <Button as={Link} to="/scraper" variant="primary">Scrape Web Content</Button>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      <Row className="mt-5">
        <Col>
          <h2 className="text-center">Features</h2>
          <ul className="list-group">
            <li className="list-group-item">User authentication and account management</li>
            <li className="list-group-item">Document processing for PDF, DOCX, and TXT files</li>
            <li className="list-group-item">Web scraping to extract content from URLs</li>
            <li className="list-group-item">AI-powered chat interface</li>
            <li className="list-group-item">Conversation history and management</li>
          </ul>
        </Col>
      </Row>
    </Container>
  );
};

export default Home; 