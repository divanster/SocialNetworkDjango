// frontend/src/types/post.ts
export interface Post {
  id: string;                // UUID
  title: string;
  content: string;
  author?: {                  // your API must return this object
    id: string;
    username: string;
  };
  user?: string;
  created_at?: string;
  updated_at?: string;
  images?: { id: string; image: string }[];
  tags?: { tagged_user_id: string; tagged_user_username: string | null }[];
  reactions_count?: number;   // your feed endpoint should provide this
  comments_count?: number;    // and this
}
