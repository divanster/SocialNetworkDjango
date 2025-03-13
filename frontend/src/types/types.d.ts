// src/types/custom.d.ts

export type PostData = {
  id: number;
  title: string;
  content: string;
  created_at: string;
  updated_at: string;
  author: string;
  images: string[];
  ratings: any[];
  tags: any[];
};

declare global {
  interface WindowEventMap {
    'ws-user_online': CustomEvent<any>;
    'ws-user_offline': CustomEvent<any>;
  }
}
