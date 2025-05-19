// frontend/src/index.tsx (FINAL)
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import store from './store';
import { AuthProvider } from './contexts/AuthContext';
import { PresenceWebSocketProvider } from './contexts/PresenceWebSocketContext';
import { OnlineStatusProvider } from './contexts/OnlineStatusContext';
import ErrorBoundary from './components/ErrorBoundary';

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(
    <BrowserRouter>
      <Provider store={store}>
        <AuthProvider>
          <PresenceWebSocketProvider>
            <OnlineStatusProvider>
              <ErrorBoundary>
                <App />
              </ErrorBoundary>
            </OnlineStatusProvider>
          </PresenceWebSocketProvider>
        </AuthProvider>
      </Provider>
    </BrowserRouter>
  );
}
reportWebVitals();
