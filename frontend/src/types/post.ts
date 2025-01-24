// frontend/src/types/post.ts

export interface Post {
  id: string; // Changed from number to string
  title: string;
  content: string;
  author?: {
    id: string;
    username: string;
    // Add other fields if necessary
  };
  created_at?: string;
  updated_at?: string;
  // Add or remove optional fields as necessary
  tags?: {
    id: string; // string if you use UUID
    name: string;
  }[];
  images?: {
    id: string; // string if you use UUID
    image: string;
  }[];
  ratings?: {
    id: string; // string if you use UUID
    value: number;
    user: string; // string if user IDs are UUID
  }[];
}
