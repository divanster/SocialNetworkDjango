// frontend/src/components/FeedItem/Album.tsx

import React from 'react';
import { Album as AlbumType } from '../../types/album';
import EditAlbumModal from '../CentralNewsFeed/EditAlbumModal';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import './Album.css'; // Ensure Album.css exists or remove this line

interface AlbumProps {
  album: AlbumType;
  onDelete: (id: string) => void;
  onUpdate: (album: AlbumType) => void;
}

const Album: React.FC<AlbumProps> = ({ album, onDelete, onUpdate }) => {
  const [showEditModal, setShowEditModal] = React.useState(false);
  // Use optional chaining and default values to prevent runtime errors
  const authorFullName = album.author?.full_name || 'Unknown Author';
  const authorUsername = album.author?.username || 'unknown_user';
  const authorId = album.author?.id;

  return (
    <div className="album-card">
      <div className="album-header">
        <UserIdentityLink userId={authorId} className="album-author-link" ariaLabel={`Open ${authorFullName} profile`}>
          <Avatar
            size={50}
            src={album.author?.profile_picture || undefined}
            name={authorFullName}
            alt={`${authorUsername} avatar`}
          />
          <div>
            <strong>{authorFullName}</strong>
            <span>{new Date(album.created_at).toLocaleString()}</span>
          </div>
        </UserIdentityLink>
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
      <button onClick={() => setShowEditModal(true)} className="edit-button">
        Edit
      </button>
      <EditAlbumModal
        show={showEditModal}
        onHide={() => setShowEditModal(false)}
        album={album}
        onSave={onUpdate}
      />
    </div>
  );
};

export default Album;
