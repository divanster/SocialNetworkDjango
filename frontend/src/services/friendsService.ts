import axios from 'axios';
import { handleApiError } from './api';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

// Define the User interface if not already defined
export interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

// Fetch friends list
export const fetchFriendsList = async (): Promise<User[]> => {
  try {
    // IMPORTANT: Use 'access_token' instead of 'token'
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      // If no token is found, optionally handle it here
      console.warn('No access token found in localStorage.');
      return [];
    }

    const response = await axios.get(`${API_URL}/friends/`, {
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
    });

    // Check for a structure with URLs and handle accordingly
    if (response.data['friend-requests']) {
      // Handle the specific case where the response contains the URLs
      console.warn('Received structure with URLs for friend requests:', response.data);
      return []; // Adjust as per how you want to handle this response
    } else if (Array.isArray(response.data)) {
      // If the API returns an array directly
      return response.data;
    } else if (Array.isArray(response.data.results)) {
      // If the API returns a paginated response: { results: [...] }
      return response.data.results;
    } else {
      console.warn('Unexpected response structure:', response.data);
      return [];
    }
  } catch (error) {
    handleApiError(error, 'Error fetching friends list');
    return [];
  }
};
