// frontend/src/components/CentralNewsFeed/CreateAlbum.tsx

import React, { useState } from 'react';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Album as AlbumType } from '../../types/album';

interface CreateAlbumProps {
  onAlbumCreated: (newAlbum: AlbumType) => void;
  sendAlbumMessage: (message: string) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CreateAlbum: React.FC<CreateAlbumProps> = ({ onAlbumCreated, sendAlbumMessage }) => {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>('public');
  const [imageFiles, setImageFiles] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setError('You must be logged in to create an album.');
      return;
    }

    if (title.trim() === '' || description.trim() === '') {
      setError('Title and description cannot be empty.');
      return;
    }

    setSaving(true);
    setError(null);

    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('visibility', visibility);
    if (imageFiles) {
      Array.from(imageFiles).forEach((file) => formData.append('image_files', file));
    }

    try {
      const response = await axios.post(`${API_URL}/albums/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      const createdAlbum: AlbumType = response.data;

      onAlbumCreated(createdAlbum);
      sendAlbumMessage(JSON.stringify({ type: 'new_album', data: createdAlbum }));

      setTitle('');
      setDescription('');
      setVisibility('public');
      setImageFiles(null);
    } catch (err) {
      console.error('Error creating album:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred while creating the album.');
      } else {
        setError('An unexpected error occurred.');
      }
    } finally {
      setSaving(false);
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="mb-4">
      {error && <Alert variant="danger">{error}</Alert>}

      <Form.Group className="mb-3" controlId="formAlbumTitle">
        <Form.Label>Title</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter album title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formAlbumDescription">
        <Form.Label>Description</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="Enter album description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formAlbumVisibility">
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

      <Form.Group className="mb-3" controlId="formAlbumImages">
        <Form.Label>Upload Photos</Form.Label>
        <Form.Control
          type="file"
          multiple
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files) {
              setImageFiles(e.target.files);
            }
          }}
        />
      </Form.Group>

      <Button variant="primary" type="submit" disabled={saving}>
        {saving ? (
          <>
            <Spinner
              as="span"
              animation="border"
              size="sm"
              role="status"
              aria-hidden="true"
            />{' '}
            Creating...
          </>
        ) : (
          'Create Album'
        )}
      </Button>
    </Form>
  );
};

export default CreateAlbum;
