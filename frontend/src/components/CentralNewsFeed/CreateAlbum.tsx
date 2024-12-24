// frontend/src/components/CentralNewsFeed/CreateAlbum.tsx

import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Album as AlbumType } from '../../types/album'; // Import your Album type

interface CreateAlbumProps {
  onAlbumCreated: (newAlbum: AlbumType) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CreateAlbum: React.FC<CreateAlbumProps> = ({ onAlbumCreated }) => {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState<'public' | 'friends' | 'private'>('public');
  const [imageFiles, setImageFiles] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setError('You must be logged in to create an album.');
      return;
    }

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

      const createdAlbum: AlbumType = response.data; // Adjust according to your backend response

      // Update the parent component's state
      onAlbumCreated(createdAlbum);

      setTitle('');
      setDescription('');
      setVisibility('public');
      setImageFiles(null);
      setError(null);
      setSuccess('Album created successfully!');
    } catch (err) {
      console.error('Error creating album:', err);
      setSuccess(null);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
      {/* Display errors or success messages */}
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <Form.Group>
        <Form.Label>Title</Form.Label>
        <Form.Control
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter album title"
          required
        />
      </Form.Group>

      <Form.Group>
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

      <Form.Group>
        <Form.Label>Visibility</Form.Label>
        <Form.Control
          as="select"
          value={visibility}
          onChange={(e) => setVisibility(e.target.value as 'public' | 'friends' | 'private')}
          required
        >
          <option value="public">Public</option>
          <option value="friends">Friends</option>
          <option value="private">Private</option>
        </Form.Control>
      </Form.Group>

      <Form.Group>
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

      <Button type="submit">Create Album</Button>
    </Form>
  );
};

export default CreateAlbum;
