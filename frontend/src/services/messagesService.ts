// frontend/src/services/messagesService.ts

import {
  fetchMessages,
  sendMessage as sendMessageAPI,
  broadcastMessage as broadcastMessageAPI,
  fetchMessageByIdAPI,
  markMessageAsReadAPI,
} from './api';

// Fetch inbox messages
export const fetchInboxMessages = async () => {
  try {
    const messages = await fetchMessages();
    return messages;
  } catch (error) {
    console.error('Error fetching inbox messages:', error);
    throw error;
  }
};

// Send a message to a specific user
export const sendMessage = async (receiverId: number, content: string) => {
  try {
    const message = await sendMessageAPI(receiverId, content);
    return message;
  } catch (error) {
    console.error('Error sending message:', error);
    throw error;
  }
};

// Broadcast a message to all users
export const broadcastMessage = async (content: string) => {
  try {
    const messages = await broadcastMessageAPI(content);
    return messages;
  } catch (error) {
    console.error('Error broadcasting message:', error);
    throw error;
  }
};

// Fetch a specific message by ID
export const fetchMessageById = async (messageId: string) => {
  try {
    const message = await fetchMessageByIdAPI(messageId);
    return message;
  } catch (error) {
    console.error('Error fetching message by ID:', error);
    throw error;
  }
};

// Mark a message as read
export const markMessageAsRead = async (messageId: string) => {
  try {
    const result = await markMessageAsReadAPI(messageId);
    return result;
  } catch (error) {
    console.error('Error marking message as read:', error);
    throw error;
  }
};
