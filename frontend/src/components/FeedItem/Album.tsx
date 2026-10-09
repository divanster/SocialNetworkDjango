import React from 'react';
import { Link } from 'react-router-dom';
import { Album as AlbumType } from '../../types/album';
import EditAlbumModal from '../CentralNewsFeed/EditAlbumModal';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import { useAuth } from '../../contexts/AuthContext';
import { buildAlbumPath } from '../../utils/profileRoutes';
import './Album.css';

interface AlbumProps {
  album: AlbumType;
  onDelete?: (id: string) => void;
  onUpdate?: (album: AlbumType) => void;
}

const Album: React.FC<AlbumProps> = ({ album, onDelete, onUpdate }) => {
  const { user } = useAuth();
  const [showEditModal, setShowEditModal] = React.useState(false);
  const authorFullName = album.author?.full_name || 'Unknown Author';
  const authorUsername = album.author?.username || 'unknown_user';
  const authorId = album.author?.id;
  const canManage = Boolean(user?.id && album.user_id === user.id);
  const photoCount = Array.isArray(album.photos) ? album.photos.length : 0;

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
        {canManage && onDelete && (
          <button
            onClick={() => {
              if (window.confirm('Delete this album?')) onDelete(album.id);
            }}
            className="delete-button"
            aria-label="Delete album"
            type="button"
          >
            &times;
          </button>
        )}
      </div>
      <div className="album-content">
        <h3>
          <Link to={buildAlbumPath(album.id)} className="album-title-link">
            {album.title}
          </Link>
        </h3>
        <p>{album.description}</p>
        {Array.isArray(album.tags) && album.tags.length > 0 && (
          <div className="mb-2">
            <small className="text-muted me-1">Tagged:</small>
            {album.tags.map((tag) => (
              <UserIdentityLink
                key={tag.id}
                userId={tag.tagged_user?.id}
                className="me-2"
              >
                @{tag.tagged_user?.username || 'user'}
              </UserIdentityLink>
            ))}
          </div>
        )}
        <small className="text-muted d-block mt-1">
          Visibility: {album.visibility}
          {photoCount > 0 ? ` • ${photoCount} photo${photoCount > 1 ? 's' : ''}` : ''}
        </small>
      </div>
      <div className="album-actions-row">
        <Link to={buildAlbumPath(album.id)} className="btn btn-outline-primary btn-sm">
          Open Album
        </Link>
        {canManage && onUpdate && (
          <button
            onClick={() => setShowEditModal(true)}
            className="edit-button btn btn-primary btn-sm"
            type="button"
          >
            Edit
          </button>
        )}
      </div>
      {canManage && onUpdate && (
        <EditAlbumModal
          show={showEditModal}
          onHide={() => setShowEditModal(false)}
          album={album}
          onSave={onUpdate}
        />
      )}
    </div>
  );
};

export default Album;
