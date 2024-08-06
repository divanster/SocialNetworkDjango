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
            <Navbar />  {/* Navbar will be displayed on all pages */}
            <Routes>
                <Route path="/" element={<Navigate to="/feed" />} />  {/* Redirect to /feed */}
                <Route path="/feed" element={<NewsFeed />} />  {/* Display NewsFeed component */}
                <Route path="/login" element={<Login />} />  {/* Display Login component */}
                <Route path="/signup" element={<Signup />} />  {/* Display Signup component */}
                <Route path="*" element={<NotFound />} />  {/* Handle undefined routes */}
            </Routes>
        </Router>
    );
};

export default App;
