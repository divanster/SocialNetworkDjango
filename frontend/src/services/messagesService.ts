import axios from 'axios';
import { handleApiError } from './api';

export interface User {
  id: string; // using string for UUID
  username: string;
  full_name: string;
  profile_picture: string | null;
}

export interface Message {
  id: string;
  sender: User;
  receiver: User;
  content: string;
  read: boolean;
  created_at: string;
}

/**
 * Fetch inbox messages for the current logged‑in user.
 * Calls GET /messenger/inbox/ on your backend.
 */
export const fetchInboxMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get('/messenger/inbox/');
    if (response.data && Array.isArray(response.data.results)) {
      return response.data.results;
    }
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching inbox messages');
    return [];
  }
};

/**
 * Send a message to a specific user.
 * POST /messenger/ on your backend.
 */
export const sendMessageToUser = async (
  receiverId: string,
  content: string
): Promise<Message> => {
  try {
    const response = await axios.post('/messenger/', {
      receiver: receiverId,
      content,
    });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error sending message to user');
    throw error;
  }
};

/**
 * Broadcast a message to all users.
 * POST /messenger/broadcast/ on your backend.
 */
export const broadcastMessageToAll = async (content: string): Promise<Message[]> => {
  try {
    const response = await axios.post('/messenger/broadcast/', { content });
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error broadcasting message to all users');
    throw error;
  }
};

/**
 * Fetch a specific message by its ID.
 * GET /messenger/{messageId}/ on your backend.
 */
export const fetchMessageById = async (messageId: string): Promise<Message> => {
  try {
    const response = await axios.get(`/messenger/${messageId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error fetching message by ID');
    throw error;
  }
};

/**
 * Mark a specific message as read.
 * POST /messenger/{messageId}/mark_as_read/ on your backend.
 */
export const markMessageAsRead = async (messageId: string): Promise<void> => {
  try {
    await axios.post(`/messenger/${messageId}/mark_as_read/`);
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
    throw error;
  }
};
