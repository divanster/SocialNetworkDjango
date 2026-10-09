import axios from 'axios';
import { handleApiError } from './api';

export interface NotificationItem {
  id: string;
  notification_type: string;
  text: string;
  read: boolean;
  created_at: string;
  sender_id?: string | null;
  sender_username?: string | null;
  receiver_id?: string | null;
  receiver_username?: string | null;
  content_type?: number | null;
  object_id?: string | null;
  content_object_url?: string | null;
}

const asArray = (payload: any): NotificationItem[] => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export const listNotifications = async (): Promise<NotificationItem[]> => {
  try {
    const response = await axios.get('/notifications/');
    return asArray(response.data);
  } catch (error) {
    handleApiError(error, 'Error listing notifications');
    throw error;
  }
};

export const markNotificationAsRead = async (notificationId: string): Promise<void> => {
  try {
    await axios.post(`/notifications/${notificationId}/mark_as_read/`);
  } catch (error) {
    handleApiError(error, `Error marking notification as read: ${notificationId}`);
    throw error;
  }
};

export const markAllNotificationsAsRead = async (): Promise<void> => {
  try {
    await axios.post('/notifications/mark_all_as_read/');
  } catch (error) {
    handleApiError(error, 'Error marking all notifications as read');
    throw error;
  }
};
