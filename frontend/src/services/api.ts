import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Utility function to get headers with authorization
const getHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  },
});

// Fetch user profile data
const fetchProfileData = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/users/me/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching profile data', error);
    throw error;
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
    console.error('Error updating profile data', error);
    throw error;
  }
};

// Fetch news feed
const fetchNewsFeed = async () => {
  try {
    const response = await axios.get(`${API_URL}/posts/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching news feed', error);
    return { posts: [] };
  }
};

// Fetch notifications count
const fetchNotificationsCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/count/`, getHeaders());
    return response.data.count;
  } catch (error) {
    console.error('Error fetching notifications count', error);
    return 0;
  }
};

// Fetch messages count
const fetchMessagesCount = async () => {
  try {
    const response = await axios.get(`${API_URL}/messages/count/`, getHeaders());
    return response.data.count;
  } catch (error) {
    console.error('Error fetching messages count', error);
    return 0;
  }
};

// Fetch albums
const fetchAlbums = async () => {
  try {
    const response = await axios.get(`${API_URL}/albums/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching albums', error);
    return { albums: [] };
  }
};

// Fetch comments
const fetchComments = async () => {
  try {
    const response = await axios.get(`${API_URL}/comments/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching comments', error);
    return { comments: [] };
  }
};

// Fetch follows
const fetchFollows = async () => {
  try {
    const response = await axios.get(`${API_URL}/follows/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching follows', error);
    return { follows: [] };
  }
};

// Fetch friends
const fetchFriends = async () => {
  try {
    const response = await axios.get(`${API_URL}/friends/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching friends', error);
    return { friends: [] };
  }
};

// Fetch messages
const fetchMessages = async () => {
  try {
    const response = await axios.get(`${API_URL}/messages/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching messages', error);
    return { messages: [] };
  }
};

// Fetch notifications
const fetchNotifications = async () => {
  try {
    const response = await axios.get(`${API_URL}/notifications/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching notifications', error);
    return { notifications: [] };
  }
};

// Fetch stories
const fetchStories = async () => {
  try {
    const response = await axios.get(`${API_URL}/stories/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching stories', error);
    return { stories: [] };
  }
};

// Fetch users
const fetchUsers = async () => {
  try {
    const response = await axios.get(`${API_URL}/users/`, getHeaders());
    return response.data;
  } catch (error) {
    console.error('Error fetching users', error);
    return { users: [] };
  }
};

export {
  fetchProfileData,
  updateProfileData,
  fetchNewsFeed,
  fetchNotificationsCount,
  fetchMessagesCount,
  fetchAlbums,
  fetchComments,
  fetchFollows,
  fetchFriends,
  fetchMessages,
  fetchNotifications,
  fetchStories,
  fetchUsers,
};
