import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';
import axios from 'axios';
import jwtDecode, { JwtPayload } from 'jwt-decode';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  loading: boolean; // Add this
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

// Decode token to get expiration time
const getTokenExpirationTime = (token: string): number | null => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    if (decoded.exp) {
      return decoded.exp * 1000; // Convert to milliseconds
    }
    return null;
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
};

// AuthProvider Component
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true); // Add loading state

  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      setToken(accessToken);
      setIsAuthenticated(!!accessToken);
      setAuthToken(accessToken); // Set token to axios globally
      setLoading(false); // Token initialization complete
    };

    initializeAuth();
  }, []);

  const scheduleTokenRefresh = (accessToken: string) => {
    const expirationTime = getTokenExpirationTime(accessToken);
    if (expirationTime) {
      const delay = expirationTime - Date.now() - 60000; // Refresh 1 minute before expiration
      if (delay > 0) {
        setTimeout(() => {
          refreshToken();
        }, delay);
      }
    }
  };

  const login = (accessToken: string, refreshTokenStr: string) => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshTokenStr);
    setToken(accessToken);
    setIsAuthenticated(true);
    setAuthToken(accessToken); // Set token to axios globally

    // Schedule token refresh
    scheduleTokenRefresh(accessToken);
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

        // Schedule token refresh
        scheduleTokenRefresh(response.data.access);

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
    <AuthContext.Provider value={{ isAuthenticated, token, loading, login, logout, refreshToken }}>
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
