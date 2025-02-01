// src/services/friendsService.ts

import axios from 'axios';
import { handleApiError } from './api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Fetch friends list
export const fetchFriendsList = async (): Promise<User[]> => {
  try {
    const response = await axios.get(`${API_URL}/friends/`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    // **Adjust this based on your API's response structure**
    // If your API returns { results: [...] }, use response.data.results
    // If it returns an array directly, use response.data
    if (Array.isArray(response.data)) {
      return response.data;
    } else if (Array.isArray(response.data.results)) {
      return response.data.results;
    } else {
      console.warn('Unexpected response structure:', response.data);
      return [];
    }

  } catch (error) {
    handleApiError(error, 'Error fetching friends list');
    return []; // Return an empty array in case of error
  }
};

// Define the User interface if not already defined
export interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}
