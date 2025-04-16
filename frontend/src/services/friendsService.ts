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

    // For each friendship record, figure out which side is me
    // and return the other user as the "friend."
    const friends = friendships.map((friendship) => {
      if (friendship.user1.id === currentUserId) {
        return friendship.user2;
      } else if (friendship.user2.id === currentUserId) {
        return friendship.user1;
      } else {
        // Neither side is me, so skip this record
        return null;
      }
    });

    // Filter out nulls (friendships that don't involve the current user)
    const validFriends = friends.filter((u) => u !== null) as User[];

    return validFriends;
  } catch (error) {
    handleApiError(error, 'Error fetching friends');
    return [];
  }
};
