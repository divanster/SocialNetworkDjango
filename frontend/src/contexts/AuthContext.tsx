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
import { fetchProfileData } from '../services/api';
import { useNavigate } from 'react-router-dom';

const setAuthToken = (token: string | null): void => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

const getTokenExpirationTime = (token: string): number | null => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp ? decoded.exp * 1000 : null;
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
};

export interface User {
  id: string;  // Changed to string to match UUIDs
  email: string;
  username: string;
  profile: {
    first_name: string;
    last_name: string;
    gender: string;
    date_of_birth: string;
    profile_picture: string;
    bio: string;
    phone: string;
    town: string;
    country: string;
    relationship_status: string;
  };
}

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  user: User | null;
  loading: boolean;
  login: (accessToken: string, refreshTokenStr: string) => void;
  logout: () => Promise<void>;
  refreshToken: () => Promise<string | null>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();
  const refreshTokenRef = useRef<(() => Promise<string | null>) | null>(null);

  const scheduleTokenRefresh = useCallback((accessToken: string): void => {
    const expirationTime = getTokenExpirationTime(accessToken);
    if (expirationTime) {
      const delay = expirationTime - Date.now() - 60000; // 60 seconds before expiration
      console.log(`Scheduling token refresh in ${Math.max(delay / 1000, 0)} seconds`);
      if (delay > 0) {
        setTimeout(() => {
          refreshTokenRef.current?.();
        }, delay);
      }
    }
  }, []);

  const logout = useCallback(async () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    window.dispatchEvent(new CustomEvent('user-logout'));
    navigate('/login');
  }, [navigate]);

  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const storedRefreshToken = localStorage.getItem('refresh_token');
      console.log('Stored refresh token:', storedRefreshToken);
      if (!storedRefreshToken) {
        console.log('No refresh token available.');
        await logout();
        return null;
      }
      const response = await axios.post(
        `${API_URL}/token/refresh/`,
        { refresh: storedRefreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': '',
          },
        }
      );
      console.log('Refresh token response:', response.data);
      const newAccessToken = response.data.access;
      const newRefreshToken = response.data.refresh;
      if (newAccessToken) {
        console.log('Token refreshed successfully.');
        localStorage.setItem('access_token', newAccessToken);
        if (newRefreshToken) {
          console.log('Refresh token rotated successfully.');
          localStorage.setItem('refresh_token', newRefreshToken);
        }
        setToken(newAccessToken);
        setIsAuthenticated(true);
        setAuthToken(newAccessToken);
        scheduleTokenRefresh(newAccessToken);
        const userData = await fetchProfileData();
        setUser(userData);
        return newAccessToken;
      } else {
        console.log('No access token found in refresh response.');
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

  const login = useCallback(
    (accessToken: string, refreshTokenStr: string): void => {
      console.log('Logging in...');
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshTokenStr);
      setToken(accessToken);
      setIsAuthenticated(true);
      setAuthToken(accessToken);
      scheduleTokenRefresh(accessToken);
      fetchProfileData()
        .then((userData) => {
          setUser(userData);
          console.log('User data fetched successfully after login.');
        })
        .catch((error) => {
          console.error('Error fetching user data after login:', error);
        });
    },
    [scheduleTokenRefresh]
  );

  useEffect(() => {
    const initializeAuth = async () => {
      console.log('Initializing authentication...');
      const storedAccessToken = localStorage.getItem('access_token');
      if (storedAccessToken) {
        const expirationTime = getTokenExpirationTime(storedAccessToken);
        if (expirationTime && expirationTime > Date.now()) {
          console.log('Access token is valid.');
          setToken(storedAccessToken);
          setIsAuthenticated(true);
          setAuthToken(storedAccessToken);
          scheduleTokenRefresh(storedAccessToken);
          try {
            const userData = await fetchProfileData();
            setUser(userData);
            console.log('User data fetched successfully during initialization.');
          } catch (error) {
            console.error('Error fetching user data during initialization:', error);
            await logout();
          }
        } else {
          console.log('Access token expired. Attempting to refresh...');
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
        if (originalRequest.url?.endsWith('/token/refresh/')) {
          await logout();
          return Promise.reject(error);
        }
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
  }, [refreshToken, logout]);

  const contextValue: AuthContextType = {
    isAuthenticated,
    token,
    user,
    loading,
    login,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
