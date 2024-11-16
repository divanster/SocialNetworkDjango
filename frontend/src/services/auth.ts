// src/services/auth.ts

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const login = async (email: string, password: string) => {
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
};

export const signup = async (formData: FormData) => {
  const response = await axios.post(`${API_URL}/auth/signup/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

// Removed the logout function as it's now handled by AuthContext
