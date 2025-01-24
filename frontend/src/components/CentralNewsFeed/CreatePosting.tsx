// frontend/src/components/CentralNewsFeed/CreatePosting.tsx

import React, { useState } from 'react';
import { Form, Button, Alert, Spinner, Modal } from 'react-bootstrap';
import { BsImage, BsPeople, BsCameraVideo, BsEmojiSmile } from 'react-icons/bs';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Post as PostType } from '../../types/post';
import { Album as AlbumType } from '../../types/album';
import './CreatePosting.css'; // Ensure this file exists and is correctly linked

interface CreatePostingProps {
  onPostCreated: (newPost: PostType) => void;
  onAlbumCreated: (newAlbum: AlbumType) => void;
  sendMessage: (message: string) => void;
  sendAlbumMessage: (message: string) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CreatePosting: React.FC<CreatePostingProps> = ({
  onPostCreated,
  onAlbumCreated,
  sendMessage,
  sendAlbumMessage,
}) => {
  const { token } = useAuth();

  // State for post
  const [postTitle, setPostTitle] = useState(''); // Added title state
  const [postContent, setPostContent] = useState('');
  const [postImages, setPostImages] = useState<FileList | null>(null);
  const [savingPost, setSavingPost] = useState<boolean>(false);
  const [postError, setPostError] = useState<string | null>(null);

  // State for album modal
  const [showAlbumModal, setShowAlbumModal] = useState<boolean>(false);
  const [albumTitle, setAlbumTitle] = useState('');
  const [albumDescription, setAlbumDescription] = useState('');
  const [albumImages, setAlbumImages] = useState<FileList | null>(null);
  const [savingAlbum, setSavingAlbum] = useState<boolean>(false);
  const [albumError, setAlbumError] = useState<string | null>(null);

  // Handlers for post
  const handlePostTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPostTitle(e.target.value);
  };

  const handlePostContentChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPostContent(e.target.value);
  };

  const handlePostImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPostImages(e.target.files);
    }
  };

  const handlePostSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!token) {
      setPostError('You must be logged in to create a post.');
      return;
    }

    if (postTitle.trim() === '' || postContent.trim() === '') {
      setPostError('Title and content cannot be empty.');
      return;
    }

    setSavingPost(true);
    setPostError(null);

    const formData = new FormData();
    formData.append('title', postTitle); // Include title in FormData
    formData.append('content', postContent); // Required
    formData.append('visibility', 'public'); // Example, adjust as needed

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

      // Reset post form
      setPostTitle('');
      setPostContent('');
      setPostImages(null);
      // Reset file input value
      (document.getElementById('post-image-input') as HTMLInputElement).value = '';
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

  // Handlers for album
  const handleOpenAlbumModal = () => {
    setShowAlbumModal(true);
  };

  const handleCloseAlbumModal = () => {
    setShowAlbumModal(false);
    setAlbumTitle('');
    setAlbumDescription('');
    setAlbumImages(null);
    setAlbumError(null);
  };

  const handleAlbumTitleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAlbumTitle(e.target.value);
  };

  const handleAlbumDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setAlbumDescription(e.target.value);
  };

  const handleAlbumImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setAlbumImages(e.target.files);
    }
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
    formData.append('visibility', 'public'); // Or allow user to select

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

      // Reset album form
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

  return (
    <>
      <div className="create-posting-container p-3 mb-4 bg-white rounded shadow-sm">
        {/* Post Error Alert */}
        {postError && <Alert variant="danger">{postError}</Alert>}

        <Form onSubmit={handlePostSubmit}>
          {/* Title Input */}
          <Form.Group className="mb-3" controlId="formPostTitle">
            <Form.Control
              type="text"
              placeholder="Enter title"
              value={postTitle}
              onChange={handlePostTitleChange}
              required
            />
          </Form.Group>

          {/* Content Input */}
          <Form.Group className="mb-3" controlId="formPostContent">
            <Form.Control
              as="textarea"
              rows={2}
              placeholder="What's on your mind?"
              value={postContent}
              onChange={handlePostContentChange}
              className="create-posting-textarea"
              required
            />
          </Form.Group>

          <div className="d-flex align-items-center justify-content-between">
            <div className="d-flex">
              {/* Photo Icon */}
              <label htmlFor="post-image-input" className="create-posting-icon-label me-3">
                <BsImage size={24} color="#4CAF50" />
                <span className="ms-1">Photo</span>
                <input
                  type="file"
                  id="post-image-input"
                  multiple
                  accept="image/*"
                  onChange={handlePostImagesChange}
                  className="d-none"
                />
              </label>

              {/* Album Icon */}
              <Button variant="outline-secondary" className="me-3 d-flex align-items-center" onClick={handleOpenAlbumModal}>
                <BsPeople size={24} color="#0084FF" />
                <span className="ms-1">Album</span>
              </Button>

              {/* Video Icon */}
              <div className="create-posting-icon-label me-3">
                <BsCameraVideo size={24} color="#FF0000" />
                <span className="ms-1">Video</span>
              </div>

              {/* Emoji Icon */}
              <div className="create-posting-icon-label">
                <BsEmojiSmile size={24} color="#FFD700" />
                <span className="ms-1">Feeling/Activity</span>
              </div>
            </div>

            {/* Post Button */}
            <Button variant="primary" type="submit" disabled={savingPost}>
              {savingPost ? (
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
          </div>

          {/* Display Selected Images */}
          {postImages && postImages.length > 0 && (
            <div className="mt-3">
              <strong>Attached Images:</strong>
              <div className="d-flex flex-wrap mt-2">
                {Array.from(postImages).map((file, index) => (
                  <img
                    key={index}
                    src={URL.createObjectURL(file)}
                    alt={`attachment-${index}`}
                    className="me-2 mb-2 post-attached-image"
                  />
                ))}
              </div>
            </div>
          )}
        </Form>
      </div>

      {/* Album Creation Modal */}
      <Modal show={showAlbumModal} onHide={handleCloseAlbumModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create Album</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {albumError && <Alert variant="danger">{albumError}</Alert>}

          <Form onSubmit={handleAlbumSubmit}>
            {/* Album Title */}
            <Form.Group className="mb-3" controlId="formAlbumTitle">
              <Form.Label>Title</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter album title"
                value={albumTitle}
                onChange={handleAlbumTitleChange}
                required
              />
            </Form.Group>

            {/* Album Description */}
            <Form.Group className="mb-3" controlId="formAlbumDescription">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                placeholder="Enter album description"
                value={albumDescription}
                onChange={handleAlbumDescriptionChange}
                required
              />
            </Form.Group>

            {/* Album Images */}
            <Form.Group className="mb-3" controlId="formAlbumImages">
              <Form.Label>Upload Photos</Form.Label>
              <Form.Control
                type="file"
                multiple
                accept="image/*"
                onChange={handleAlbumImagesChange}
              />
            </Form.Group>

            {/* Album Visibility (Optional) */}
            <Form.Group className="mb-3" controlId="formAlbumVisibility">
              <Form.Label>Visibility</Form.Label>
              <Form.Select
                value="public"
                onChange={(e) => {/* Handle visibility if implemented */}}
              >
                <option value="public">Public</option>
                <option value="friends">Friends</option>
                <option value="private">Private</option>
              </Form.Select>
            </Form.Group>

            {/* Submit Button */}
            <Button variant="primary" type="submit" disabled={savingAlbum}>
              {savingAlbum ? (
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
        </Modal.Body>
      </Modal>
    </>
  ); // Closing the return statement

}; // **Missing Closing Brace Added Here**

export default CreatePosting;
