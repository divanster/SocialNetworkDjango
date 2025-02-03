// frontend/src/services/api.ts

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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

// Fetch user profile data
export const fetchProfileData = async () => {
  try {
    const response = await axios.get('/users/users/me/');
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching profile data');
  }
};

// Update user profile data
export const updateProfileData = async (formData: FormData) => {
  try {
    const response = await axios.patch('/users/users/me/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error updating profile data');
  }
};

/**
 * =====================
 *  NEWS FEED
 * =====================
 */

export const fetchNewsFeed = async () => {
  try {
    const response = await axios.get('/posts/');
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
