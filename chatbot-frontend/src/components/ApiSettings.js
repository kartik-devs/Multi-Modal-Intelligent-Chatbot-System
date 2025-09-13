import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Table, Alert, Badge, Modal } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';
  
const ApiSettings = () => {
  const { currentUser } = useAuth();
  const [apiKeys, setApiKeys] = useState([]);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Form state
  const [newApiKey, setNewApiKey] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('');
  const [isDefault, setIsDefault] = useState(true);
  const [keyName, setKeyName] = useState('');
  
  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [detectedProvider, setDetectedProvider] = useState(null);

  useEffect(() => {
    fetchApiKeys();
    fetchProviders();
  }, []);

  const fetchApiKeys = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/api-keys`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setApiKeys(response.data.api_keys || []);
    } catch (error) {
      console.error('Error fetching API keys:', error);
      setError('Failed to fetch API keys');
    } finally {
      setLoading(false);
    }
  };

  const fetchProviders = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/providers`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      setProviders(response.data.providers || []);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!newApiKey) {
      setError('API key is required');
      return;
    }
    
    // If provider not selected but detected, use the detected one
    const providerToUse = selectedProvider || detectedProvider;
    
    if (!providerToUse) {
      setError('Please select a provider');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/api-keys`, {
        api_key: newApiKey,
        provider: providerToUse,
        is_default: isDefault,
        name: keyName
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setSuccess('API key added successfully');
      setNewApiKey('');
      setSelectedProvider('');
      setIsDefault(true);
      setKeyName('');
      fetchApiKeys();
    } catch (error) {
      console.error('Error adding API key:', error);
      setError(error.response?.data?.message || 'Failed to add API key');
    }
  };

  const handleDelete = async (keyId) => {
    if (!window.confirm('Are you sure you want to delete this API key?')) {
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/api-keys/${keyId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setSuccess('API key deleted successfully');
      fetchApiKeys();
    } catch (error) {
      console.error('Error deleting API key:', error);
      setError('Failed to delete API key');
    }
  };

  const handleSetDefault = async (keyId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/api/api-keys/${keyId}/default`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setSuccess('Default API key updated successfully');
      fetchApiKeys();
    } catch (error) {
      console.error('Error setting default API key:', error);
      setError('Failed to update default API key');
    }
  };

  const detectProvider = async () => {
    if (!newApiKey) {
      setError('Please enter an API key to detect');
      return;
    }
    
    // Basic detection based on key format
    let detected = null;
    
    if (newApiKey.startsWith('gsk_')) {
      detected = 'groq';
    } else if (newApiKey.startsWith('sk-') && !newApiKey.includes('ant-')) {
      detected = 'openai';
    } else if (newApiKey.startsWith('sk-ant-')) {
      detected = 'anthropic';
    }
    
    if (detected) {
      setDetectedProvider(detected);
      setSelectedProvider(detected);
      setShowModal(true);
    } else {
      setError('Could not detect provider. Please select one manually.');
    }
  };

  const getProviderName = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.name : providerId;
  };

  return (
    <Container className="py-5">
      <h1 className="mb-4">API Settings</h1>
      
      {error && <Alert variant="danger">{error}</Alert>}
      {success && <Alert variant="success">{success}</Alert>}
      
      <Row className="mb-5">
        <Col md={6}>
          <Card className="shadow">
            <Card.Header className="bg-primary text-white">
              <h4 className="mb-0">Add New API Key</h4>
            </Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>API Key</Form.Label>
                  <Form.Control 
                    type="text" 
                    value={newApiKey}
                    onChange={(e) => setNewApiKey(e.target.value)}
                    placeholder="Enter your API key"
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Key Name (Optional)</Form.Label>
                  <Form.Control 
                    type="text" 
                    value={keyName}
                    onChange={(e) => setKeyName(e.target.value)}
                    placeholder="Enter a reference name for this key"
                  />
                  <Form.Text className="text-muted">
                    A friendly name to help you identify this key (e.g. "Work Account", "Personal")
                  </Form.Text>
                </Form.Group>
                
                <div className="d-flex justify-content-between mb-3">
                  <Button 
                    variant="outline-secondary" 
                    onClick={detectProvider}
                    disabled={!newApiKey}
                  >
                    Auto-Detect Provider
                  </Button>
                  
                  <Form.Group>
                    <Form.Check 
                      type="checkbox"
                      label="Set as default"
                      checked={isDefault}
                      onChange={(e) => setIsDefault(e.target.checked)}
                    />
                  </Form.Group>
                </div>
                
                <Form.Group className="mb-3">
                  <Form.Label>Provider</Form.Label>
                  <Form.Select 
                    value={selectedProvider}
                    onChange={(e) => setSelectedProvider(e.target.value)}
                  >
                    <option value="">Select Provider</option>
                    {providers.map(provider => (
                      <option key={provider.id} value={provider.id}>
                        {provider.name}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
                
                <Button variant="primary" type="submit" className="w-100">
                  Add API Key
                </Button>
              </Form>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={6}>
          <Card className="shadow h-100">
            <Card.Header className="bg-info text-white">
              <h4 className="mb-0">API Key Tips</h4>
            </Card.Header>
            <Card.Body>
              <h5>Where to get API keys:</h5>
              <ul>
                <li><strong>Groq</strong>: <a href="https://console.groq.com/keys" target="_blank" rel="noreferrer">https://console.groq.com/keys</a></li>
                <li><strong>OpenAI</strong>: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noreferrer">https://platform.openai.com/api-keys</a></li>
                <li><strong>Anthropic</strong>: <a href="https://console.anthropic.com/account/keys" target="_blank" rel="noreferrer">https://console.anthropic.com/account/keys</a></li>
                <li><strong>Ollama</strong>: No API key required (runs locally)</li>
              </ul>
              <hr />
              <p><strong>Note:</strong> Your API keys are stored securely and are only used to make requests to the respective AI providers.</p>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Card className="shadow">
        <Card.Header className="bg-primary text-white">
          <h4 className="mb-0">Your API Keys</h4>
        </Card.Header>
        <Card.Body>
          {loading ? (
            <p className="text-center">Loading API keys...</p>
          ) : apiKeys.length === 0 ? (
            <p className="text-center">No API keys added yet.</p>
          ) : (
            <Table striped bordered hover responsive>
              <thead>
                <tr>
                  <th>Provider</th>
                  <th>Name</th>
                  <th>API Key</th>
                  <th>Usage Count</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {apiKeys.map((key) => (
                  <tr key={key.id}>
                    <td>
                      {getProviderName(key.provider)}
                    </td>
                    <td>
                      {key.name || '-'}
                    </td>
                    <td>
                      <code>{key.api_key}</code>
                    </td>
                    <td>{key.usage_count}</td>
                    <td>
                      {key.is_default ? (
                        <Badge bg="success">Default</Badge>
                      ) : (
                        <Badge bg="secondary">Alternative</Badge>
                      )}
                    </td>
                    <td>
                      {!key.is_default && (
                        <Button 
                          variant="outline-primary" 
                          size="sm"
                          onClick={() => handleSetDefault(key.id)}
                          className="me-2"
                        >
                          Set Default
                        </Button>
                      )}
                      <Button 
                        variant="outline-danger" 
                        size="sm"
                        onClick={() => handleDelete(key.id)}
                      >
                        Delete
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Card.Body>
      </Card>
      
      {/* Provider Detection Modal */}
      <Modal show={showModal} onHide={() => setShowModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Provider Detected</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p>
            We detected that this API key is for <strong>{getProviderName(detectedProvider)}</strong>.
          </p>
          <p>
            Do you want to use this provider?
          </p>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button 
            variant="primary" 
            onClick={() => {
              setSelectedProvider(detectedProvider);
              setShowModal(false);
            }}
          >
            Use {getProviderName(detectedProvider)}
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ApiSettings; 