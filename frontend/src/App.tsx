// src/App.tsx

import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NewsFeed from './pages/NewsFeed';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Profile from './components/LeftSidebar/Profile';
import Navbar from './components/Navbar/Navbar';
import NotFound from './components/NotFound';
import Messages from './components/Messages/Messages'; // Import the Messages component
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketManager';

const App: React.FC = () => {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <Router>
          <Navbar />
          <Routes>
            <Route path="/" element={<Navigate to="/feed" />} />
            <Route path="/feed" element={<NewsFeed />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/messages" element={<Messages />} /> {/* Add the Messages route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </WebSocketProvider>
    </AuthProvider>
  );
};

export default App;
