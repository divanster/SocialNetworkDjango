// types/post.ts

export interface Post {
    id: number;
    title: string;
    content: string;
    author: string;
    created_at: string;
    updated_at: string;
    tags: { id: number; name: string }[];
    images: { id: number; image: string }[];
    ratings: { id: number; value: number; user: number }[];
}
