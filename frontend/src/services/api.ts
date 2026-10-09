// frontend/src/services/api.ts

import axios from 'axios';

const RAW_API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001/api/v1';
export const API_URL = RAW_API_URL.replace(/\/+$/, '');

// Set axios base URL so that relative URLs are correctly prefixed.
axios.defaults.baseURL = API_URL;

/**
 * Set the Authorization header for all axios requests.
 */
export const setAuthToken = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

/**
 * Helper function to handle API errors.
 */
export const handleApiError = (error: any, errorMessage: string) => {
  console.error(errorMessage, error);
  if (error.response) {
    console.error('Response data:', error.response.data);
  }
  throw error;
};

/**
 * =====================
 *  USER PROFILE
 * =====================
 */

export interface UserProfileData {
  first_name?: string;
  last_name?: string;
  gender?: string;
  date_of_birth?: string | null;
  profile_picture?: string | null;
  bio?: string;
  phone?: string | null;
  town?: string | null;
  country?: string | null;
  relationship_status?: string;
}

export interface UserData {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  profile: UserProfileData;
}

export interface UpdateProfilePayload {
  username?: string;
  profile?: Partial<UserProfileData>;
}

// Fetch user profile data
export const fetchProfileData = async (): Promise<UserData> => {
  try {
    const response = await axios.get('/users/me/');
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching profile data');
    throw error;
  }
};

export const fetchUserById = async (userId: string): Promise<UserData> => {
  try {
    const response = await axios.get(`/users/users/${userId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error, `Error fetching user profile by id: ${userId}`);
    throw error;
  }
};

// Update user profile data
export const updateProfileData = async (payload: FormData | UpdateProfilePayload): Promise<UserData> => {
  try {
    const response = await axios.patch('/users/me/', payload);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error updating profile data');
    throw error;
  }
};

/**
 * =====================
 *  NEWS FEED
 * =====================
 */

export const fetchNewsFeed = async () => {
  try {
    const response = await axios.get('/social/');
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching news feed');
    return { posts: [] };
  }
};

/**
 * =====================
 *  NOTIFICATIONS
 * =====================
 */

export const fetchNotificationsCount = async () => {
  try {
    const response = await axios.get('/notifications/count/');
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications count');
    return 0;
  }
};

/**
 * =====================
 *  MESSAGES COUNT
 * =====================
 */

// Fetch unread messages count using the correct endpoint
export const fetchMessagesCount = async () => {
  try {
    const response = await axios.get('/messenger/count/');
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching messages count');
    return 0;
  }
};

/**
 * =====================
 *  USERS
 * =====================
 */

export const fetchUsers = async () => {
  try {
    const response = await axios.get('/users/users/');
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    handleApiError(error, 'Error fetching users');
    return [];
  }
};
