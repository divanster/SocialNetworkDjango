// frontend/src/services/api.ts

import axios from 'axios';

// API base URL from environment variable or fallback to localhost
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Helper function to set Authorization header for all Axios requests
export const setAuthToken = (token: string | null) => {
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete axios.defaults.headers.common['Authorization'];
  }
};

// Helper function to handle errors
export const handleApiError = (error: any, errorMessage: string) => {
  console.error(errorMessage, error);
  if (error.response) {
    console.error('Response data:', error.response.data);
  }
  throw error;
};

// Fetch user profile data
export const fetchProfileData = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/users/me/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
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
        Authorization: `Bearer ${localStorage.getItem('token')}`,
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
    const response = await axios.get(`${API_URL}/posts/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching news feed');
    return { posts: [] };
  }
};

// Fetch notifications count
export const fetchNotificationsCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/count/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications count');
    return 0;
  }
};

// Fetch unread messages count
export const fetchMessagesCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/count/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
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
      receiver_id: receiverId,
      content,
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error sending message');
  }
};

// Broadcast a message to all users
export const broadcastMessage = async (content: string) => {
  try {
    const response = await axios.post(`${API_URL}/messenger/messages/broadcast/`, { content }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error broadcasting message');
  }
};

// Fetch a specific message by ID
export const fetchMessageByIdAPI = async (messageId: string) => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/${messageId}/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching message by ID');
  }
};

// Mark a message as read
export const markMessageAsReadAPI = async (messageId: string) => {
  try {
    const response = await axios.post(`${API_URL}/messenger/messages/${messageId}/mark-as-read/`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
  }
};

// Fetch messages
export const fetchMessages = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    console.log('API response:', response.data);
    return response.data.results || [];
  } catch (error) {
    handleApiError(error, 'Error fetching messages');
    return [];
  }
};

// Fetch users
export const fetchUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/users/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    handleApiError(error, 'Error fetching users');
    return [];
  }
};
