// src/services/messagesService.ts

import {
  fetchMessages,
  sendMessage,
  broadcastMessage,
  fetchMessageByIdAPI,
  markMessageAsReadAPI,
} from './api';
import { handleApiError } from './api';
import { User } from './friendsService'; // Adjust if necessary

// Exported Message Interface
export interface Message {
  id: string; // UUID as string
  sender: User;
  receiver: User;
  content: string;
  read: boolean; // Aliased from 'is_read'
  created_at: string;
}

// Fetch inbox messages
export const fetchInboxMessages = async (): Promise<Message[]> => {
  try {
    const messages = await fetchMessages();
    return messages;
  } catch (error) {
    handleApiError(error, 'Error fetching inbox messages');
    return [];
  }
};

// Send a message to a specific user
export const sendMessageToUser = async (receiverId: number, content: string): Promise<Message> => {
  try {
    const message = await sendMessage(receiverId, content);
    return message;
  } catch (error) {
    handleApiError(error, 'Error sending message to user');
    throw error;
  }
};

// Broadcast a message to all users
export const broadcastMessageToAll = async (content: string): Promise<Message[]> => {
  try {
    const messages = await broadcastMessage(content);
    return messages;
  } catch (error) {
    handleApiError(error, 'Error broadcasting message to all users');
    throw error;
  }
};

// Fetch a specific message by ID
export const fetchMessageById = async (messageId: string): Promise<Message> => {
  try {
    const message = await fetchMessageByIdAPI(messageId);
    return message;
  } catch (error) {
    handleApiError(error, 'Error fetching message by ID');
    throw error;
  }
};

// Mark a message as read
export const markMessageAsRead = async (messageId: string): Promise<any> => {
  try {
    const response = await markMessageAsReadAPI(messageId);
    return response;
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
    throw error;
  }
};
