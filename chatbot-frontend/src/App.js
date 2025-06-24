import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Navigation from './components/Navigation';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Chat from './components/Chat';
import Documents from './components/Documents';
import WebScraper from './components/WebScraper';
import ApiSettings from './components/ApiSettings';
import ProtectedRoute from './components/ProtectedRoute';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <Navigation />
          <main>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected Routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/chat" element={<Chat />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/scraper" element={<WebScraper />} />
                <Route path="/api-settings" element={<ApiSettings />} />
              </Route>
            </Routes>
          </main>
          <footer className="bg-dark text-light py-3 mt-5">
            <div className="container text-center">
              <p className="mb-0">
                &copy; {new Date().getFullYear()} Multi-Modal Intelligent Chatbot
              </p>
            </div>
          </footer>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App; 