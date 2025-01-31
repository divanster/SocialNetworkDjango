import axios from 'axios';

// Check if the app is running in local development or Docker
const isLocal = window.location.hostname === 'localhost';

// Set API and WebSocket URLs based on the environment (Docker or Local)
const API_URL = isLocal
  ? 'http://localhost:8000/api/v1'  // Local development API URL
  : process.env.REACT_APP_API_URL || 'http://web:8000/api/v1';  // Docker API URL

const WEBSOCKET_URL = isLocal
  ? 'ws://localhost:8000/ws'  // Local development WebSocket URL
  : process.env.REACT_APP_WEBSOCKET_URL || 'ws://web:8000/ws';  // Docker WebSocket URL

export const login = async (email: string, password: string) => {
  try {
    const response = await axios.post(`${API_URL}/token/`, {
      email,
      password,
    });

    if (response.data.access && response.data.refresh) {
      return {
        access: response.data.access,
        refresh: response.data.refresh,
      };
    } else {
      throw new Error('Login failed: Access or refresh token not received.');
    }
  } catch (error: unknown) {
    // Type guard to check if the error is an instance of Error
    if (error instanceof Error) {
      throw new Error(`Login failed: ${error.message}`);
    } else {
      throw new Error('Login failed: An unknown error occurred.');
    }
  }
};

export const signup = async (formData: FormData) => {
  try {
    const response = await axios.post(`${API_URL}/auth/signup/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: unknown) {
    // Type guard to check if the error is an instance of Error
    if (error instanceof Error) {
      throw new Error(`Signup failed: ${error.message}`);
    } else {
      throw new Error('Signup failed: An unknown error occurred.');
    }
  }
};

// Optional: You can re-add the logout function if necessary
// export const logout = () => { /* Handle logout */ };
