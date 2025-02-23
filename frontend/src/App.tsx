// frontend/src/App.tsx
import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar/Navbar';
import ErrorBoundary from './components/ErrorBoundary';
import { OnlineStatusProvider } from './contexts/OnlineStatusContext'; // Import OnlineStatusProvider

// Lazy load pages and components to improve performance
const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Albums = lazy(() => import('./pages/Albums'));
const Login = lazy(() => import('./components/Auth/Login'));
const Signup = lazy(() => import('./components/Auth/Signup'));
const NotFound = lazy(() => import('./components/NotFound'));
const Profile = lazy(() => import('./components/LeftSidebar/Profile'));
const Messages = lazy(() => import('./pages/Messages'));
const MessagesPage = lazy(() => import('./pages/MessagesPage'));
const Contacts = lazy(() => import('./components/RightSidebar/Contacts'));

const App: React.FC = () => {
  return (
    <OnlineStatusProvider> {/* Wrap the app with OnlineStatusProvider */}
      <Navbar /> {/* Global Navbar */}
      <ErrorBoundary> {/* Wrap with ErrorBoundary to handle any errors */}
        <Suspense fallback={<div>Loading...</div>}> {/* Lazy loading fallback */}
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
            <Route
              path="/contacts"
              element={
                <ProtectedRoute>
                  <Contacts />
                </ProtectedRoute>
              }
            />

            {/* Catch-All Route */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </OnlineStatusProvider>
  );
};

export default App;
