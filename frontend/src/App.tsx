// frontend/src/App.tsx

import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Switch, Route } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import { WebSocketProvider } from './contexts/WebSocketManager';
import { AuthProvider } from './contexts/AuthContext';
import { Provider } from 'react-redux';
import store from './store';

const NewsFeed = lazy(() => import('./pages/NewsFeed'));
const Albums = lazy(() => import('./pages/Albums')); // New Albums page
const Login = lazy(() => import('./pages/Login'));
const Signup = lazy(() => import('./pages/Signup'));
const NotFound = lazy(() => import('./pages/NotFound'));

const App: React.FC = () => {
  return (
    <Provider store={store}>
      <AuthProvider>
        <WebSocketProvider>
          <Router>
            <Suspense fallback={<div>Loading...</div>}>
              <Switch>
                <Route path="/login" component={Login} />
                <Route path="/signup" component={Signup} />
                <ProtectedRoute exact path="/" component={NewsFeed} />
                <ProtectedRoute path="/albums" component={Albums} /> {/* Protected Albums route */}
                <Route component={NotFound} />
              </Switch>
            </Suspense>
          </Router>
        </WebSocketProvider>
      </AuthProvider>
    </Provider>
  );
};

export default App;
