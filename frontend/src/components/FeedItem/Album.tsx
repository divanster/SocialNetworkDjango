import React from 'react';
import { Album as AlbumType } from '../../types/album';

interface AlbumProps {
  album: AlbumType;
  onDelete: (id: number) => void;
}

const Album: React.FC<AlbumProps> = ({ album, onDelete }) => {
  const handleDelete = () => {
    onDelete(album.id);
  };

  return (
    <div className="album">
      <h2>{album.title}</h2>
      <p>{album.description}</p>
      <button onClick={handleDelete}>Delete Album</button>
      <div className="photos">
        {album.photos && album.photos.length > 0 ? (
          album.photos.map((photo) => (
            <div key={photo.id} className="photo">
              <img src={photo.image} alt={photo.description} />
              <p>{photo.description}</p>
            </div>
          ))
        ) : (
          <p>No photos available</p>
        )}
      </div>
    </div>
  );
};

export default Album;
