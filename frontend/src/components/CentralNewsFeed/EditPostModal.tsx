// frontend/src/components/CentralNewsFeed/EditPostModal.tsx

import React, { useState } from 'react';
import { Modal, Button, Form } from 'react-bootstrap';
import { Post as PostType } from '../../types/post';

interface EditPostModalProps {
  show: boolean;
  onHide: () => void;
  post: PostType;
  onSave: (updatedPost: PostType) => void;
}

const EditPostModal: React.FC<EditPostModalProps> = ({ show, onHide, post, onSave }) => {
  const [title, setTitle] = useState<string>(post.title);
  const [content, setContent] = useState<string>(post.content);

  const handleSave = () => {
    if (title.trim() === '' || content.trim() === '') {
      alert('Title and content cannot be empty.');
      return;
    }
    const updatedPost: PostType = { ...post, title, content };
    onSave(updatedPost);
    onHide();
  };

  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Edit Post</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <Form>
          <Form.Group controlId="formPostTitle">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter post title"
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
            />
          </Form.Group>
        </Form>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="primary" onClick={handleSave}>
          Save Changes
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default EditPostModal;
