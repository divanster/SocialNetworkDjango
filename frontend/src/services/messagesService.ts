// frontend/src/services/messagesService.ts
import axios from 'axios';
import { handleApiError } from './api';

export interface User {
  id: string; // UUID as a string
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

// Helper: transform raw API message into our Message type.
// Our API returns sender and receiver as IDs, plus sender_name, receiver_name, etc.
// Optionally, if your API returns profile picture URLs, include them.
const transformMessage = (msg: any): Message => {
  return {
    id: msg.id,
    sender: {
      id: msg.sender,
      username: msg.sender_name,
      full_name: msg.sender_full_name,
      profile_picture: msg.sender_profile_picture || null,
    },
    receiver: {
      id: msg.receiver,
      username: msg.receiver_name,
      full_name: msg.receiver_full_name,
      profile_picture: msg.receiver_profile_picture || null,
    },
    content: msg.content,
    read: msg.read,
    created_at: msg.created_at,
  };
};

/**
 * Fetch inbox messages.
 * GET /messenger/inbox/
 */
export const fetchInboxMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get('/messenger/inbox/');
    let data = response.data;
    if (data && Array.isArray(data.results)) {
      data = data.results;
    }
    return data.map(transformMessage);
  } catch (error) {
    handleApiError(error, 'Error fetching inbox messages');
    return [];
  }
};

/**
 * Send a message to a specific user.
 * POST /messenger/
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
    return transformMessage(response.data);
  } catch (error) {
    handleApiError(error, 'Error sending message to user');
    throw error;
  }
};

/**
 * Fetch a specific message by its ID.
 * GET /messenger/{messageId}/
 */
export const fetchMessageById = async (messageId: string): Promise<Message> => {
  try {
    const response = await axios.get(`/messenger/${messageId}/`);
    return transformMessage(response.data);
  } catch (error) {
    handleApiError(error, 'Error fetching message by ID');
    throw error;
  }
};

/**
 * Mark a message as read.
 * POST /messenger/{messageId}/mark_as_read/
 */
export const markMessageAsRead = async (messageId: string): Promise<void> => {
  try {
    await axios.post(`/messenger/${messageId}/mark_as_read/`);
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
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
    let data = response.data;
    if (data && Array.isArray(data.results)) {
      data = data.results;
    }
    return data.map(transformMessage);
  } catch (error) {
    handleApiError(error, 'Error broadcasting message');
    throw error;
  }
};
