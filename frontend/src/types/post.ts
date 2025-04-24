// frontend/src/types/post.ts
export interface Post {
  id: string;                // UUID
  title: string;
  content: string;
  author?: {                  // your API must return this object
    id: string;
    username: string;
  };
  created_at?: string;
  updated_at?: string;
  images?: { id: string; image: string }[];
  reactions_count?: number;   // your feed endpoint should provide this
  comments_count?: number;    // and this
}
