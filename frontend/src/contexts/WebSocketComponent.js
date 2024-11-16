// WebSocketComponent.js

import React, { useEffect, useState, useRef } from "react";
import jwt_decode from "jwt-decode";
import { useAuth } from './AuthContext'; // Assuming your AuthContext file is in the same folder

function isTokenExpired(token) {
  const decoded = jwt_decode(token);
  const currentTime = Date.now() / 1000;  // in seconds
  return decoded.exp < currentTime;
}

const WebSocketComponent = () => {
  const { token, refreshToken } = useAuth(); // useAuth hook from AuthContext to get current token and refresh function
  const [error, setError] = useState(null);
  const socketRef = useRef(null);

  useEffect(() => {
    const connectWebSocket = async () => {
      // Close any existing WebSocket connection before attempting to reconnect.
      if (socketRef.current) {
        console.log('Closing existing WebSocket connection.');
        socketRef.current.close();
      }

      let currentToken = token;

      if (!currentToken || isTokenExpired(currentToken)) {
        console.log('Token is expired or missing. Attempting to refresh.');
        currentToken = await refreshToken();
      }

      if (currentToken) {
        console.log('Connecting to WebSocket with token:', currentToken);
        const ws = new WebSocket(`ws://localhost:8000/ws/albums/?token=${currentToken}`);

        ws.onopen = () => {
          console.log("WebSocket connected");
          setError(null); // Clear any previous errors.
        };

        ws.onmessage = (event) => {
          console.log("Received:", event.data);
        };

        ws.onclose = async (event) => {
          console.log("WebSocket connection closed", event);
          if (event.code === 4002) { // Server closed connection because token expired
            console.log('Token expired on server. Refreshing token.');
            const newToken = await refreshToken();
            if (newToken) {
              console.log('Reconnecting WebSocket with new token.');
              connectWebSocket();
            } else {
              setError("Token expired. Please login again.");
            }
          } else {
            console.log('WebSocket closed for another reason:', event.reason);
          }
        };

        ws.onerror = (error) => {
          console.error("WebSocket error", error);
          setError("An error occurred with the WebSocket connection.");
        };

        socketRef.current = ws;
      } else {
        console.log("Unable to connect to WebSocket. No valid token available.");
        setError("Token expired. Please login again.");
      }
    };

    // Only connect if the token is not null.
    if (token) {
      connectWebSocket();
    }

    // Cleanup function when the component unmounts or when re-rendering
    return () => {
      if (socketRef.current) {
        console.log('Cleaning up WebSocket connection.');
        socketRef.current.close();
      }
    };
  }, [token, refreshToken]); // Re-run the effect whenever the token changes

  return (
    <div>
      {error && <p>{error}</p>}
      {/* Additional UI for WebSocket interactions can go here */}
    </div>
  );
};

export default WebSocketComponent;
