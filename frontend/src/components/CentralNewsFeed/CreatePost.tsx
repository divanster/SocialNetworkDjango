// frontend/src/components/CentralNewsFeed/CreatePost.tsx

import React, { useState } from 'react';
import { Form, Button, Alert, Spinner } from 'react-bootstrap';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Post as PostType } from '../../types/post';

interface CreatePostProps {
  onPostCreated: (newPost: PostType) => void;
  sendMessage: (message: string) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CreatePost: React.FC<CreatePostProps> = ({ onPostCreated, sendMessage }) => {
  const { token } = useAuth();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [images, setImages] = useState<FileList | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setError('You must be logged in to create a post.');
      return;
    }

    if (title.trim() === '' || content.trim() === '') {
      setError('Title and content cannot be empty.');
      return;
    }

    setSaving(true);
    setError(null);

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

      const createdPost: PostType = response.data;

      onPostCreated(createdPost);
      sendMessage(JSON.stringify({ type: 'new_post', data: createdPost }));

      setTitle('');
      setContent('');
      setImages(null);
    } catch (err) {
      console.error('Error creating post:', err);
      if (axios.isAxiosError(err)) {
        setError(err.response?.data?.detail || 'An error occurred while creating the post.');
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

      <Form.Group className="mb-3" controlId="formPostTitle">
        <Form.Label>Title</Form.Label>
        <Form.Control
          type="text"
          placeholder="Enter post title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPostContent">
        <Form.Label>Content</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          placeholder="What's on your mind?"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          required
        />
      </Form.Group>

      <Form.Group className="mb-3" controlId="formPostImages">
        <Form.Label>Upload Images</Form.Label>
        <Form.Control
          type="file"
          multiple
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
            if (e.target.files) {
              setImages(e.target.files);
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
            Posting...
          </>
        ) : (
          'Post'
        )}
      </Button>
    </Form>
  );
};

export default CreatePost;
