import React, { useEffect, useMemo, useState } from 'react';
import { Form, Button, Alert, Spinner, Modal } from 'react-bootstrap';
import { BsImage, BsCameraVideo, BsEmojiSmile, BsCollectionPlay, BsPeople } from 'react-icons/bs';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import { Post as PostType } from '../../types/post';
import { Album as AlbumType } from '../../types/album';
import Avatar from '../Common/Avatar';
import UserTagPicker from '../Common/UserTagPicker';
import { CompactUser } from '../../services/socialGraphService';
import { createStory } from '../../services/contentService';
import { useNavigate } from 'react-router-dom';
import './CreatePosting.css';

interface CreatePostingProps {
  onPostCreated: (newPost: PostType) => void;
  onAlbumCreated: (newAlbum: AlbumType) => void;
  onStoryCreated?: (story: any) => void;
  sendMessage: (message: string) => void;
  sendAlbumMessage: (message: string) => void;
}

const CreatePosting: React.FC<CreatePostingProps> = ({
  onPostCreated,
  onStoryCreated,
  sendMessage,
}) => {
  const navigate = useNavigate();
  const { token, user } = useAuth();

  const [postContent, setPostContent] = useState('');
  const [postImages, setPostImages] = useState<File[]>([]);
  const [savingPost, setSavingPost] = useState<boolean>(false);
  const [postError, setPostError] = useState<string | null>(null);
  const [taggedUsers, setTaggedUsers] = useState<CompactUser[]>([]);

  const [showStoryModal, setShowStoryModal] = useState<boolean>(false);
  const [storyContent, setStoryContent] = useState<string>('');
  const [storyVisibility, setStoryVisibility] = useState<'public' | 'friends' | 'private'>('public');
  const [storyMediaFile, setStoryMediaFile] = useState<File | null>(null);
  const [storyMediaPreview, setStoryMediaPreview] = useState<string | null>(null);
  const [storyTags, setStoryTags] = useState<CompactUser[]>([]);
  const [savingStory, setSavingStory] = useState<boolean>(false);
  const [storyError, setStoryError] = useState<string | null>(null);

  const postImagePreviews = useMemo(
    () => postImages.map((file) => ({ file, preview: URL.createObjectURL(file) })),
    [postImages]
  );

  useEffect(() => () => {
    postImagePreviews.forEach(({ preview }) => URL.revokeObjectURL(preview));
  }, [postImagePreviews]);

  const storyMediaType = useMemo<'text' | 'image' | undefined>(() => {
    if (!storyMediaFile) return undefined;
    return storyMediaFile.type.startsWith('image/') ? 'image' : undefined;
  }, [storyMediaFile]);

  const handlePostImagesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPostImages(Array.from(e.target.files));
    }
  };

  const removePostImage = (indexToRemove: number) => {
    setPostImages((prev) => prev.filter((_, index) => index !== indexToRemove));
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
    postImages.forEach((file) => formData.append('image_files', file));
    taggedUsers.forEach((userToTag) => formData.append('tagged_user_ids', userToTag.id));

    try {
      const response = await axios.post('/social/', formData);
      const createdPost: PostType = response.data;
      onPostCreated(createdPost);
      sendMessage(JSON.stringify({ type: 'new_post', data: createdPost }));
      setPostContent('');
      setPostImages([]);
      setTaggedUsers([]);
      const fileInput = document.getElementById('post-image-input') as HTMLInputElement | null;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      setPostError(typeof detail === 'string' ? detail : 'An error occurred while creating the post.');
    } finally {
      setSavingPost(false);
    }
  };

  const openStoryModal = () => {
    setStoryError(null);
    setShowStoryModal(true);
  };

  const closeStoryModal = () => {
    if (storyMediaPreview) {
      URL.revokeObjectURL(storyMediaPreview);
    }
    setShowStoryModal(false);
    setStoryContent('');
    setStoryVisibility('public');
    setStoryMediaFile(null);
    setStoryMediaPreview(null);
    setStoryTags([]);
    setStoryError(null);
  };

  const handleStoryMediaChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    if (storyMediaPreview) {
      URL.revokeObjectURL(storyMediaPreview);
    }
    setStoryMediaFile(file);
    if (!file) {
      setStoryMediaPreview(null);
      return;
    }
    if (!file.type.startsWith('image/')) {
      setStoryError('Only image media is currently supported for stories.');
      setStoryMediaFile(null);
      setStoryMediaPreview(null);
      return;
    }
    setStoryError(null);
    setStoryMediaPreview(URL.createObjectURL(file));
  };

  const handleCreateStory = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!token) {
      setStoryError('You must be logged in to create a story.');
      return;
    }
    if (!storyContent.trim() && !storyMediaFile) {
      setStoryError('Add story text or select an image.');
      return;
    }
    setSavingStory(true);
    setStoryError(null);
    const formData = new FormData();
    formData.append('content', storyContent.trim());
    formData.append('visibility', storyVisibility);
    if (storyMediaFile) {
      formData.append('media_file', storyMediaFile);
      if (storyMediaType) {
        formData.append('media_type', storyMediaType);
      }
    }
    storyTags.forEach((tag) => formData.append('tagged_user_ids', tag.id));
    try {
      const createdStory = await createStory(formData);
      onStoryCreated?.(createdStory);
      closeStoryModal();
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setStoryError(typeof detail === 'string' ? detail : 'Failed to create story.');
    } finally {
      setSavingStory(false);
    }
  };

  const displayName = user?.username || 'friend';

  return (
    <>
      <div className="composer-card">
        {postError && <Alert variant="danger">{postError}</Alert>}

        <Form onSubmit={handlePostSubmit}>
          <div className="composer-top">
            <Avatar size={42} src={user?.profile?.profile_picture} name={displayName} alt={`${displayName} avatar`} />
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

            <button type="button" className="composer-action-btn" onClick={() => navigate('/albums')}>
              <BsPeople aria-hidden="true" />
              <span>Album</span>
            </button>

            <button type="button" className="composer-action-btn" onClick={openStoryModal}>
              <BsCollectionPlay aria-hidden="true" />
              <span>Story</span>
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

          <div className="mt-3">
            <UserTagPicker label="Tag people in this post" selectedUsers={taggedUsers} onChange={setTaggedUsers} />
          </div>

          {postImagePreviews.length > 0 && (
            <div className="composer-attachments">
              {postImagePreviews.map(({ file, preview }, index) => (
                <div key={`${file.name}-${file.size}-${index}`} className="post-attached-item">
                  <img src={preview} alt={`attachment-${index}`} className="post-attached-image" />
                  <button
                    type="button"
                    className="post-attached-remove"
                    onClick={() => removePostImage(index)}
                    aria-label={`Remove ${file.name}`}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          )}
        </Form>
      </div>

      <Modal show={showStoryModal} onHide={closeStoryModal} centered>
        <Modal.Header closeButton>
          <Modal.Title>Create Story</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {storyError && <Alert variant="danger">{storyError}</Alert>}
          <Form onSubmit={handleCreateStory}>
            <Form.Group className="mb-3">
              <Form.Label>Story text</Form.Label>
              <Form.Control
                as="textarea"
                rows={3}
                value={storyContent}
                onChange={(e) => setStoryContent(e.target.value)}
                placeholder="Share a quick update"
              />
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Visibility</Form.Label>
              <Form.Select
                value={storyVisibility}
                onChange={(e) => setStoryVisibility(e.target.value as 'public' | 'friends' | 'private')}
              >
                <option value="public">Public</option>
                <option value="friends">Friends</option>
                <option value="private">Private</option>
              </Form.Select>
            </Form.Group>
            <Form.Group className="mb-3">
              <Form.Label>Story image (optional)</Form.Label>
              <Form.Control type="file" accept="image/*" onChange={handleStoryMediaChange} />
            </Form.Group>
            {storyMediaPreview && (
              <img src={storyMediaPreview} alt="Story preview" className="story-preview-image mb-3" />
            )}
            <Form.Group className="mb-3">
              <UserTagPicker label="Tag people in this story" selectedUsers={storyTags} onChange={setStoryTags} />
            </Form.Group>
            <div className="d-flex gap-2">
              <Button variant="secondary" onClick={closeStoryModal} disabled={savingStory}>
                Cancel
              </Button>
              <Button type="submit" disabled={savingStory}>
                {savingStory ? 'Creating...' : 'Create Story'}
              </Button>
            </div>
          </Form>
        </Modal.Body>
      </Modal>
    </>
  );
};

export default CreatePosting;
