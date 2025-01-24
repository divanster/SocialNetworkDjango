// frontend/src/components/FeedItem/Album.tsx

import React from 'react';
import { Album as AlbumType } from '../../types/album';
import './Album.css'; // Ensure Album.css exists or remove this line

interface AlbumProps {
  album: AlbumType;
  onDelete: (id: string) => void;
  onUpdate: (album: AlbumType) => void;
}

const Album: React.FC<AlbumProps> = ({ album, onDelete, onUpdate }) => {
  // Use optional chaining and default values to prevent runtime errors
  const authorFullName = album.author?.full_name || 'Unknown Author';
  const authorProfilePicture = album.author?.profile_picture || '/default-profile.png';
  const authorUsername = album.author?.username || 'unknown_user';

  return (
    <div className="album-card">
      <div className="album-header">
        <img src={authorProfilePicture} alt={`${authorUsername}'s profile`} />
        <div>
          <strong>{authorFullName}</strong>
          <span>{new Date(album.created_at).toLocaleString()}</span>
        </div>
        <button onClick={() => onDelete(album.id)} className="delete-button">
          &times;
        </button>
      </div>
      <div className="album-content">
        <h3>{album.title}</h3>
        <p>{album.description}</p>
        {/* Render album photos or other details */}
      </div>
      {/* Optionally, include an edit button */}
      <button onClick={() => onUpdate(album)} className="edit-button">
        Edit
      </button>
    </div>
  );
};

export default Album;
