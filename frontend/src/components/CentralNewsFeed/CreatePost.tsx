import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { useWebSocket } from '../../contexts/WebSocketContext';
import { useNavigate } from 'react-router-dom';
import './CreatePost.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const CreatePost: React.FC = () => {
  const { socket } = useWebSocket();
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const token = localStorage.getItem('token');

    if (!token) {
      setError('You must be logged in to create a post.');
      navigate('/login');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    if (images) {
      for (let i = 0; i < images.length; i++) {
        formData.append('image_files', images[i]);
      }
    }

    try {
      const response = await axios.post(`${API_URL}/social/posts/`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Response data:', response.data);
      if (socket) {
        socket.send(JSON.stringify({ message: response.data }));
      }
      // Clear the form after successful post creation
      setTitle('');
      setContent('');
      setImages(null);
      setError(null);
    } catch (error) {
      console.error('Error creating post:', error);
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 401) {
          // If unauthorized, clear tokens and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          setError('Session expired. Please log in again.');
          navigate('/login');
        } else {
          setError(error.response?.data?.detail || 'An error occurred');
        }
      } else {
        setError('An unexpected error occurred');
      }
    }
  };

  return (
    <Form onSubmit={handleSubmit} className="create-post-container">
      {error && <div className="alert alert-danger">{error}</div>}
      <Form.Group>
        <Form.Label>Title</Form.Label>
        <Form.Control
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
      </Form.Group>
      <Form.Group>
        <Form.Label>Content</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          value={content}
          onChange={(e) => setContent(e.target.value)}
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
