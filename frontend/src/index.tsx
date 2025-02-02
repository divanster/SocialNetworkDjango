// frontend/src/index.tsx

import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css'; // Import Bootstrap CSS

import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter
import { Provider } from 'react-redux';
import store from './store';
import { AuthProvider } from './contexts/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketManager';
import ErrorBoundary from './components/ErrorBoundary';

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        {/* Place BrowserRouter at the top so that all children get router context */}
        <BrowserRouter>
          <Provider store={store}>
            <AuthProvider>
              <WebSocketProvider>
                <App />
              </WebSocketProvider>
            </AuthProvider>
          </Provider>
        </BrowserRouter>
      </ErrorBoundary>
    </React.StrictMode>
  );
}

reportWebVitals();

console.log('Application rendered successfully');
