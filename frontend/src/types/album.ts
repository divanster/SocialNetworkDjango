// types/album.ts
export interface Album {
    id: number;
    title: string;
    description: string;
    user: string;
    created_at: string;
    photos: { id: number; image: string; description: string }[];
}
