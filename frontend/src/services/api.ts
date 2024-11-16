// src/services/api.ts

import axios from 'axios';

// API base URL from environment variable or fallback to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Helper function to set Authorization header for all Axios requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Helper function to handle errors
const handleApiError = (error: any, errorMessage: string) => {
  console.error(errorMessage, error);
  if (error.response) {
    console.error('Response data:', error.response.data);
  }
  throw error;
};

// Fetch user profile data
export const fetchProfileData = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/users/me/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching profile data');
  }
};

// Update user profile data
export const updateProfileData = async (formData: FormData) => {
  try {
    const response = await axios.patch(`${API_URL}/users/users/me/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error updating profile data');
  }
};

// Fetch news feed
export const fetchNewsFeed = async () => {
  try {
    const response = await axios.get(`${API_URL}/posts/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching news feed');
    return { posts: [] };
  }
};

// Fetch notifications count
export const fetchNotificationsCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/count/`);
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications count');
    return 0;
  }
};

// Fetch unread messages count
export const fetchMessagesCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/count/`);
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching messages count');
    return 0;
  }
};

// Send a new message
export const sendMessage = async (receiverId: number, content: string) => {
  try {
    const response = await axios.post(`${API_URL}/messenger/messages/`, {
      receiver: receiverId,
      content,
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error sending message');
  }
};

// Fetch all messages
export const fetchMessages = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/`);
    console.log('API response:', response.data);
    return response.data.results || [];
  } catch (error) {
    handleApiError(error, 'Error fetching messages');
    return [];
  }
};

// Fetch albums
export const fetchAlbums = async () => {
  try {
    const response = await axios.get(`${API_URL}/albums/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching albums');
    return { albums: [] };
  }
};

// Fetch comments
export const fetchComments = async () => {
  try {
    const response = await axios.get(`${API_URL}/comments/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching comments');
    return { comments: [] };
  }
};

// Fetch follows
export const fetchFollows = async () => {
  try {
    const response = await axios.get(`${API_URL}/follows/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching follows');
    return { follows: [] };
  }
};

// Fetch friends
export const fetchFriends = async () => {
  try {
    const response = await axios.get(`${API_URL}/friends/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching friends');
    return { friends: [] };
  }
};

// Fetch notifications
export const fetchNotifications = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications');
    return { notifications: [] };
  }
};

// Fetch stories
export const fetchStories = async () => {
  try {
    const response = await axios.get(`${API_URL}/stories/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching stories');
    return { stories: [] };
  }
};

// Fetch users
export const fetchUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/`);
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    handleApiError(error, 'Error fetching users');
    return [];
  }
};
