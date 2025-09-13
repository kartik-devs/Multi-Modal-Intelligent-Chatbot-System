import axios from 'axios';

// Define the base URL for the API
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:5000';

// Create an axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to include the auth token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Add a response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is due to an invalid/expired token and we haven't tried to refresh yet
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      // Clear the invalid token
      localStorage.removeItem('token');
      
      // Redirect to login page
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Authentication services
export const authService = {
  register: (userData) => api.post('/api/auth/register', userData),
  login: (credentials) => api.post('/api/auth/login', credentials),
  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  },
  getCurrentUser: () => {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },
  // Add a method to check if the token is valid
  validateToken: () => api.get('/api/auth/user'),
};

// Document services
export const documentService = {
  uploadDocument: (formData) => {
    return api.post('/api/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getDocuments: () => api.get('/api/documents'),
};

// Chat services
export const chatService = {
  sendMessage: (payload) => api.post('/api/chat', payload),
};

// Web scraping services
export const scrapingService = {
  scrapeUrl: (url, save = false, formData = null, method = 'GET') => 
    api.post('/api/scrape', { url, save, form_data: formData, method }),
  scrapeUcr: (payload) => api.post('/api/scrape/ucr', payload),
};

export default api; 