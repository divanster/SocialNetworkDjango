import React from 'react';
import { Album as AlbumType } from '../../types/album';

interface AlbumProps {
    album: AlbumType;
}

const Album: React.FC<AlbumProps> = ({ album }) => {
    return (
        <div className="album">
            <h2>{album.title}</h2>
            <p>{album.description}</p>
            <div className="photos">
                {album.photos.map(photo => (
                    <div key={photo.id} className="photo">
                        <img src={photo.image} alt={photo.description} />
                        <p>{photo.description}</p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default Album;
