// frontend/src/components/FeedItem/Album.tsx
import React from 'react';

interface AlbumProps {
    album: {
        id: number;
        user: number;
        title: string;
        description: string;
        created_at: string;
        updated_at: string;
        photos: { id: number; album: number; image: string; description: string; created_at: string }[];
    };
}

const Album: React.FC<AlbumProps> = ({ album }) => {
    return (
        <div className="album">
            <h3>{album.title}</h3>
            <p>{album.description}</p>
        </div>
    );
};

export default Album;
