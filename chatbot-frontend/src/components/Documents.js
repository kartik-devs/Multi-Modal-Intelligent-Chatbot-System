import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Form, Button, Card, Table, Alert } from 'react-bootstrap';
import { documentService } from '../services/api';
import { useNavigate } from 'react-router-dom';

const Documents = () => {
  const [documents, setDocuments] = useState([]);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [authError, setAuthError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDocuments();
  }, []);

  const fetchDocuments = async () => {
    setLoading(true);
    setAuthError(null);
    try {
      const response = await documentService.getDocuments();
      setDocuments(response.data.documents || []);
      setError('');
    } catch (error) {
      console.error('Error fetching documents:', error);
      if (error.response && error.response.status === 401) {
        setAuthError("Authentication error: Your session may have expired. Please try logging in again.");
      } else {
        setError('Failed to fetch documents. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a file to upload.');
      return;
    }
    
    setError('');
    setSuccess('');
    setUploading(true);
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      await documentService.uploadDocument(formData);
      setSuccess('Document uploaded successfully!');
      setFile(null);
      e.target.reset();
      fetchDocuments(); // Refresh the documents list
    } catch (error) {
      console.error('Error uploading document:', error);
      if (error.response && error.response.status === 401) {
        setAuthError("Authentication error: Your session may have expired. Please try logging in again.");
      } else {
        setError(error.response?.data?.message || 'Failed to upload document. Please try again.');
      }
    } finally {
      setUploading(false);
    }
  };

  const handleRetry = () => {
    fetchDocuments();
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">Document Management</h1>
      
      {authError ? (
        <Alert variant="danger">
          <Alert.Heading>Authentication Error</Alert.Heading>
          <p>{authError}</p>
          <hr />
          <div className="d-flex justify-content-end">
            <Button variant="outline-danger" onClick={handleRetry} className="me-2">
              Retry
            </Button>
            <Button variant="danger" onClick={handleLogin}>
              Login Again
            </Button>
          </div>
        </Alert>
      ) : (
        <>
          <Row className="mb-5">
            <Col md={6}>
              <Card>
                <Card.Header>Upload a Document</Card.Header>
                <Card.Body>
                  {error && <Alert variant="danger">{error}</Alert>}
                  {success && <Alert variant="success">{success}</Alert>}
                  <Form onSubmit={handleSubmit}>
                    <Form.Group controlId="formFile" className="mb-3">
                      <Form.Label>Select a document to upload (PDF, DOCX, TXT)</Form.Label>
                      <Form.Control 
                        type="file" 
                        onChange={handleFileChange}
                        accept=".pdf,.docx,.txt"
                        disabled={uploading}
                      />
                    </Form.Group>
                    <Button 
                      variant="primary" 
                      type="submit"
                      disabled={uploading || !file}
                    >
                      {uploading ? 'Uploading...' : 'Upload'}
                    </Button>
                  </Form>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card>
                <Card.Header>Document Tips</Card.Header>
                <Card.Body>
                  <ul>
                    <li>Upload documents that you want the AI to reference</li>
                    <li>Supported formats: PDF, DOCX, TXT</li>
                    <li>Maximum file size: 16MB</li>
                    <li>For best results, ensure documents are text-searchable</li>
                    <li>The AI will be able to reference these documents when answering your questions</li>
                  </ul>
                </Card.Body>
              </Card>
            </Col>
          </Row>
          
          <Card>
            <Card.Header>Your Documents</Card.Header>
            <Card.Body>
              {loading ? (
                <p className="text-center">Loading documents...</p>
              ) : documents.length === 0 ? (
                <p className="text-center">No documents uploaded yet.</p>
              ) : (
                <Table striped bordered hover responsive>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Type</th>
                      <th>Size</th>
                      <th>Uploaded</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc._id}>
                        <td>{doc.filename}</td>
                        <td>{doc.filetype}</td>
                        <td>{Math.round(doc.size / 1024)} KB</td>
                        <td>{formatDate(doc.uploadDate)}</td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </>
      )}
    </Container>
  );
};

export default Documents; 