// src/contexts/AuthContext.tsx

import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  login: (accessToken: string, refreshTokenStr: string) => void;
  logout: () => Promise<void>;
  refreshToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Helper to set Axios default header for authentication
const setAuthToken = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// AuthProvider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = localStorage.getItem('access_token');
    setToken(accessToken);
    setIsAuthenticated(!!accessToken);
    setAuthToken(accessToken); // Set token to axios globally
  }, []);

  const login = (accessToken: string, refreshTokenStr: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshTokenStr);
    setToken(accessToken);
    setIsAuthenticated(true);
    setAuthToken(accessToken); // Set token to axios globally
  };

  const logout = async () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setIsAuthenticated(false);
    setAuthToken(null); // Clear the axios token
  };

  const refreshToken = async (): Promise<string | null> => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        console.log('No refresh token available.');
        await logout();
        return null;
      }

      console.log('Attempting to refresh token...');
      const response = await axios.post(`${API_URL}/token/refresh/`, {
        refresh: refreshToken,
      });

      if (response.data.access) {
        console.log('Token refreshed successfully:', response.data.access);
        localStorage.setItem('access_token', response.data.access);
        setToken(response.data.access);
        setIsAuthenticated(true);
        setAuthToken(response.data.access); // Update token in axios headers
        return response.data.access;
      } else {
        console.log('Failed to refresh token.');
        await logout();
        return null;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      await logout();
      return null;
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
