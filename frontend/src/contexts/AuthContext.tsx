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
import { fetchProfileData } from '../services/api'; // Ensure this path is correct
import { useNavigate } from 'react-router-dom';

// Helper function to set the Axios header globally
const setAuthToken = (token: string | null): void => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Decode token expiration time (convert seconds to milliseconds)
const getTokenExpirationTime = (token: string): number | null => {
  try {
    const decoded = jwtDecode<JwtPayload>(token);
    return decoded.exp ? decoded.exp * 1000 : null;
  } catch (error) {
    console.error('Failed to decode token:', error);
    return null;
  }
};

// Define the User interface based on your backend's user data structure
export interface User {
  id: number;
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
    // Add other profile fields as needed
  };
  // Add any other user fields if necessary
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

interface AuthProviderProps {
  children: ReactNode;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [token, setToken] = useState<string | null>(localStorage.getItem('access_token'));
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const navigate = useNavigate();

  // Store refreshToken function in a ref for scheduled calls
  const refreshTokenRef = useRef<(() => Promise<string | null>) | null>(null);

  // Schedule a token refresh 1 minute before expiration
  const scheduleTokenRefresh = useCallback((accessToken: string): void => {
    const expirationTime = getTokenExpirationTime(accessToken);
    if (expirationTime) {
      const delay = expirationTime - Date.now() - 60000;
      console.log(`Scheduling token refresh in ${Math.max(delay / 1000, 0)} seconds`);
      if (delay > 0) {
        setTimeout(() => {
          refreshTokenRef.current?.();
        }, delay);
      }
    }
  }, []);

  // Logout function: clears tokens, resets state, and redirects to login page
  const logout = useCallback(async (): Promise<void> => {
    console.log('Logging out...');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setAuthToken(null);
    navigate('/login'); // Redirect to login page
  }, [navigate]);

  // Refresh token function: uses the stored refresh token to get a new access token.
  // If the backend rotates tokens, update the stored refresh token as well.
  const refreshToken = useCallback(async (): Promise<string | null> => {
    try {
      const storedRefreshToken = localStorage.getItem('refresh_token');
      console.log('Stored refresh token:', storedRefreshToken);

      if (!storedRefreshToken) {
        console.log('No refresh token available.');
        await logout();
        return null;
      }

      // For the refresh request, explicitly clear the Authorization header.
      const response = await axios.post(
        `${API_URL}/token/refresh/`,
        { refresh: storedRefreshToken },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': '', // Override any default Authorization header
          },
        }
      );

      console.log('Refresh token response:', response.data);

      const newAccessToken = response.data.access;
      const newRefreshToken = response.data.refresh; // If backend rotates refresh tokens
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

        // Fetch and update the user data after refreshing the token
        const userData = await fetchProfileData();
        setUser(userData);

        return newAccessToken;
      } else {
        console.log('No access token found in refresh response.');
        await logout();
        return null;
      }
    } catch (error: any) {
      if (error.response && error.response.data) {
        console.error('Error refreshing token details:', error.response.data);
      }
      console.error('Error refreshing token:', error);
      await logout();
      return null;
    }
  }, [logout, scheduleTokenRefresh]);

  // Save the refreshToken function in a ref so it can be invoked from scheduled callbacks
  useEffect(() => {
    refreshTokenRef.current = refreshToken;
  }, [refreshToken]);

  // Login function: stores tokens, sets state, schedules refresh, and fetches user data
  const login = useCallback(
    (accessToken: string, refreshTokenStr: string): void => {
      console.log('Logging in...');
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshTokenStr);
      setToken(accessToken);
      setIsAuthenticated(true);
      setAuthToken(accessToken);

      scheduleTokenRefresh(accessToken);

      // Fetch and set user data after login
      fetchProfileData()
        .then((userData) => {
          setUser(userData);
          console.log('User data fetched successfully after login.');
        })
        .catch((error) => {
          console.error('Error fetching user data after login:', error);
          // Optionally, logout if fetching user data fails
        });
    },
    [scheduleTokenRefresh]
  );

  // Initialize authentication state on app load
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

  // Axios interceptor: on 401 errors (except for the refresh endpoint), attempt token refresh.
  useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        // If the refresh request itself fails, logout immediately.
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

  return (
    <AuthContext.Provider
      value={{ isAuthenticated, token, user, loading, login, logout, refreshToken }}
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
