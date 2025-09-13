import React, { useState } from 'react';
import { Container, Row, Col, Form, Button, Card, Alert, Spinner } from 'react-bootstrap';
import { scrapingService } from '../services/api';

const WebScraper = () => {
  const [url, setUrl] = useState('');
  const [saveContent, setSaveContent] = useState(true);
  const [method, setMethod] = useState('GET');
  const [formData, setFormData] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [scrapedContent, setScrapedContent] = useState('');
  const [ucrHtml, setUcrHtml] = useState('');

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
      // Parse form data if provided
      let parsedFormData = null;
      if (method === 'POST' && formData.trim()) {
        try {
          parsedFormData = JSON.parse(formData);
        } catch (parseError) {
          setError('Invalid JSON format for form data. Please check your input.');
          setLoading(false);
          return;
        }
      }
      
      const response = await scrapingService.scrapeUrl(url, saveContent, parsedFormData, method);
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
      
      {/* UCR Fee Viewer Section */}
      <Row className="mb-5">
        <Col>
          <Card className="border-primary">
            <Card.Header className="bg-primary text-white">
              <h5 className="mb-0">UCR Fee Viewer - Context4 Reference-based Pricing</h5>
            </Card.Header>
            <Card.Body>
              <p className="text-muted mb-3">
                Specialized tool for querying the UCR Fee Viewer with medical procedure codes.
              </p>
              
              <Form onSubmit={handleSubmit}>
                <input type="hidden" value="https://www.feeinfo.com/DecisionPointUCR/?acctkey=C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs" 
                       onChange={(e) => setUrl(e.target.value)} />
                
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Service Date</Form.Label>
                      <Row>
                        <Col md={4}>
                          <Form.Select 
                            defaultValue="04"
                            onChange={(e) => {
                              const month = e.target.value;
                              setFormData(prev => {
                                const data = prev ? JSON.parse(prev) : {};
                                const currentDate = data.service_date || "04/04/2002";
                                const parts = currentDate.split('/');
                                data.service_date = `${month}/${parts[1] || "04"}/${parts[2] || "2002"}`;
                                return JSON.stringify(data, null, 2);
                              });
                            }}
                            disabled={loading}
                          >
                            <option value="01">January</option>
                            <option value="02">February</option>
                            <option value="03">March</option>
                            <option value="04">April</option>
                            <option value="05">May</option>
                            <option value="06">June</option>
                            <option value="07">July</option>
                            <option value="08">August</option>
                            <option value="09">September</option>
                            <option value="10">October</option>
                            <option value="11">November</option>
                            <option value="12">December</option>
                          </Form.Select>
                        </Col>
                        <Col md={4}>
                          <Form.Select 
                            defaultValue="04"
                            onChange={(e) => {
                              const day = e.target.value;
                              setFormData(prev => {
                                const data = prev ? JSON.parse(prev) : {};
                                const currentDate = data.service_date || "04/04/2002";
                                const parts = currentDate.split('/');
                                data.service_date = `${parts[0] || "04"}/${day}/${parts[2] || "2002"}`;
                                return JSON.stringify(data, null, 2);
                              });
                            }}
                            disabled={loading}
                          >
                            {Array.from({length: 31}, (_, i) => (
                              <option key={i+1} value={String(i+1).padStart(2, '0')}>
                                {i+1}
                              </option>
                            ))}
                          </Form.Select>
                        </Col>
                        <Col md={4}>
                          <Form.Select 
                            defaultValue="2002"
                            onChange={(e) => {
                              const year = e.target.value;
                              setFormData(prev => {
                                const data = prev ? JSON.parse(prev) : {};
                                const currentDate = data.service_date || "04/04/2002";
                                const parts = currentDate.split('/');
                                data.service_date = `${parts[0] || "04"}/${parts[1] || "04"}/${year}`;
                                return JSON.stringify(data, null, 2);
                              });
                            }}
                            disabled={loading}
                          >
                             {(() => {
                              const currentYear = new Date().getFullYear();
                              const startYear = 2000;
                              const endYear = currentYear + 5; // allow near-future years e.g., 2025+
                              const options = [];
                              for (let y = startYear; y <= endYear; y++) {
                                options.push(
                                  <option key={y} value={y}>{y}</option>
                                );
                              }
                              return options;
                            })()}
                          </Form.Select>
                        </Col>
                      </Row>
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Zip Code</Form.Label>
                      <Form.Control 
                        type="text" 
                        placeholder="90210"
                        defaultValue="90210"
                        onChange={(e) => {
                          setFormData(prev => {
                            const data = prev ? JSON.parse(prev) : {};
                            data.zip_code = e.target.value;
                            return JSON.stringify(data, null, 2);
                          });
                        }}
                        disabled={loading}
                      />
                    </Form.Group>
                  </Col>
                </Row>
                
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Procedure Code</Form.Label>
                      <Form.Control 
                        type="text" 
                        placeholder="99214"
                        defaultValue="99214"
                        onChange={(e) => {
                          setFormData(prev => {
                            const data = prev ? JSON.parse(prev) : {};
                            data.procedure_code = e.target.value;
                            return JSON.stringify(data, null, 2);
                          });
                        }}
                        disabled={loading}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Percentile</Form.Label>
                      <Form.Select 
                        defaultValue="50"
                        onChange={(e) => {
                          setFormData(prev => {
                            const data = prev ? JSON.parse(prev) : {};
                            data.percentile = e.target.value;
                            return JSON.stringify(data, null, 2);
                          });
                        }}
                        disabled={loading}
                      >
                        <option value="25">25th Percentile</option>
                        <option value="50">50th Percentile</option>
                        <option value="75">75th Percentile</option>
                        <option value="90">90th Percentile</option>
                        <option value="95">95th Percentile</option>
                      </Form.Select>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-3">
                  <Form.Label>Modifier (Optional)</Form.Label>
                  <Form.Control 
                    type="text" 
                    placeholder="e.g., 25, 59, etc."
                    onChange={(e) => {
                      setFormData(prev => {
                        const data = prev ? JSON.parse(prev) : {};
                        if (e.target.value) {
                          data.modifier = e.target.value;
                        } else {
                          delete data.modifier;
                        }
                        return JSON.stringify(data, null, 2);
                      });
                    }}
                    disabled={loading}
                  />
                </Form.Group>
                
                <div className="d-flex gap-2">
                  <Button 
                    variant="primary" 
                    type="submit"
                    disabled={loading}
                    onClick={() => {
                      setUrl("https://www.feeinfo.com/DecisionPointUCR/?acctkey=C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs");
                      setMethod("POST");
                      setFormData(JSON.stringify({
                        service_date: "04/04/2002",
                        procedure_code: "99214",
                        zip_code: "90210",
                        percentile: "50"
                      }, null, 2));
                    }}
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
                        Querying UCR...
                      </>
                    ) : 'Query UCR Fee Viewer'}
                  </Button>
                  <Button
                    variant="success"
                    type="button"
                    disabled={loading}
                    onClick={async () => {
                      setError('');
                      setSuccess('');
                      setUcrHtml('');
                      setScrapedContent('');
                      setLoading(true);
                      try {
                        const acctMatch = ("https://www.feeinfo.com/DecisionPointUCR/?acctkey=C4H2Qj65Neil_GhodMDQ54Sl9kXsqFs").match(/acctkey=([^&]+)/);
                        const acctkey = acctMatch ? acctMatch[1] : '';
                        const payload = {
                          acctkey,
                          serviceDate: JSON.parse(formData || '{}').service_date || '04/04/2002',
                          procedureCode: JSON.parse(formData || '{}').procedure_code || '99214',
                          zipCode: JSON.parse(formData || '{}').zip_code || '90210',
                          percentile: JSON.parse(formData || '{}').percentile || '50',
                          debug: true
                        };
                        const resp = await scrapingService.scrapeUcr(payload);
                        const parsed = resp.data?.data;
                        const raw = resp.data?.raw_html;
                        if (raw) setUcrHtml(raw);
                        if (parsed) setScrapedContent(JSON.stringify(parsed, null, 2));
                        setSuccess('UCR results fetched successfully.');
                      } catch (e) {
                        setError(e.response?.data?.message || 'Failed to fetch UCR results.');
                      } finally {
                        setLoading(false);
                      }
                    }}
                  >
                    Fetch with Browser (Playwright)
                  </Button>
                  
                  <Form.Check 
                    type="checkbox" 
                    label="Save results" 
                    checked={saveContent}
                    onChange={(e) => setSaveContent(e.target.checked)}
                    disabled={loading}
                    className="ms-3"
                  />
                </div>
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
      
      <Row className="mb-5">
        <Col>
          <Card>
            <Card.Header>General Web Scraper (Other Websites)</Card.Header>
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
                  <Form.Label>HTTP Method</Form.Label>
                  <Form.Select 
                    value={method}
                    onChange={(e) => setMethod(e.target.value)}
                    disabled={loading}
                  >
                    <option value="GET">GET</option>
                    <option value="POST">POST</option>
                  </Form.Select>
                </Form.Group>
                
                {method === 'POST' && (
                  <Form.Group className="mb-3">
                    <Form.Label>Form Data (JSON format)</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={4}
                      placeholder='{"field1": "value1", "field2": "value2"}'
                      value={formData}
                      onChange={(e) => setFormData(e.target.value)}
                      disabled={loading}
                    />
                    <Form.Text className="text-muted">
                      Enter form data as JSON key-value pairs for POST requests
                    </Form.Text>
                  </Form.Group>
                )}
                
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
      
      {(ucrHtml || scrapedContent) && (
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
              {ucrHtml ? (
                <div dangerouslySetInnerHTML={{ __html: ucrHtml }} />
              ) : (
                <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {scrapedContent}
                </pre>
              )}
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
                <li>Use POST method for forms that require data submission</li>
                <li>Form data should be in JSON format: {`{"field1": "value1", "field2": "value2"}`}</li>
                <li>Some websites may block scraping attempts</li>
                <li>Check the website's robots.txt file and terms of service before scraping</li>
                <li>Save the content if you want the AI to reference it in future conversations</li>
                <li>The AI can use the scraped content to provide more accurate and up-to-date answers</li>
              </ul>
              
              <div className="mt-3">
                <h6>UCR Fee Viewer Usage:</h6>
                <p className="text-muted">
                  Use the specialized UCR Fee Viewer section above for medical procedure fee lookups. 
                  The general scraper below is for other websites that support form submissions.
                </p>
                
                <h6>Example for Other Websites:</h6>
                <pre className="bg-light p-2 rounded">
{`URL: https://example.com/form
Method: POST
Form Data:
{
  "field1": "value1",
  "field2": "value2"
}`}
                </pre>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default WebScraper; 