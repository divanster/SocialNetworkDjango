// frontend/src/components/FeedItem/Album.tsx

import React, { useState } from 'react';
import { Album as AlbumType } from '../../types/album';
import { Card, Button, Spinner } from 'react-bootstrap';
import EditAlbumModal from '../CentralNewsFeed/EditAlbumModal';

interface AlbumProps {
  album: AlbumType;
  onDelete: (id: number) => Promise<void>;
  onUpdate: (updatedAlbum: AlbumType) => void; // Ensure this is present
}

const Album: React.FC<AlbumProps> = ({ album, onDelete, onUpdate }) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);

  const handleEditClick = () => {
    setShowModal(true);
    console.log(`Editing album with ID ${album.id}`);
  };

  const handleSave = (updatedAlbum: AlbumType) => {
    onUpdate(updatedAlbum);
    console.log(`Album with ID ${updatedAlbum.id} updated.`);
    setShowModal(false);
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <>
      <Card className="mb-3">
        <Card.Body>
          <Card.Title>{album.title}</Card.Title>
          <Card.Subtitle className="mb-2 text-muted">
            By {album.user} on {new Date(album.created_at).toLocaleString()}
          </Card.Subtitle>
          <Card.Text>{album.description}</Card.Text>
          {album.photos && album.photos.length > 0 && (
            <div className="mb-2">
              {album.photos.map((photo) => (
                <img
                  key={photo.id}
                  src={photo.image}
                  alt="Album"
                  style={{ width: '100px', marginRight: '10px', borderRadius: '8px' }}
                />
              ))}
            </div>
          )}
          {/* Action Buttons */}
          <Button
            variant="primary"
            className="me-2"
            onClick={handleEditClick}
            disabled={saving}
          >
            {saving ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />{' '}
                Updating...
              </>
            ) : (
              'Update'
            )}
          </Button>
          <Button
            variant="danger"
            onClick={() => {
              if (window.confirm('Are you sure you want to delete this album?')) {
                onDelete(album.id);
              }
            }}
            disabled={saving}
          >
            {saving ? (
              <>
                <Spinner
                  as="span"
                  animation="border"
                  size="sm"
                  role="status"
                  aria-hidden="true"
                />{' '}
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </Button>
        </Card.Body>
      </Card>

      {/* Edit Album Modal */}
      {showModal && (
        <EditAlbumModal
          show={showModal}
          onHide={handleCloseModal}
          album={album}
          onSave={handleSave}
        />
      )}
    </>
  );
};

export default Album;
