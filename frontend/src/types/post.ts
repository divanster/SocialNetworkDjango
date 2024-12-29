// frontend/src/types/post.ts

export interface User {
  id: number;
  username: string;
  email: string;
  // Add other user-related fields as needed
}

export interface Image {
  id: number;
  image: string; // URL or path to the image
}

export interface Post {
  id: number;
  title: string;
  content: string;
  user: User; // Updated to include 'user' as an object
  visibility: string; // or use an enum if defined
  created_at: string;
  updated_at: string;
  images?: Image[]; // Optional array of images
}
