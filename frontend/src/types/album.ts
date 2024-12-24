// frontend/src/types/album.ts

export interface Photo {
    id: number;
    image: string;
    description: string;
}

export interface Album {
    id: number;
    title: string;
    description: string;
    user: string;
    visibility: 'public' | 'friends' | 'private';
    created_at: string;
    photos: Photo[];
}
