export const profileBasePath = '/profile';
export const friendsBasePath = '/friends';

export const hasValidUserId = (userId?: string | null): userId is string =>
  typeof userId === 'string' && userId.trim().length > 0;

export const buildProfilePath = (userId?: string | null): string => {
  if (!hasValidUserId(userId)) {
    return profileBasePath;
  }
  return `${profileBasePath}/${encodeURIComponent(userId)}`;
};

export const buildMessengerPathForUser = (userId: string): string =>
  `/messenger?userId=${encodeURIComponent(userId)}`;
