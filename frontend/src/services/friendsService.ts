// frontend/src/services/friendsService.ts
import axios from 'axios';
import { handleApiError } from './api';

export interface User {
  id: string; // UUID as string
  username: string;
  full_name: string;
  profile_picture: string | null;
}

export interface Friendship {
  id: string;
  user1: User;
  user2: User;
  created_at: string;
}

/**
 * Fetch friendships and convert them into a friend list.
 * Use the current user's id to decide which partner is the friend.
 */
export const fetchFriendsList = async (currentUserId: string): Promise<User[]> => {
  try {
    const response = await axios.get('/friends/friendships/');
    const friendships: Friendship[] = response.data.results || [];
    const friends = friendships.map((friendship) => {
      return friendship.user1.id === currentUserId
        ? friendship.user2
        : friendship.user1;
    });
    return friends;
  } catch (error) {
    handleApiError(error, 'Error fetching friends');
    return [];
  }
};
