// frontend/src/App.tsx

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar/Navbar'; // Import Navbar component
import ErrorBoundary from './components/ErrorBoundary'; // Import ErrorBoundary

const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Albums = lazy(() => import('./pages/Albums'));
const Login = lazy(() => import('./components/Auth/Login'));
const Signup = lazy(() => import('./components/Auth/Signup'));
const NotFound = lazy(() => import('./components/NotFound'));
const Profile = lazy(() => import('./components/LeftSidebar/Profile'));
const Messages = lazy(() => import('./pages/Messages')); // Import Messages.tsx
const MessagesPage = lazy(() => import('./pages/MessagesPage')); // For individual messages

const App: React.FC = () => {
  return (
    <Router>
      <Navbar /> {/* Ensure Navbar is placed here */}
      <ErrorBoundary>
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
            <Route
              path="/messages"
              element={
                <ProtectedRoute>
                  <Messages />
                </ProtectedRoute>
              }
            />
            <Route
              path="/messages/:id"
              element={
                <ProtectedRoute>
                  <MessagesPage />
                </ProtectedRoute>
              }
            />

            {/* Catch-All Route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </Router>
  );
};

export default App;
