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
import { WebSocketProvider } from './contexts/WebSocketContext'; // Correct import here
import { OnlineStatusProvider } from './contexts/OnlineStatusContext'; // Correct import here
import ErrorBoundary from './components/ErrorBoundary';

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <BrowserRouter>
          <Provider store={store}>
            <AuthProvider>
              <WebSocketProvider>
                <OnlineStatusProvider>
                  <App />
                </OnlineStatusProvider>
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
