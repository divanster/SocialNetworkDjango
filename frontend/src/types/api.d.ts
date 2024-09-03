// src/types/api.d.ts
declare module 'services/api' {
  export const fetchProfileData: () => Promise<any>;
  export const updateProfileData: (formData: FormData) => Promise<any>;
  export const fetchNewsFeed: () => Promise<any>;
  export const fetchNotificationsCount: () => Promise<number>;
  export const fetchMessagesCount: () => Promise<number>;
  export const sendMessage: (receiverId: number, content: string) => Promise<any>;
  export const fetchMessages: () => Promise<any>;
  export const fetchUsers: () => Promise<any>; // Add fetchUsers function here
  // Add other functions as needed
}
