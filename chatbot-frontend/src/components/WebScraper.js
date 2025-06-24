import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import { scrapingService } from '../services/api';

const WebScraper = () => {
  const [url, setUrl] = useState('');
  const [saveContent, setSaveContent] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [scrapedContent, setScrapedContent] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!url) {
      setError('Please enter a URL to scrape.');
      return;
    }
    
    setError('');
    setSuccess('');
    setScrapedContent('');
    setLoading(true);
    
    try {
      const response = await scrapingService.scrapeUrl(url, saveContent);
      setScrapedContent(response.data.content);
      setSuccess(saveContent ? 
        'Content scraped and saved successfully!' : 
        'Content scraped successfully!'
      );
    } catch (error) {
      console.error('Error scraping URL:', error);
      setError(error.response?.data?.message || 'Failed to scrape URL. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">Web Scraper</h1>
      
      <Row className="mb-5">
        <Col>
          <Card>
            <Card.Header>Scrape Web Content</Card.Header>
            <Card.Body>
              {error && <Alert variant="danger">{error}</Alert>}
              {success && <Alert variant="success">{success}</Alert>}
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>URL to Scrape</Form.Label>
                  <Form.Control 
                    type="url" 
                    placeholder="https://example.com" 
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    disabled={loading}
                    required
                  />
                </Form.Group>
                <Form.Group className="mb-3">
                  <Form.Check 
                    type="checkbox" 
                    label="Save content for future reference" 
                    checked={saveContent}
                    onChange={(e) => setSaveContent(e.target.checked)}
                    disabled={loading}
                  />
                </Form.Group>
                <Button 
                  variant="primary" 
                  type="submit"
                  disabled={loading || !url}
                >
                  {loading ? (
                    <>
                      <Spinner
                        as="span"
                        animation="border"
                        size="sm"
                        role="status"
                        aria-hidden="true"
                        className="me-2"
                      />
                      Scraping...
                    </>
                  ) : 'Scrape Content'}
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      {scrapedContent && (
        <Card>
          <Card.Header>Scraped Content</Card.Header>
          <Card.Body>
            <div 
              className="scraped-content"
              style={{
                maxHeight: '500px',
                overflowY: 'auto',
                padding: '15px',
                backgroundColor: '#f8f9fa',
                borderRadius: '5px'
              }}
            >
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                {scrapedContent}
              </pre>
            </div>
          </Card.Body>
        </Card>
      )}
      
      <Row className="mt-4">
        <Col>
          <Card>
            <Card.Header>Web Scraping Tips</Card.Header>
            <Card.Body>
              <ul>
                <li>Enter a complete URL including the protocol (http:// or https://)</li>
                <li>Some websites may block scraping attempts</li>
                <li>Check the website's robots.txt file and terms of service before scraping</li>
                <li>Save the content if you want the AI to reference it in future conversations</li>
                <li>The AI can use the scraped content to provide more accurate and up-to-date answers</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default WebScraper; 