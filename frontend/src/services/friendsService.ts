// frontend/src/services/friendsService.ts

import { handleApiError } from './api';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

/**
 * If your Django route is /api/v1/friends/friendships or something like that,
 * you can fetch the data accordingly.
 */
export const fetchFriendsList = async () => {
  try {
    const response = await axios.get(`${API_URL}/friends/friendships/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching friends');
  }
};
