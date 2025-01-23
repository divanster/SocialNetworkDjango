// frontend/src/index.tsx

import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css';

import { WebSocketProvider } from './contexts/WebSocketManager';
import { AuthProvider } from './contexts/AuthContext';
import ErrorBoundary from './components/ErrorBoundary';
import { Provider } from 'react-redux';
import store from './store';

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <Provider store={store}>
          <AuthProvider>
            <WebSocketProvider>
              <App />
            </WebSocketProvider>
          </AuthProvider>
        </Provider>
      </ErrorBoundary>
    </React.StrictMode>
  );
}

reportWebVitals();

console.log('Application rendered successfully');
