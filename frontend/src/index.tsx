// index.tsx
import React from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

import { WebSocketProvider } from './contexts/WebSocketContext'; // Import WebSocketProvider

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <WebSocketProvider> {/* Wrap the app with WebSocketProvider */}
        <App />
      </WebSocketProvider>
    </React.StrictMode>
  );
}

reportWebVitals();
