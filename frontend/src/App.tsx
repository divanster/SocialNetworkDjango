// frontend/src/App.tsx

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import { WebSocketProvider } from './contexts/WebSocketManager';
import { AuthProvider } from './contexts/AuthContext';
import { Provider } from 'react-redux';
import store from './store';

const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Albums = lazy(() => import('./pages/Albums')); // Correct import path
const Login = lazy(() => import('./components/Auth/Login'));
const Signup = lazy(() => import('./components/Auth/Signup'));
const NotFound = lazy(() => import('./components/NotFound'));
const Profile = lazy(() => import('./components/LeftSidebar/Profile')); // Corrected path

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AuthProvider>
        <WebSocketProvider>
          <Router>
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
        </WebSocketProvider>
      </AuthProvider>
    </Provider>
  );
};

export default App;
