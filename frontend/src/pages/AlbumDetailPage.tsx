import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { Alert, Button, Form, Modal, Spinner } from 'react-bootstrap';
import { Link, useParams } from 'react-router-dom';
import Avatar from '../components/Common/Avatar';
import UserIdentityLink from '../components/Common/UserIdentityLink';
import { useAuth } from '../contexts/AuthContext';
import { Album, Photo } from '../types/album';
import {
  deletePhoto,
  getAlbumById,
  listPhotos,
  updatePhoto,
  uploadPhoto,
} from '../services/contentService';
import { albumsBasePath } from '../utils/profileRoutes';
import './AlbumDetailPage.css';

const AlbumDetailPage: React.FC = () => {
  const { albumId } = useParams<{ albumId: string }>();
  const { user } = useAuth();
  const [album, setAlbum] = useState<Album | null>(null);
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [notFound, setNotFound] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [photoToPreview, setPhotoToPreview] = useState<Photo | null>(null);
  const [editingPhotoId, setEditingPhotoId] = useState<string | null>(null);
  const [editingDescription, setEditingDescription] = useState<string>('');

  const canManage = useMemo(
    () => Boolean(user?.id && album?.user_id && user.id === album.user_id),
    [user?.id, album?.user_id]
  );

  const loadAlbum = useCallback(async () => {
    if (!albumId) {
      setNotFound(true);
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    setNotFound(false);
    try {
      const [albumData, photosData] = await Promise.all([getAlbumById(albumId), listPhotos(albumId)]);
      setAlbum(albumData);
      setPhotos(photosData);
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setNotFound(true);
      } else {
        setError('Failed to load album details.');
      }
    } finally {
      setLoading(false);
    }
  }, [albumId]);

  useEffect(() => {
    loadAlbum();
  }, [loadAlbum]);

  const handleUploadPhotos = async (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!albumId || !event.target.files || event.target.files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      const files = Array.from(event.target.files);
      for (const file of files) {
        const formData = new FormData();
        formData.append('album', albumId);
        formData.append('image', file);
        await uploadPhoto(formData);
      }
      await loadAlbum();
      event.target.value = '';
    } catch {
      setError('Failed to upload photo.');
    } finally {
      setUploading(false);
    }
  };

  const handleDeletePhoto = async (photoId: string) => {
    if (!window.confirm('Delete this photo?')) return;
    try {
      await deletePhoto(photoId);
      setPhotos((prev) => prev.filter((photo) => photo.id !== photoId));
      if (photoToPreview?.id === photoId) {
        setPhotoToPreview(null);
      }
    } catch {
      setError('Failed to delete photo.');
    }
  };

  const startEditPhotoDescription = (photo: Photo) => {
    setEditingPhotoId(photo.id);
    setEditingDescription(photo.description || '');
  };

  const cancelEditPhotoDescription = () => {
    setEditingPhotoId(null);
    setEditingDescription('');
  };

  const submitEditPhotoDescription = async (photoId: string) => {
    const formData = new FormData();
    formData.append('description', editingDescription);
    try {
      const updated = await updatePhoto(photoId, formData);
      setPhotos((prev) => prev.map((photo) => (photo.id === photoId ? updated : photo)));
      cancelEditPhotoDescription();
    } catch {
      setError('Failed to update photo description.');
    }
  };

  if (loading) {
    return (
      <div className="album-detail-page__loading" role="status" aria-live="polite">
        <Spinner animation="border" size="sm" className="me-2" />
        Loading album...
      </div>
    );
  }

  if (notFound || !album) {
    return (
      <div className="album-detail-page">
        <Alert variant="warning">
          Album not found or unavailable.
        </Alert>
        <Link className="btn btn-outline-primary" to={albumsBasePath}>
          Back to albums
        </Link>
      </div>
    );
  }

  return (
    <div className="album-detail-page">
      <div className="album-detail-page__header">
        <div className="album-detail-page__identity">
          <UserIdentityLink userId={album.author?.id}>
            <Avatar
              size={48}
              src={album.author?.profile_picture}
              name={album.author?.full_name || album.author?.username || 'Unknown'}
              alt="Album owner avatar"
            />
          </UserIdentityLink>
          <div>
            <h1>{album.title}</h1>
            <div className="album-detail-page__meta">
              <UserIdentityLink userId={album.author?.id}>
                {album.author?.full_name || album.author?.username || 'Unknown user'}
              </UserIdentityLink>
              <span>{new Date(album.created_at).toLocaleString()}</span>
              <span>{album.visibility}</span>
            </div>
          </div>
        </div>
        <Link className="btn btn-outline-secondary" to={albumsBasePath}>
          Back
        </Link>
      </div>

      {album.description && <p className="album-detail-page__description">{album.description}</p>}

      {error && (
        <Alert variant="danger" className="d-flex justify-content-between align-items-center">
          <span>{error}</span>
          <Button size="sm" variant="outline-danger" onClick={loadAlbum}>
            Retry
          </Button>
        </Alert>
      )}

      {canManage && (
        <div className="album-detail-page__upload mb-3">
          <Form.Label htmlFor="album-photo-upload" className="fw-semibold">Upload photos</Form.Label>
          <Form.Control
            id="album-photo-upload"
            type="file"
            multiple
            accept="image/*"
            onChange={handleUploadPhotos}
            disabled={uploading}
          />
          {uploading && <div className="small mt-2">Uploading...</div>}
        </div>
      )}

      {photos.length === 0 ? (
        <div className="album-detail-page__empty">
          <h3>No photos in this album yet</h3>
          {canManage && <p>Upload photos to get started.</p>}
        </div>
      ) : (
        <div className="album-detail-page__grid">
          {photos.map((photo) => (
            <div className="album-photo-card" key={photo.id}>
              <button
                type="button"
                className="album-photo-preview-btn"
                onClick={() => setPhotoToPreview(photo)}
                aria-label="Open photo preview"
              >
                <img
                  src={photo.image}
                  alt={photo.description || 'Album photo'}
                  onError={(e) => {
                    e.currentTarget.src = 'https://via.placeholder.com/600x400?text=Image+Unavailable';
                  }}
                />
              </button>
              <div className="album-photo-card__body">
                {editingPhotoId === photo.id ? (
                  <>
                    <Form.Control
                      size="sm"
                      value={editingDescription}
                      onChange={(e) => setEditingDescription(e.target.value)}
                      placeholder="Photo description"
                    />
                    <div className="album-photo-card__actions">
                      <Button size="sm" onClick={() => submitEditPhotoDescription(photo.id)}>Save</Button>
                      <Button size="sm" variant="outline-secondary" onClick={cancelEditPhotoDescription}>Cancel</Button>
                    </div>
                  </>
                ) : (
                  <>
                    {photo.description && <p>{photo.description}</p>}
                    {canManage && (
                      <div className="album-photo-card__actions">
                        <Button size="sm" variant="outline-primary" onClick={() => startEditPhotoDescription(photo)}>
                          Edit
                        </Button>
                        <Button size="sm" variant="outline-danger" onClick={() => handleDeletePhoto(photo.id)}>
                          Delete
                        </Button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Modal show={Boolean(photoToPreview)} onHide={() => setPhotoToPreview(null)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Photo preview</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {photoToPreview && (
            <img
              src={photoToPreview.image}
              alt={photoToPreview.description || 'Album photo preview'}
              className="album-detail-page__preview-image"
              onError={(e) => {
                e.currentTarget.src = 'https://via.placeholder.com/900x600?text=Image+Unavailable';
              }}
            />
          )}
          {photoToPreview?.description && (
            <p className="mt-2 mb-0">{photoToPreview.description}</p>
          )}
        </Modal.Body>
      </Modal>
    </div>
  );
};

export default AlbumDetailPage;
