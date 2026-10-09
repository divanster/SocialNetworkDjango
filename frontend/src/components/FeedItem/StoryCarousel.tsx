import React, { useMemo, useState } from 'react';
import { Button, Modal } from 'react-bootstrap';
import Avatar from '../Common/Avatar';
import UserIdentityLink from '../Common/UserIdentityLink';
import { deleteStory } from '../../services/contentService';
import { useAuth } from '../../contexts/AuthContext';
import './StoryCarousel.css';

interface StoryProps {
  id: string;
  user?: { id: string; full_name?: string; profile_picture?: string } | string;
  user_name?: string;
  content: string;
  media_url?: string | null;
  media_type?: 'text' | 'image' | 'video';
  created_at: string;
  updated_at: string;
}

interface Props {
  stories: StoryProps[];
  onStoryDeleted?: (storyId: string) => void;
}

interface NormalizedStory {
  id: string;
  userId?: string;
  userName: string;
  userAvatar?: string;
  content: string;
  mediaUrl?: string | null;
  mediaType: 'text' | 'image' | 'video';
  createdAt?: string;
}

const StoryCarousel: React.FC<Props> = ({ stories, onStoryDeleted }) => {
  const { user } = useAuth();
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  const normalizedStories = useMemo<NormalizedStory[]>(
    () =>
      stories.map((story) => {
        const userObject = typeof story.user === 'object' && story.user !== null ? story.user : undefined;
        const userId = userObject?.id || (typeof story.user === 'string' ? story.user : undefined);
        return {
          id: String(story.id),
          userId: userId ? String(userId) : undefined,
          userName: userObject?.full_name || story.user_name || 'Unknown user',
          userAvatar: userObject?.profile_picture,
          content: story.content,
          mediaUrl: story.media_url ?? null,
          mediaType: story.media_type || 'text',
          createdAt: story.created_at,
        };
      }),
    [stories]
  );

  if (!normalizedStories.length) {
    return <div className="story-empty-state">No stories available right now.</div>;
  }

  const activeStory = activeIndex === null ? null : normalizedStories[activeIndex];
  const canDeleteActiveStory = Boolean(activeStory?.userId && user?.id && activeStory.userId === user.id);

  const goPrevious = () => {
    setDeleteError(null);
    setActiveIndex((prev) => {
      if (prev === null || prev <= 0) return 0;
      return prev - 1;
    });
  };

  const goNext = () => {
    setDeleteError(null);
    setActiveIndex((prev) => {
      if (prev === null) return 0;
      if (prev >= normalizedStories.length - 1) return normalizedStories.length - 1;
      return prev + 1;
    });
  };

  const handleDeleteStory = async () => {
    if (!activeStory) return;
    if (!window.confirm('Delete this story?')) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteStory(activeStory.id);
      onStoryDeleted?.(activeStory.id);
      setActiveIndex((prev) => {
        if (prev === null) return null;
        if (normalizedStories.length <= 1) return null;
        return Math.min(prev, normalizedStories.length - 2);
      });
    } catch {
      setDeleteError('Failed to delete story.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <>
      <div className="stories-bar">
        {normalizedStories.slice(0, 10).map((story, index) => (
          <button
            key={story.id}
            className="story-wrapper"
            type="button"
            onClick={() => {
              setDeleteError(null);
              setActiveIndex(index);
            }}
            aria-label={`Open story by ${story.userName}`}
          >
            <UserIdentityLink userId={story.userId} className="story-user" ariaLabel={`Open ${story.userName} profile`}>
              <Avatar
                size={28}
                src={story.userAvatar}
                name={story.userName}
                alt={`${story.userName} avatar`}
              />
              <span>{story.userName}</span>
            </UserIdentityLink>
            <div className="story-teaser">
              {story.mediaUrl ? (
                <img
                  src={story.mediaUrl}
                  alt={`${story.userName} story`}
                  onError={(e) => {
                    e.currentTarget.src = 'https://via.placeholder.com/200x300?text=Story+Unavailable';
                  }}
                />
              ) : (
                <p>{story.content || 'Story'}</p>
              )}
            </div>
          </button>
        ))}
        {normalizedStories.length > 10 && <div className="story-scroll-hint">›</div>}
      </div>

      <Modal show={activeIndex !== null} onHide={() => setActiveIndex(null)} centered>
        <Modal.Header closeButton>
          <Modal.Title>Story</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {activeStory && (
            <div className="story-viewer">
              <UserIdentityLink userId={activeStory.userId} className="story-user" ariaLabel={`Open ${activeStory.userName} profile`}>
                <Avatar size={32} src={activeStory.userAvatar} name={activeStory.userName} alt={`${activeStory.userName} avatar`} />
                <span>{activeStory.userName}</span>
              </UserIdentityLink>
              {activeStory.createdAt && (
                <small className="text-muted d-block mb-2">
                  {new Date(activeStory.createdAt).toLocaleString()}
                </small>
              )}
              {activeStory.mediaType === 'image' && activeStory.mediaUrl ? (
                <img
                  className="story-viewer-media"
                  src={activeStory.mediaUrl}
                  alt={`${activeStory.userName} story media`}
                  onError={(e) => {
                    e.currentTarget.src = 'https://via.placeholder.com/900x600?text=Story+Unavailable';
                  }}
                />
              ) : (
                <p className="story-viewer-content">{activeStory.content}</p>
              )}
              {deleteError && <p className="text-danger mb-2">{deleteError}</p>}
              <div className="story-viewer-controls">
                <Button variant="outline-secondary" onClick={goPrevious} disabled={activeIndex === 0}>
                  Previous
                </Button>
                <Button variant="outline-secondary" onClick={goNext} disabled={activeIndex === normalizedStories.length - 1}>
                  Next
                </Button>
                {canDeleteActiveStory && (
                  <Button variant="outline-danger" onClick={handleDeleteStory} disabled={deleting}>
                    {deleting ? 'Deleting...' : 'Delete'}
                  </Button>
                )}
              </div>
            </div>
          )}
        </Modal.Body>
      </Modal>
    </>
  );
};

export default StoryCarousel;
