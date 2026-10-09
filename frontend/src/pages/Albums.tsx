import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Alert, Button, Spinner } from 'react-bootstrap';
import { Link } from 'react-router-dom';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';
import AlbumCard from '../components/FeedItem/Album';
import { useAuth } from '../contexts/AuthContext';
import { Album } from '../types/album';
import { deleteAlbum, listAlbums } from '../services/contentService';
import { profileBasePath } from '../utils/profileRoutes';
import './AlbumsPage.css';

const Albums: React.FC = () => {
  const { user } = useAuth();
  const [albums, setAlbums] = useState<Album[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadAlbums = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listAlbums();
      setAlbums(data);
    } catch {
      setError('Failed to load albums.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAlbums();
  }, [loadAlbums]);

  const handleAlbumCreated = (newAlbum: Album) => {
    setAlbums((prev) => [newAlbum, ...prev]);
  };

  const handleAlbumUpdated = (updatedAlbum: Album) => {
    setAlbums((prev) => prev.map((album) => (album.id === updatedAlbum.id ? updatedAlbum : album)));
  };

  const handleAlbumDeleted = async (albumId: string) => {
    try {
      await deleteAlbum(albumId);
      setAlbums((prev) => prev.filter((album) => album.id !== albumId));
    } catch {
      setError('Failed to delete album.');
    }
  };

  const myAlbumsCount = useMemo(
    () => albums.filter((album) => user?.id && album.user_id === user.id).length,
    [albums, user?.id]
  );

  return (
    <div className="albums-page">
      <div className="albums-page__header">
        <div>
          <h1 className="albums-page__title">Albums</h1>
          <p className="albums-page__subtitle">
            Manage your albums and explore albums shared with you.
          </p>
        </div>
        <Link className="btn btn-outline-secondary" to={profileBasePath}>
          Back to profile
        </Link>
      </div>

      <div className="albums-page__create">
        <h2>Create album</h2>
        <CreateAlbum onAlbumCreated={handleAlbumCreated} sendAlbumMessage={() => undefined} />
      </div>

      <div className="albums-page__summary">
        <span>Total albums: {albums.length}</span>
        <span>Your albums: {myAlbumsCount}</span>
      </div>

      {loading ? (
        <div className="albums-page__loading" role="status" aria-live="polite">
          <Spinner animation="border" size="sm" className="me-2" />
          Loading albums...
        </div>
      ) : (
        <>
          {error && (
            <Alert variant="danger" className="d-flex justify-content-between align-items-center">
              <span>{error}</span>
              <Button variant="outline-danger" size="sm" onClick={loadAlbums}>
                Retry
              </Button>
            </Alert>
          )}

          {!error && albums.length === 0 && (
            <div className="albums-empty-state">
              <h3>No albums yet</h3>
              <p>Create your first album to start sharing photos.</p>
            </div>
          )}

          <div className="albums-page__list">
            {albums.map((album) => (
              <AlbumCard
                key={album.id}
                album={album}
                onDelete={handleAlbumDeleted}
                onUpdate={handleAlbumUpdated}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Albums;
