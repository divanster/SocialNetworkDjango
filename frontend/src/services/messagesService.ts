// frontend/src/services/messagesService.ts

import axios from 'axios';
import { handleApiError } from './api';

export interface User {
  id: number;
  username: string;
  full_name: string;
  profile_picture: string | null;
}

export interface Message {
  id: string;       // UUID as string
  sender: User;     // Sender's user object
  receiver: User;   // Receiver's user object
  content: string;
  read: boolean;    // True if the message has been read
  created_at: string;
}

/**
 * Fetch inbox messages.
 * Calls GET /messenger/inbox/ on your backend.
 */
export const fetchInboxMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get('/messenger/inbox/');
    // If a paginated response is returned, use its "results" property.
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
 * POST /messenger/ to create a new message.
 */
export const sendMessageToUser = async (
  receiverId: number,
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
 * POST /messenger/broadcast/
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
 * GET /messenger/<messageId>/
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
 * Mark a message as read.
 * POST /messenger/<messageId>/mark_as_read/
 */
export const markMessageAsRead = async (messageId: string): Promise<void> => {
  try {
    await axios.post(`/messenger/${messageId}/mark_as_read/`);
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
    throw error;
  }
};
