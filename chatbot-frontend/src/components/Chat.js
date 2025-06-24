import React, { useState, useRef, useEffect } from 'react';
import { Container, Row, Col, Form, Button, Card, Dropdown, Badge, Spinner, Alert } from 'react-bootstrap';
import { chatService, documentService } from '../services/api';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

const Chat = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [documentContent, setDocumentContent] = useState('');
  const [providers, setProviders] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState('groq');
  const [selectedModel, setSelectedModel] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  const [selectedApiKey, setSelectedApiKey] = useState(null);
  const [authError, setAuthError] = useState(null);
  const messagesEndRef = useRef(null);
  const { currentUser } = useAuth();
  const navigate = useNavigate();

  // Fetch documents, providers and API keys on component mount
  useEffect(() => {
    fetchData();
  }, []);

  // Function to fetch all required data
  const fetchData = async () => {
    setAuthError(null);
    try {
      await fetchDocuments();
      await fetchProviders();
      await fetchApiKeys();
    } catch (error) {
      if (error.response && error.response.status === 401) {
        setAuthError("Authentication error: Your session may have expired. Please try logging in again.");
      } else {
        console.error('Error fetching data:', error);
      }
    }
  };

  // Scroll to bottom whenever messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Update selected model when provider changes
  useEffect(() => {
    if (selectedProvider && providers.length > 0) {
      const provider = providers.find(p => p.id === selectedProvider);
      if (provider && provider.models && provider.models.length > 0) {
        setSelectedModel(provider.default_model);
      }
    }
    // Reset selected API key when provider changes
    setSelectedApiKey(null);
  }, [selectedProvider, providers]);

  const fetchDocuments = async () => {
    try {
      const response = await documentService.getDocuments();
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
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
      throw error;
    }
  };

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
      throw error;
    }
  };

  const handleRetry = () => {
    fetchData();
  };

  const handleLogin = () => {
    navigate('/login');
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const selectDocument = async (doc) => {
    setSelectedDocument(doc);
    if (doc && doc._id) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/api/documents/${doc._id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        if (response.data && response.data.document) {
          // Use full_content if available, otherwise use content
          const content = response.data.document.full_content || response.data.document.content || '';
          setDocumentContent(content);
        }
      } catch (error) {
        console.error('Error fetching document content:', error);
      }
    } else {
      setDocumentContent('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);
    
    try {
      // Include document content in the context if a document is selected
      const payload = {
        message: input,
        document_id: selectedDocument ? selectedDocument._id : null,
        context: documentContent,
        provider: selectedProvider,
        model: selectedModel,
        api_key: selectedApiKey ? selectedApiKey.api_key : null
      };
      
      const response = await chatService.sendMessage(payload);
      const aiMessage = { 
        role: 'assistant', 
        content: response.data.response,
        provider: response.data.provider,
        model: response.data.model
      };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { 
        role: 'system', 
        content: `Error: ${error.response?.data?.message || 'There was an error processing your request.'}`
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const getProviderName = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.name : providerId;
  };

  const getProviderModels = (providerId) => {
    const provider = providers.find(p => p.id === providerId);
    return provider ? provider.models : [];
  };

  // Get API keys for the selected provider
  const getProviderApiKeys = (providerId) => {
    return apiKeys.filter(key => key.provider === providerId);
  };

  // Format API key for display (showing only prefix and suffix)
  const formatApiKey = (key) => {
    if (!key || !key.api_key) return 'Default';
    const displayName = key.name || (key.is_default ? 'Default Key' : 'API Key');
    const prefix = key.api_key.substring(0, 4);
    const suffix = key.api_key.substring(key.api_key.length - 4);
    return `${displayName} (${prefix}...${suffix})${key.is_default ? ' ★' : ''}`;
  };

  // Format AI response with markdown-like syntax
  const formatAIResponse = (text) => {
    // Bold text between ** **
    let formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Numbered lists
    formattedText = formattedText.replace(/(\d+\.\s.*?)(?=\n\d+\.|\n\n|$)/g, '<div class="list-item">$1</div>');
    
    // Add paragraph breaks
    formattedText = formattedText.replace(/\n\n/g, '</p><p>');
    
    return <div dangerouslySetInnerHTML={{ __html: `<p>${formattedText}</p>` }} />;
  };

  return (
    <Container className="py-4">
      {authError ? (
        <Row className="justify-content-center mb-3">
          <Col md={10} lg={8}>
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
          </Col>
        </Row>
      ) : (
        <>
          <Row className="justify-content-center mb-3">
            <Col md={10} lg={8} className="text-center">
              <h1 className="text-primary mb-3">Chat with AI</h1>
            </Col>
          </Row>
          <Row className="justify-content-center">
            <Col md={10} lg={8}>
              <Card className="chat-container shadow">
                <Card.Header className="bg-primary text-white">
                  <div className="d-flex justify-content-center align-items-center">
                    <div className="d-flex flex-wrap justify-content-center" style={{ width: '100%' }}>
                      {/* AI Provider Selector */}
                      <Dropdown className="mx-1 mb-1" style={{ flex: '1 1 0', minWidth: '120px', maxWidth: '200px' }}>
                        <Dropdown.Toggle variant="light" id="provider-dropdown" size="sm" className="w-100">
                          <i className="bi bi-robot me-2"></i>
                          {getProviderName(selectedProvider)}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          {providers.map(provider => (
                            <Dropdown.Item 
                              key={provider.id} 
                              onClick={() => setSelectedProvider(provider.id)}
                              active={selectedProvider === provider.id}
                            >
                              {provider.name}
                            </Dropdown.Item>
                          ))}
                        </Dropdown.Menu>
                      </Dropdown>
                      
                      {/* Model Selector */}
                      {selectedProvider && getProviderModels(selectedProvider).length > 0 && (
                        <Dropdown className="mx-1 mb-1" style={{ flex: '1 1 0', minWidth: '120px', maxWidth: '200px' }}>
                          <Dropdown.Toggle variant="light" id="model-dropdown" size="sm" className="w-100">
                            <i className="bi bi-cpu me-2"></i>
                            {selectedModel || 'Select Model'}
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            {getProviderModels(selectedProvider).map(model => (
                              <Dropdown.Item 
                                key={model} 
                                onClick={() => setSelectedModel(model)}
                                active={selectedModel === model}
                              >
                                {model}
                              </Dropdown.Item>
                            ))}
                          </Dropdown.Menu>
                        </Dropdown>
                      )}
                      
                      {/* API Key Selector */}
                      {selectedProvider && getProviderApiKeys(selectedProvider).length > 0 && (
                        <Dropdown className="mx-1 mb-1" style={{ flex: '1 1 0', minWidth: '120px', maxWidth: '200px' }}>
                          <Dropdown.Toggle variant="light" id="api-key-dropdown" size="sm" className="w-100">
                            <i className="bi bi-key me-2"></i>
                            {selectedApiKey ? formatApiKey(selectedApiKey) : 'Select API Key'}
                          </Dropdown.Toggle>
                          <Dropdown.Menu>
                            <Dropdown.Item onClick={() => setSelectedApiKey(null)}>
                              Use Default API Key
                            </Dropdown.Item>
                            <Dropdown.Divider />
                            {getProviderApiKeys(selectedProvider).map(key => (
                              <Dropdown.Item 
                                key={key.id} 
                                onClick={() => setSelectedApiKey(key)}
                                active={selectedApiKey && selectedApiKey.id === key.id}
                              >
                                {formatApiKey(key)}
                              </Dropdown.Item>
                            ))}
                          </Dropdown.Menu>
                        </Dropdown>
                      )}
                      
                      {/* Document Selector */}
                      <Dropdown className="mx-1 mb-1" style={{ flex: '1 1 0', minWidth: '120px', maxWidth: '200px' }}>
                        <Dropdown.Toggle variant="light" id="document-dropdown" size="sm" className="w-100">
                          {selectedDocument ? (
                            <>
                              <i className="bi bi-file-earmark-text me-2"></i>
                              {selectedDocument.filename}
                            </>
                          ) : (
                            <>
                              <i className="bi bi-file-earmark me-2"></i>
                              Select Document
                            </>
                          )}
                        </Dropdown.Toggle>
                        <Dropdown.Menu>
                          <Dropdown.Item onClick={() => setSelectedDocument(null)}>
                            No Document (General Chat)
                          </Dropdown.Item>
                          <Dropdown.Divider />
                          {documents.map(doc => (
                            <Dropdown.Item key={doc._id} onClick={() => selectDocument(doc)}>
                              {doc.filename}
                            </Dropdown.Item>
                          ))}
                        </Dropdown.Menu>
                      </Dropdown>
                    </div>
                  </div>
                </Card.Header>
                <Card.Body 
                  className="chat-messages" 
                  style={{ 
                    height: '50vh', 
                    overflowY: 'auto',
                    backgroundColor: '#f8f9fa',
                    padding: '20px',
                    borderRadius: '0.5rem'
                  }}
                >
                  {messages.length === 0 ? (
                    <div className="text-center text-muted my-5">
                      <div className="mb-4">
                        <i className="bi bi-chat-dots" style={{ fontSize: '3rem' }}></i>
                      </div>
                      <h4>Start a conversation!</h4>
                      {selectedProvider && (
                        <p className="mt-3">
                          <Badge bg="primary" className="me-2">
                            {getProviderName(selectedProvider)}
                            {selectedModel && ` / ${selectedModel}`}
                          </Badge>
                          {selectedApiKey && (
                            <Badge bg="secondary">
                              API: {formatApiKey(selectedApiKey)}
                            </Badge>
                          )}
                        </p>
                      )}
                      {selectedDocument && (
                        <p className="mt-3">
                          <Badge bg="info">
                            Document: {selectedDocument.filename}
                          </Badge>
                        </p>
                      )}
                    </div>
                  ) : (
                    messages.map((msg, index) => (
                      <div 
                        key={index} 
                        className={`message ${msg.role === 'user' ? 'user-message' : 'ai-message'}`}
                        style={{
                          marginBottom: '16px',
                          padding: '12px 15px',
                          borderRadius: '18px',
                          maxWidth: '85%',
                          alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                          backgroundColor: msg.role === 'user' ? '#0d6efd' : '#ffffff',
                          color: msg.role === 'user' ? 'white' : '#212529',
                          marginLeft: msg.role === 'user' ? 'auto' : '0',
                          marginRight: msg.role === 'user' ? '0' : 'auto',
                          display: 'block',
                          boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                          border: msg.role === 'user' ? 'none' : '1px solid #e9ecef',
                          wordBreak: 'break-word'
                        }}
                      >
                        <div 
                          className="message-content"
                          style={{
                            fontSize: '0.95rem',
                            lineHeight: '1.5'
                          }}
                        >
                          {msg.role === 'user' ? msg.content : formatAIResponse(msg.content)}
                        </div>
                        <div 
                          className="message-role" 
                          style={{ 
                            fontSize: '0.75rem', 
                            opacity: 0.7,
                            textAlign: msg.role === 'user' ? 'right' : 'left',
                            marginTop: '4px'
                          }}
                        >
                          {msg.role === 'user' ? 'You' : (
                            <>
                              AI 
                              {msg.provider && (
                                <Badge bg="light" text="dark" className="ms-1" style={{ fontSize: '0.7rem' }}>
                                  {getProviderName(msg.provider)}
                                  {msg.model && ` / ${msg.model}`}
                                </Badge>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </Card.Body>
                <Card.Footer className="bg-light py-2">
                  <Form onSubmit={handleSubmit}>
                    <div className="d-flex">
                      <Form.Control
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your message..."
                        disabled={loading}
                        className="py-2"
                        style={{ borderRadius: '20px' }}
                      />
                      <Button 
                        type="submit" 
                        variant="primary" 
                        className="ms-2"
                        disabled={loading}
                        style={{ borderRadius: '50%', width: '38px', height: '38px', padding: '0', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                      >
                        {loading ? (
                          <Spinner size="sm" animation="border" />
                        ) : (
                          <i className="bi bi-send"></i>
                        )}
                      </Button>
                    </div>
                  </Form>
                </Card.Footer>
              </Card>
            </Col>
          </Row>
        </>
      )}
    </Container>
  );
};

export default Chat; 