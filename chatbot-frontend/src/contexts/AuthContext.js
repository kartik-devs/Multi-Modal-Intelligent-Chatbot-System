import React, { createContext, useState, useEffect, useContext } from 'react';
import { authService } from '../services/api';

// Create the authentication context
const AuthContext = createContext();

// Custom hook to use the auth context
export const useAuth = () => {
  return useContext(AuthContext);
};

// Provider component that wraps the app and makes auth object available to any child component that calls useAuth()
export const AuthProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // On mount, check if user is already logged in and validate token
  useEffect(() => {
    const validateAuth = async () => {
      const user = authService.getCurrentUser();
      const token = localStorage.getItem('token');
      
      if (user && token) {
        try {
          // Validate the token with the backend
          await authService.validateToken();
          setCurrentUser(user);
        } catch (err) {
          // If token validation fails, clear the stored data
          console.error('Token validation failed:', err);
          authService.logout();
        }
      }
      setLoading(false);
    };
    
    validateAuth();
  }, []);

  // Register a new user
  const register = async (userData) => {
    try {
      setError('');
      const response = await authService.register(userData);
      return response.data;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to register');
      throw err;
    }
  };

  // Login user
  const login = async (credentials) => {
    try {
      setError('');
      const response = await authService.login(credentials);
      const { token, user } = response.data;
      
      // Store token and user info in localStorage
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      
      setCurrentUser(user);
      return user;
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to login');
      throw err;
    }
  };

  // Logout user
  const logout = () => {
    authService.logout();
    setCurrentUser(null);
  };

  // Value object that will be passed to any consuming components
  const value = {
    currentUser,
    loading,
    error,
    register,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
}; 