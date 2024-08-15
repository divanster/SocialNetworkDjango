// frontend/src/services/auth.ts
import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const login = async (email: string, password: string) => {
  const response = await axios.post(`${API_URL}/token/`, {
    email,
    password,
  });
  if (response.data.access) {
    localStorage.setItem('token', response.data.access);
  }
  return response.data;
};

export const signup = async (formData: FormData) => {
  const response = await axios.post(`${API_URL}/auth/signup/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const logout = async () => {
  const token = localStorage.getItem('token');
  const refreshToken = localStorage.getItem('refresh_token');

  if (refreshToken) {
    try {
      await axios.post(`${API_URL}/token/blacklist/`, { refresh: refreshToken }, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login'; // Redirect to login page after logout
    } catch (error) {
      console.error('Logout failed:', error);
    }
  } else {
    console.log('No refresh token found');
    localStorage.removeItem('token');
    window.location.href = '/login'; // Redirect even if no refresh token found
  }
};

export const getCurrentUser = () => {
  return localStorage.getItem('token');
};
