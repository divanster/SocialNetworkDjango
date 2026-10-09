import { buildAlbumPath, buildMessengerPathForUser, buildProfilePath } from './profileRoutes';
import { NotificationItem } from '../services/notificationsService';

export interface NotificationDestination {
  path: string | null;
  canNavigate: boolean;
}

const userProfileTypes = new Set([
  'follow',
  'friend_request',
  'friend_added',
  'friend_removed',
  'accepted_request',
  'update',
  'welcome',
]);

const albumTypes = new Set(['album_created', 'album', 'photo', 'photo_created', 'photo_updated']);
const storyTypes = new Set(['story', 'story_created']);
const postTypes = new Set(['post', 'social_event', 'comment', 'reaction']);
const taggingTypes = new Set(['tag', 'tagged']);

export const resolveNotificationDestination = (
  notification: NotificationItem
): NotificationDestination => {
  const type = (notification.notification_type || '').toLowerCase();
  const senderId = notification.sender_id ? String(notification.sender_id) : null;
  const objectId = notification.object_id ? String(notification.object_id) : null;

  if (type === 'message') {
    if (senderId) {
      return { canNavigate: true, path: buildMessengerPathForUser(senderId) };
    }
    return { canNavigate: true, path: '/messenger' };
  }

  if (userProfileTypes.has(type)) {
    if (senderId) {
      return { canNavigate: true, path: buildProfilePath(senderId) };
    }
    return { canNavigate: true, path: '/friends' };
  }

  if (albumTypes.has(type) && objectId) {
    return { canNavigate: true, path: buildAlbumPath(objectId) };
  }

  if (storyTypes.has(type) || postTypes.has(type) || taggingTypes.has(type)) {
    return { canNavigate: false, path: null };
  }

  if (senderId) {
    return { canNavigate: true, path: buildProfilePath(senderId) };
  }

  return { canNavigate: false, path: null };
};
