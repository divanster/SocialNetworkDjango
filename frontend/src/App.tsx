import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import Navbar from './components/Navbar/Navbar';
import ErrorBoundary from './components/ErrorBoundary';

const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Messenger = lazy(() => import('./pages/Messenger'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const FriendsPage = lazy(() => import('./pages/FriendsPage'));
const Albums = lazy(() => import('./pages/Albums'));
const AlbumDetailPage = lazy(() => import('./pages/AlbumDetailPage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));
const Login = lazy(() => import('./components/Auth/Login'));
const Signup = lazy(() => import('./components/Auth/Signup'));
const NotFound = lazy(() => import('./components/NotFound'));

const App: React.FC = () => {

  return (
    <>
      <Navbar />
      <ErrorBoundary>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            {/* Protected */}
            <Route path="/" element={<ProtectedRoute><NewsFeed /></ProtectedRoute>} />
            <Route path="/messenger" element={<ProtectedRoute><Messenger /></ProtectedRoute>} />
            <Route path="/friends" element={<ProtectedRoute><FriendsPage /></ProtectedRoute>} />
            <Route path="/albums" element={<ProtectedRoute><Albums /></ProtectedRoute>} />
            <Route path="/albums/:albumId" element={<ProtectedRoute><AlbumDetailPage /></ProtectedRoute>} />
            <Route path="/notifications" element={<ProtectedRoute><NotificationsPage /></ProtectedRoute>} />
            <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            <Route path="/profile/:userId" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </ErrorBoundary>
    </>
  );
};

export default App;
