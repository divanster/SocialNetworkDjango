// frontend/src/components/CentralNewsFeed/EditPostModal.tsx

import React, { useState } from 'react';
import { Modal, Button, Form, Alert, Spinner } from 'react-bootstrap';
import { Post as PostType } from '../../types/post';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

interface EditPostModalProps {
  show: boolean;
  onHide: () => void;
  post: PostType;
  onSave: (updatedPost: PostType) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const EditPostModal: React.FC<EditPostModalProps> = ({ show, onHide, post, onSave }) => {
  const { token } = useAuth();
  const [title, setTitle] = useState<string>(post.title);
  const [content, setContent] = useState<string>(post.content);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState<boolean>(false);

  const handleSave = async () => {
    if (title.trim() === '' || content.trim() === '') {
      setError('Title and content cannot be empty.');
      return;
    }

    if (!token) {
      setError('You must be logged in to update a post.');
      return;
    }

    setSaving(true);
    setError(null);

    try {
      const response = await axios.put(
        `${API_URL}/social/${post.id}/`,
        { title, content },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      const updatedPost: PostType = response.data;
      onSave(updatedPost);
      onHide();
    } catch (err) {
      console.error('Error updating post:', err);
      setError('Failed to update post.');
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
        <Modal.Title>Edit Post</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {error && <Alert variant="danger">{error}</Alert>}
        <Form>
          <Form.Group controlId="formPostTitle">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter post title"
              required
            />
          </Form.Group>
          <Form.Group controlId="formPostContent" className="mt-3">
            <Form.Label>Content</Form.Label>
            <Form.Control
              as="textarea"
              rows={4}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Enter post content"
              required
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

export default EditPostModal;
