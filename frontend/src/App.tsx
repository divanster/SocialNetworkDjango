import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import NewsFeed from './pages/NewsFeed';
import Login from './components/Auth/Login';
import Signup from './components/Auth/Signup';
import Navbar from './components/Navbar/Navbar';
import NotFound from './components/NotFound';  // Assuming you have a NotFound component

const App: React.FC = () => {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<Navigate to="/feed" />} />
                <Route path="/feed" element={<NewsFeed />} />
                <Route path="/login" element={<Login />} />
                <Route path="/signup" element={<Signup />} />
                <Route path="*" element={<NotFound />} />  {/* Handles undefined routes */}
            </Routes>
        </Router>
    );
};

export default App;
