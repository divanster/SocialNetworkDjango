import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css';
import { BrowserRouter } from 'react-router-dom';
import { Provider as ReduxProvider } from 'react-redux';
import store from './store';
import { AuthProvider } from './contexts/AuthContext';
import { OnlineStatusProvider } from './contexts/OnlineStatusContext';
import ErrorBoundary from './components/ErrorBoundary';

const container = document.getElementById('root');
if (container) {
  const root = createRoot(container);
  root.render(
    <BrowserRouter>
      <ReduxProvider store={store}>
        <AuthProvider>
          <OnlineStatusProvider>
            <ErrorBoundary>
              <App />
            </ErrorBoundary>
          </OnlineStatusProvider>
        </AuthProvider>
      </ReduxProvider>
    </BrowserRouter>
  );
}

reportWebVitals();
