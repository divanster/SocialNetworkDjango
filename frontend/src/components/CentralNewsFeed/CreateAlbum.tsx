import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { useWebSocket } from '../../contexts/WebSocketManager';
import { useAuth } from '../../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const CreateAlbum: React.FC = () => {
  const albumSocket = useWebSocket('albums'); // Get WebSocket directly for "albums"
  const { token } = useAuth(); // Get token from AuthContext
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [visibility, setVisibility] = useState('public'); // Add visibility state
  const [photos, setPhotos] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setSuccess(null);

    // Create a new FormData instance to send as multipart/form-data
    const formData = new FormData();
    formData.append('title', title);
    formData.append('description', description);
    formData.append('visibility', visibility); // Append visibility

    if (photos) {
      // Add photos to form data as 'photos_upload' field
      Array.from(photos).forEach((photo) => {
        formData.append('photos_upload', photo);
      });
    }

    // Log form data to ensure it's being sent as expected
    for (let [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }

    try {
      if (!token) {
        setError('No authentication token available.');
        return;
      }

      const response = await axios.post(`${API_URL}/albums/albums/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`,
        },
      });

      if (albumSocket) {
        albumSocket.send(JSON.stringify({ message: response.data }));
      }

      setTitle('');
      setDescription('');
      setVisibility('public'); // Reset visibility
      setPhotos(null);
      setSuccess('Album created successfully!');
    } catch (error) {
      console.error('Error creating album:', error);
      if (axios.isAxiosError(error)) {
        console.error('Error response data:', error.response?.data); // Log full error response
        setError(
          error.response?.data?.detail ||
            JSON.stringify(error.response?.data) || // Handle nested errors
            'An error occurred while creating the album.'
        );
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
          onChange={(e) => setVisibility(e.target.value)}
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
              setPhotos(e.target.files);
            }
          }}
        />
      </Form.Group>

      <Button type="submit">Create Album</Button>
    </Form>
  );
};

export default CreateAlbum;
