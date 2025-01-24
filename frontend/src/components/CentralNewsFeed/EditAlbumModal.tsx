import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { Album as AlbumType } from '../../types/album';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

interface EditAlbumModalProps {
  show: boolean;
  onHide: () => void;
  album: AlbumType;
  onSave: (updatedAlbum: AlbumType) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const EditAlbumModal: React.FC<EditAlbumModalProps> = ({ show, onHide, album, onSave }) => {
  const { token } = useAuth();
  const [title, setTitle] = useState<string>(album.title);
  const [description, setDescription] = useState<string>(album.description);
  const validVisibilities = ['public', 'friends', 'private'] as const;
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>(
    validVisibilities.includes(album.visibility as 'public' | 'friends' | 'private')
      ? (album.visibility as 'public' | 'friends' | 'private')
      : 'public'
  );
  const [images, setImages] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  useEffect(() => {
    if (show) {
      setTitle(album.title);
      setDescription(album.description);
      setVisibility(
        validVisibilities.includes(album.visibility as 'public' | 'friends' | 'private')
          ? (album.visibility as 'public' | 'friends' | 'private')
          : 'public'
      );
      setImages(null);
      setError(null);
    }
  }, [show, album]);

  const handleSave = async () => {
    if (title.trim() === '' || description.trim() === '') {
      setError('Title and description cannot be empty.');
      return;
    }

    if (!token) {
      setError('You must be logged in to update an album.');
      return;
    }

    setSaving(true);
    setError(null);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('visibility', visibility);
    if (images) {
      Array.from(images).forEach((file) => formData.append('image_files', file));
    }

    try {
      const response = await axios.put(`${API_URL}/albums/${album.id}/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      const updatedAlbum: AlbumType = response.data;
      onSave(updatedAlbum);
      onHide();
    } catch (err: any) {
      console.error('Error updating album:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'Failed to update album.');
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleClose = () => {
    setError(null);
    onHide();
  };

  return (
    <Modal show={show} onHide={handleClose} centered>
      <Modal.Header closeButton>
        <Modal.Title>Edit Album</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form>
          <Form.Group controlId="formAlbumTitle">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter album title"
              required
            />
          </Form.Group>
          <Form.Group controlId="formAlbumDescription" className="mt-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Enter album description"
              required
            />
          </Form.Group>
          <Form.Group controlId="formAlbumVisibility" className="mt-3">
            <Form.Label>Visibility</Form.Label>
            <Form.Select
              value={visibility}
              onChange={(e) => setVisibility(e.target.value as 'public' | 'friends' | 'private')}
              required
            >
              <option value="public">Public</option>
              <option value="friends">Friends</option>
              <option value="private">Private</option>
            </Form.Select>
          </Form.Group>
          <Form.Group controlId="formAlbumImages" className="mt-3">
            <Form.Label>Upload New Photos</Form.Label>
            <Form.Control
              type="file"
              multiple
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                if (e.target.files) {
                  setImages(e.target.files);
                }
              }}
              accept="image/*"
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={handleClose} disabled={saving}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave} disabled={saving}>
          {saving ? (
            <>
              <Spinner
                as="span"
                animation="border"
                size="sm"
                role="status"
                aria-hidden="true"
              />{' '}
              Saving...
            </>
          ) : (
            'Save Changes'
          )}
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default EditAlbumModal;
