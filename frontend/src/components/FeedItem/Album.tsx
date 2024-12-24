// frontend/src/components/FeedItem/Album.tsx

import React from 'react';
import { Album as AlbumType } from '../../types/album';
import { Card, Button } from 'react-bootstrap';

interface AlbumProps {
  album: AlbumType;
  onDelete: (id: number) => void;
}

const Album: React.FC<AlbumProps> = ({ album, onDelete }) => {
  return (
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
                style={{ width: '100px', marginRight: '10px' }}
              />
            ))}
          </div>
        )}
        <Button variant="danger" onClick={() => onDelete(album.id)}>
          Delete
        </Button>
        {/* Add an update button or modal as needed */}
      </Card.Body>
    </Card>
  );
};

export default Album;
