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

export const transformMessage = (msg: any): Message => {
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

const asArray = (payload: any): any[] => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export const fetchMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get('/messenger/');
    return asArray(response.data).map(transformMessage);
  } catch (error) {
    handleApiError(error, 'Error fetching messages');
    throw error;
  }
};

export const fetchInboxMessages = async (): Promise<Message[]> => {
  try {
    const response = await axios.get('/messenger/inbox/');
    return asArray(response.data).map(transformMessage);
  } catch (error) {
    handleApiError(error, 'Error fetching inbox messages');
    throw error;
  }
};

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

export const fetchMessageById = async (messageId: string): Promise<Message> => {
  try {
    const response = await axios.get(`/messenger/${messageId}/`);
    return transformMessage(response.data);
  } catch (error) {
    handleApiError(error, `Error fetching message by id: ${messageId}`);
    throw error;
  }
};

export const markMessageAsRead = async (messageId: string): Promise<void> => {
  try {
    await axios.post(`/messenger/${messageId}/mark_as_read/`);
  } catch (error) {
    handleApiError(error, 'Error marking message as read');
    throw error;
  }
};
