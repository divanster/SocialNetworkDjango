import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Utility function to get headers with authorization
const getHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  },
});

// Helper function to handle errors
const handleApiError = (error: any, errorMessage: string) => {
  console.error(errorMessage, error);
  if (error.response) {
    console.error('Response data:', error.response.data);
  }
  throw error;
};

// Fetch user profile data
const fetchProfileData = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/users/me/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching profile data');
  }
};

// Update user profile data
const updateProfileData = async (formData: FormData) => {
  try {
    const response = await axios.patch(`${API_URL}/users/users/me/`, formData, {
      headers: {
        ...getHeaders().headers,
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error updating profile data');
  }
};

// Fetch news feed
const fetchNewsFeed = async () => {
  try {
    const response = await axios.get(`${API_URL}/posts/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching news feed');
    return { posts: [] };
  }
};

// Fetch notifications count
const fetchNotificationsCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/count/`, getHeaders());
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications count');
    return 0;
  }
};

// Fetch unread messages count
const fetchMessagesCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/count/`, getHeaders());
    return response.data.count;
  } catch (error) {
    handleApiError(error, 'Error fetching messages count');
    return 0;
  }
};

// Send a new message
const sendMessage = async (receiverId: number, content: string) => {
  try {
    const response = await axios.post(
      `${API_URL}/messenger/messages/`,
      { receiver: receiverId, content },
      getHeaders()
    );
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error sending message');
  }
};

// Fetch all messages
const fetchMessages = async () => {
  try {
    const response = await axios.get(`${API_URL}/messenger/messages/`, getHeaders());
    console.log('API response:', response.data);
    return response.data.results || []; // Ensure this is an array of message objects
  } catch (error) {
    handleApiError(error, 'Error fetching messages');
    return [];
  }
};

// Fetch albums
const fetchAlbums = async () => {
  try {
    const response = await axios.get(`${API_URL}/albums/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching albums');
    return { albums: [] };
  }
};

// Fetch comments
const fetchComments = async () => {
  try {
    const response = await axios.get(`${API_URL}/comments/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching comments');
    return { comments: [] };
  }
};

// Fetch follows
const fetchFollows = async () => {
  try {
    const response = await axios.get(`${API_URL}/follows/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching follows');
    return { follows: [] };
  }
};

// Fetch friends
const fetchFriends = async () => {
  try {
    const response = await axios.get(`${API_URL}/friends/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching friends');
    return { friends: [] };
  }
};

// Fetch notifications
const fetchNotifications = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching notifications');
    return { notifications: [] };
  }
};

// Fetch stories
const fetchStories = async () => {
  try {
    const response = await axios.get(`${API_URL}/stories/`, getHeaders());
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching stories');
    return { stories: [] };
  }
};

// Fetch users
const fetchUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/`, getHeaders());
    return Array.isArray(response.data) ? response.data : [];
  } catch (error) {
    handleApiError(error, 'Error fetching users');
    return [];
  }
};

export {
  fetchProfileData,
  updateProfileData,
  fetchNewsFeed,
  fetchNotificationsCount,
  fetchMessagesCount,
  sendMessage,
  fetchAlbums,
  fetchComments,
  fetchFollows,
  fetchFriends,
  fetchMessages,
  fetchNotifications,
  fetchStories,
  fetchUsers,
};
