// frontend/src/components/CentralNewsFeed/CreatePost.tsx

import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CreatePost: React.FC = () => {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setError('You must be logged in to create a post.');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    if (images) {
      Array.from(images).forEach((file) => formData.append('image_files', file));
    }

    try {
      const response = await axios.post(`${API_URL}/social/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      setTitle('');
      setContent('');
      setImages(null);
      setError(null);
      setSuccess('Post created successfully!');
    } catch (err) {
      console.error('Error creating post:', err);
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
      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <Form.Group>
        <Form.Label>Title</Form.Label>
        <Form.Control
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="Enter title"
          required
        />
      </Form.Group>

      <Form.Group>
        <Form.Label>Content</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your post content"
          required
        />
      </Form.Group>

      <Form.Group>
        <Form.Label>Upload Images</Form.Label>
        <Form.Control
          type="file"
          multiple
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files) setImages(e.target.files);
          }}
        />
      </Form.Group>

      <Button type="submit">Post</Button>
    </Form>
  );
};

export default CreatePost;
