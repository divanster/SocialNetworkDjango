// frontend/src/components/CentralNewsFeed/CreatePost.tsx

import React, { useState, useEffect } from 'react';
import { Form, Button } from 'react-bootstrap';
import axios from 'axios';
import { useWebSocket } from '../../contexts/WebSocketManager';
import { useAuth } from '../../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const CreatePost: React.FC = () => {
  const { getSocket } = useWebSocket();
  const { token } = useAuth();
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (token) {
      const postSocket = getSocket(`ws://localhost:8000/ws/posts/?token=${token}`);
      setSocket(postSocket);
    }
  }, [getSocket, token]);

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
      for (let i = 0; i < images.length; i++) {
        formData.append('image_files', images[i]);
      }
    }

    try {
      const response = await axios.post(`${API_URL}/social/posts/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      if (socket) {
        socket.send(JSON.stringify({ message: response.data }));
      }
      setTitle('');
      setContent('');
      setImages(null);
      setError(null);
    } catch (error) {
      console.error('Error creating post:', error);
      if (axios.isAxiosError(error)) {
        setError(error.response?.data?.detail || 'An error occurred');
      } else {
        setError('An unexpected error occurred.');
      }
    }
  };

  return (
    <Form onSubmit={handleSubmit}>
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
