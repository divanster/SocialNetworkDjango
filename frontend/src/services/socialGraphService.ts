import axios from 'axios';
import { handleApiError } from './api';

export interface CompactUser {
  id: string;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

export interface FriendRequestItem {
  id: string;
  sender: CompactUser;
  receiver: CompactUser;
  status: 'pending' | 'accepted' | 'rejected' | string;
  created_at: string;
}

export interface FriendshipItem {
  id: string;
  user1: CompactUser;
  user2: CompactUser;
  created_at: string;
}

export interface FollowItem {
  id: string;
  follower: string;
  followed: string;
  created_at: string;
}

export interface BlockItem {
  id: string;
  blocker: CompactUser;
  blocked: CompactUser;
  created_at: string;
}

export interface SuggestionUser extends CompactUser {
  mutual_friends_count: number;
}

const asArray = <T>(value: any): T[] => {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.results)) return value.results;
  return [];
};

export const fetchFriendRequests = async (): Promise<FriendRequestItem[]> => {
  try {
    const response = await axios.get('/friends/friend-requests/');
    return asArray<FriendRequestItem>(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching friend requests');
    return [];
  }
};

export const sendFriendRequest = async (receiverId: string): Promise<FriendRequestItem> => {
  try {
    const response = await axios.post('/friends/friend-requests/', { receiver_id: receiverId });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error sending friend request');
    throw error;
  }
};

export const acceptFriendRequest = async (requestId: string): Promise<void> => {
  try {
    await axios.post(`/friends/friend-requests/${requestId}/accept/`, {});
  } catch (error) {
    handleApiError(error, 'Error accepting friend request');
    throw error;
  }
};

export const rejectFriendRequest = async (requestId: string): Promise<void> => {
  try {
    await axios.post(`/friends/friend-requests/${requestId}/reject/`, {});
  } catch (error) {
    handleApiError(error, 'Error rejecting friend request');
    throw error;
  }
};

export const cancelFriendRequest = async (requestId: string): Promise<void> => {
  try {
    await axios.delete(`/friends/friend-requests/${requestId}/`);
  } catch (error) {
    handleApiError(error, 'Error canceling friend request');
    throw error;
  }
};

export const fetchFriendships = async (): Promise<FriendshipItem[]> => {
  try {
    const response = await axios.get('/friends/friendships/');
    return asArray<FriendshipItem>(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching friendships');
    return [];
  }
};

export const removeFriendship = async (friendshipId: string): Promise<void> => {
  try {
    await axios.delete(`/friends/friendships/${friendshipId}/`);
  } catch (error) {
    handleApiError(error, 'Error removing friendship');
    throw error;
  }
};

export const fetchFollows = async (followerId?: string): Promise<FollowItem[]> => {
  try {
    const response = await axios.get('/follows/', {
      params: followerId ? { follower_id: followerId } : undefined,
    });
    return asArray<FollowItem>(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching follows');
    return [];
  }
};

export const followUser = async (userId: string): Promise<FollowItem> => {
  try {
    const response = await axios.post('/follows/', { followed: userId });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error following user');
    throw error;
  }
};

export const unfollowUser = async (followId: string): Promise<void> => {
  try {
    await axios.delete(`/follows/${followId}/`);
  } catch (error) {
    handleApiError(error, 'Error unfollowing user');
    throw error;
  }
};

export const fetchBlocks = async (): Promise<BlockItem[]> => {
  try {
    const response = await axios.get('/friends/blocks/');
    return asArray<BlockItem>(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching blocks');
    return [];
  }
};

export const blockUser = async (blockedId: string): Promise<BlockItem> => {
  try {
    const response = await axios.post('/friends/blocks/', { blocked_id: blockedId });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error blocking user');
    throw error;
  }
};

export const unblockUser = async (blockId: string): Promise<void> => {
  try {
    await axios.delete(`/friends/blocks/${blockId}/`);
  } catch (error) {
    handleApiError(error, 'Error unblocking user');
    throw error;
  }
};

export const fetchUserSuggestions = async (): Promise<SuggestionUser[]> => {
  try {
    const response = await axios.get('/users/suggestions/');
    return asArray<SuggestionUser>(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching suggestions');
    return [];
  }
};

export const searchUsers = async (query: string): Promise<CompactUser[]> => {
  try {
    const response = await axios.get('/search/', {
      params: { query },
    });
    return asArray<CompactUser>(response.data?.users);
  } catch (error) {
    handleApiError(error, 'Error searching users');
    return [];
  }
};
