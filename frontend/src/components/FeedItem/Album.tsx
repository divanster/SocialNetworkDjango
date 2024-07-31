// frontend/src/components/FeedItem/Album.tsx
import React from 'react';

interface AlbumProps {
    album: {
        id: number;
        title: string;
        description: string;
        user: string;
        created_at: string;
        photos: { id: number; image: string; description: string }[];
    };
}

const Album: React.FC<AlbumProps> = ({ album }) => {
    return (
        <div className="album">
            <h2>{album.title}</h2>
            <p>{album.description}</p>
            <p><strong>User:</strong> {album.user}</p>
            <div>
                <strong>Photos:</strong>
                {album.photos.map(photo => (
                    <img key={photo.id} src={photo.image} alt="Album" style={{ width: '100%', height: 'auto' }} />
                ))}
            </div>
            <p className="text-muted">
                Created on {new Date(album.created_at).toLocaleDateString()}
            </p>
        </div>
    );
};

export default Album;
