import React, { useState, useEffect } from 'react';
import { Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { Album as AlbumType } from '../../types/album';
import { updateAlbum } from '../../services/contentService';

interface EditAlbumModalProps {
  show: boolean;
  onHide: () => void;
  album: AlbumType;
  onSave: (updatedAlbum: AlbumType) => void;
}

const EditAlbumModal: React.FC<EditAlbumModalProps> = ({ show, onHide, album, onSave }) => {
  const [title, setTitle] = useState<string>(album.title);
  const [description, setDescription] = useState<string>(album.description);
  const validVisibilities = ['public', 'friends', 'private'] as const;
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>(
    validVisibilities.includes(album.visibility as 'public' | 'friends' | 'private')
      ? (album.visibility as 'public' | 'friends' | 'private')
      : 'public'
  );
  const [images, setImages] = useState<File[]>([]);
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
      setImages([]);
      setError(null);
    }
  }, [show, album]);

  const handleSave = async () => {
    if (title.trim() === '' || description.trim() === '') {
      setError('Title and description cannot be empty.');
      return;
    }

    setSaving(true);
    setError(null);

    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('description', description.trim());
    formData.append('visibility', visibility);
    images.forEach((file) => formData.append('image_files', file));

    try {
      const updatedAlbum = await updateAlbum(album.id, formData);
      onSave(updatedAlbum);
      onHide();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === 'string' ? detail : 'Failed to update album.');
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
              accept="image/*"
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                if (e.target.files) {
                  setImages(Array.from(e.target.files));
                }
              }}
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
              <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> Saving...
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
