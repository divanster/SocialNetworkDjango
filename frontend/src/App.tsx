// frontend/src/App.tsx

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar/Navbar'; // Import Navbar component

const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Albums = lazy(() => import('./pages/Albums')); // Correct import path
const Login = lazy(() => import('./components/Auth/Login'));
const Signup = lazy(() => import('./components/Auth/Signup'));
const NotFound = lazy(() => import('./components/NotFound'));
const Profile = lazy(() => import('./components/LeftSidebar/Profile')); // Corrected path

const App: React.FC = () => {
  return (
    <Router>
      <Navbar /> {/* Ensure Navbar is placed here */}
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />

          {/* Protected Routes */}
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <NewsFeed />
              </ProtectedRoute>
            }
          />
          <Route
            path="/albums"
            element={
              <ProtectedRoute>
                <Albums />
              </ProtectedRoute>
            }
          />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <Profile />
              </ProtectedRoute>
            }
          />

          {/* Catch-All Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </Router>
  );
};

export default App;
