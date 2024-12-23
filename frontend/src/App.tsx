// frontend/src/App.tsx

import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NewsFeed from './pages/NewsFeed';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Profile from './components/LeftSidebar/Profile';
import Navbar from './components/Navbar/Navbar';
import NotFound from './components/NotFound';
import Messages from './components/Messages/Messages';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Navbar />
        <ErrorBoundary>
          <Routes>
            <Route path="/" element={<Navigate to="/feed" />} />
            <Route path="/feed" element={<NewsFeed />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/messages" element={<Messages />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </ErrorBoundary>
      </Router>
    </AuthProvider>
  );
};

export default App;
