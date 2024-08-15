// index.tsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import { WebSocketProvider } from './contexts/WebSocketManager'; // Import WebSocketProvider
import { AuthProvider } from './contexts/AuthContext'; // Import AuthProvider

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <AuthProvider> {/* Wrap the app with AuthProvider */}
        <WebSocketProvider> {/* Wrap the app with WebSocketProvider */}
          <App />
        </WebSocketProvider>
      </AuthProvider>
    </React.StrictMode>
  );
}

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();

console.log('Application rendered successfully');
