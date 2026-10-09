import React, { useState } from 'react';
import { Form, Button, Alert, Spinner, Modal } from 'react-bootstrap';
import { BsImage, BsPeople, BsCameraVideo, BsEmojiSmile } from 'react-icons/bs';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Post as PostType } from '../../types/post';
import { Album as AlbumType } from '../../types/album';
import Avatar from '../Common/Avatar';
import './CreatePosting.css';

interface CreatePostingProps {
  onPostCreated: (newPost: PostType) => void;
  onAlbumCreated: (newAlbum: AlbumType) => void;
  sendMessage: (message: string) => void;
  sendAlbumMessage: (message: string) => void;
}

const API_URL = (process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1').replace(/\/+$/, '');

const CreatePosting: React.FC<CreatePostingProps> = ({
  onPostCreated,
  onAlbumCreated,
  sendMessage,
  sendAlbumMessage,
}) => {
  const { token, user } = useAuth();

  const [postContent, setPostContent] = useState('');
  const [postImages, setPostImages] = useState<FileList | null>(null);
  const [savingPost, setSavingPost] = useState<boolean>(false);
  const [postError, setPostError] = useState<string | null>(null);

  const [showAlbumModal, setShowAlbumModal] = useState<boolean>(false);
  const [albumTitle, setAlbumTitle] = useState('');
  const [albumDescription, setAlbumDescription] = useState('');
  const [albumImages, setAlbumImages] = useState<FileList | null>(null);
  const [savingAlbum, setSavingAlbum] = useState<boolean>(false);
  const [albumError, setAlbumError] = useState<string | null>(null);

  const handlePostImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPostImages(e.target.files);
    }
  };

  const deriveTitle = (content: string): string => {
    const clean = content.trim().replace(/\s+/g, ' ');
    if (!clean) return 'New post';
    return clean.slice(0, 60);
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setPostError('You must be logged in to create a post.');
      return;
    }

    if (postContent.trim() === '') {
      setPostError('Post content cannot be empty.');
      return;
    }

    setSavingPost(true);
    setPostError(null);

    const formData = new FormData();
    formData.append('title', deriveTitle(postContent));
    formData.append('content', postContent);
    formData.append('visibility', 'public');

    if (postImages) {
      Array.from(postImages).forEach((file) => {
        formData.append('image_files', file);
      });
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

      setPostContent('');
      setPostImages(null);
      const fileInput = document.getElementById('post-image-input') as HTMLInputElement | null;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      console.error('Error creating post:', error);
      if (axios.isAxiosError(error)) {
        if (error.response) {
          setPostError(
            error.response.data.detail ||
            JSON.stringify(error.response.data) ||
            'An error occurred while creating the post.'
          );
        } else if (error.request) {
          setPostError('No response received from the server.');
        } else {
          setPostError(error.message);
        }
      } else {
        setPostError('An unexpected error occurred.');
      }
    } finally {
      setSavingPost(false);
    }
  };

  const handleOpenAlbumModal = () => setShowAlbumModal(true);
  const handleCloseAlbumModal = () => {
    setShowAlbumModal(false);
    setAlbumTitle('');
    setAlbumDescription('');
    setAlbumImages(null);
    setAlbumError(null);
  };

  const handleAlbumSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setAlbumError('You must be logged in to create an album.');
      return;
    }

    if (albumTitle.trim() === '' || albumDescription.trim() === '') {
      setAlbumError('Title and description cannot be empty.');
      return;
    }

    if (!albumImages || albumImages.length === 0) {
      setAlbumError('You must add at least one photo to create an album.');
      return;
    }

    setSavingAlbum(true);
    setAlbumError(null);

    const formData = new FormData();
    formData.append('title', albumTitle);
    formData.append('description', albumDescription);
    formData.append('visibility', 'public');
    Array.from(albumImages).forEach((file) => {
      formData.append('image_files', file);
    });

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
      handleCloseAlbumModal();
    } catch (error: any) {
      console.error('Error creating album:', error);
      if (axios.isAxiosError(error)) {
        if (error.response) {
          setAlbumError(
            error.response.data.detail ||
            JSON.stringify(error.response.data) ||
            'An error occurred while creating the album.'
          );
        } else if (error.request) {
          setAlbumError('No response received from the server.');
        } else {
          setAlbumError(error.message);
        }
      } else {
        setAlbumError('An unexpected error occurred.');
      }
    } finally {
      setSavingAlbum(false);
    }
  };

  const displayName = user?.username || 'friend';

  return (
    <>
      <div className="composer-card">
        {postError && <Alert variant="danger">{postError}</Alert>}

        <Form onSubmit={handlePostSubmit}>
          <div className="composer-top">
            <Avatar
              size={42}
              src={user?.profile?.profile_picture}
              name={displayName}
              alt={`${displayName} avatar`}
            />
            <Form.Control
              as="textarea"
              rows={2}
              placeholder={`What's on your mind, ${displayName}?`}
              value={postContent}
              onChange={(e) => setPostContent(e.target.value)}
              className="composer-input"
              required
            />
            <Button variant="primary" type="submit" disabled={savingPost}>
              {savingPost ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> Posting...
                </>
              ) : (
                'Post'
              )}
            </Button>
          </div>

          <div className="composer-actions" role="group" aria-label="Post actions">
            <label htmlFor="post-image-input" className="composer-action-btn">
              <BsImage aria-hidden="true" />
              <span>Photo</span>
              <input
                type="file"
                id="post-image-input"
                multiple
                accept="image/*"
                onChange={handlePostImagesChange}
                className="d-none"
              />
            </label>

            <button type="button" className="composer-action-btn" onClick={handleOpenAlbumModal}>
              <BsPeople aria-hidden="true" />
              <span>Album</span>
            </button>

            <button type="button" className="composer-action-btn" aria-label="Video (coming soon)" disabled>
              <BsCameraVideo aria-hidden="true" />
              <span>Video</span>
            </button>

            <button type="button" className="composer-action-btn" aria-label="Feeling or activity (coming soon)" disabled>
              <BsEmojiSmile aria-hidden="true" />
              <span>Feeling</span>
            </button>
          </div>

          {postImages && postImages.length > 0 && (
            <div className="composer-attachments">
              {Array.from(postImages).map((file, index) => (
                <img
                  key={index}
                  src={URL.createObjectURL(file)}
                  alt={`attachment-${index}`}
                  className="post-attached-image"
                />
              ))}
            </div>
          )}
        </Form>
      </div>

      <Modal show={showAlbumModal} onHide={handleCloseAlbumModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create Album</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {albumError && <Alert variant="danger">{albumError}</Alert>}

          <Form onSubmit={handleAlbumSubmit}>
            <Form.Group className="mb-3" controlId="formAlbumTitle">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter album title"
                value={albumTitle}
                onChange={(e) => setAlbumTitle(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formAlbumDescription">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Enter album description"
                value={albumDescription}
                onChange={(e) => setAlbumDescription(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group className="mb-3" controlId="formAlbumImages">
              <Form.Label>Upload Photos</Form.Label>
              <Form.Control
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => {
                  const files = (e.currentTarget as HTMLInputElement).files;
                  if (files) setAlbumImages(files);
                }}
              />
            </Form.Group>

            <Button variant="primary" type="submit" disabled={savingAlbum}>
              {savingAlbum ? (
                <>
                  <Spinner as="span" animation="border" size="sm" role="status" aria-hidden="true" /> Creating...
                </>
              ) : (
                'Create Album'
              )}
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default CreatePosting;
