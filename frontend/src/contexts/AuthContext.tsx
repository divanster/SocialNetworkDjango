// frontend/src/contexts/AuthContext.tsx

import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  ReactNode,
  useCallback,
  useRef,
} from 'react';
import axios from 'axios';
import jwtDecode, { JwtPayload } from 'jwt-decode';

// Helper function to set the Axios header
const setAuthToken = (token: string | null): void => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Decode token expiration time
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

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  loading: boolean;
  login: (accessToken: string, refreshTokenStr: string) => void;
  logout: () => Promise<void>;
  refreshToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshTokenRef = useRef<(() => Promise<string | null>) | null>(null);

  const scheduleTokenRefresh = useCallback((accessToken: string): void => {
    const expirationTime = getTokenExpirationTime(accessToken);
    if (expirationTime) {
      const delay = expirationTime - Date.now() - 60000; // Refresh 1 minute before expiration
      if (delay > 0) {
        setTimeout(() => {
          refreshTokenRef.current?.();
        }, delay);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // No dependencies needed since `refreshTokenRef` is stable.

  const logout = useCallback(async (): Promise<void> => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setIsAuthenticated(false);
    setAuthToken(null);
  }, []);

  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const storedRefreshToken = localStorage.getItem('refresh_token');
      if (!storedRefreshToken) {
        console.log('No refresh token available.');
        await logout();
        return null;
      }

      const response = await axios.post(`${API_URL}/token/refresh/`, { refresh: storedRefreshToken });
      const newAccessToken = response.data.access;
      if (newAccessToken) {
        localStorage.setItem('access_token', newAccessToken);
        setToken(newAccessToken);
        setIsAuthenticated(true);
        setAuthToken(newAccessToken);

        scheduleTokenRefresh(newAccessToken);

        return newAccessToken;
      } else {
        await logout();
        return null;
      }
    } catch (error) {
      console.error('Error refreshing token:', error);
      await logout();
      return null;
    }
  }, [logout, scheduleTokenRefresh]);

  useEffect(() => {
    refreshTokenRef.current = refreshToken;
  }, [refreshToken]);

  const login = (accessToken: string, refreshTokenStr: string): void => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshTokenStr);
    setToken(accessToken);
    setIsAuthenticated(true);
    setAuthToken(accessToken);

    scheduleTokenRefresh(accessToken);
  };

  useEffect(() => {
    const initializeAuth = async () => {
      const accessToken = localStorage.getItem('access_token');
      if (accessToken) {
        const expirationTime = getTokenExpirationTime(accessToken);
        if (expirationTime && expirationTime > Date.now()) {
          setToken(accessToken);
          setIsAuthenticated(true);
          setAuthToken(accessToken);
          scheduleTokenRefresh(accessToken);
        } else {
          const newToken = await refreshToken();
          if (!newToken) await logout();
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, [refreshToken, logout, scheduleTokenRefresh]);

  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          const newToken = await refreshToken();
          if (newToken) {
            originalRequest.headers['Authorization'] = `Bearer ${newToken}`;
            return axios(originalRequest);
          }
        }
        return Promise.reject(error);
      }
    );

    return () => {
      axios.interceptors.response.eject(interceptor);
    };
  }, [refreshToken]);

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, token, loading, login, logout, refreshToken }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
