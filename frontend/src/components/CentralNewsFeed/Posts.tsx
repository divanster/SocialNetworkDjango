// frontend/src/components/CentralNewsFeed/Posts.tsx

import React, { useState } from 'react';
import { Card, Button, Spinner } from 'react-bootstrap';
import EditPostModal from './EditPostModal';
import { Post as PostType } from '../../types/post';

interface PostsProps {
  posts: PostType[];
  /** Use string if your backend returns UUIDs */
  onDeletePost: (id: string) => void;
  /** Rename to onUpdatePost for clarity */
  onUpdatePost: (updatedPost: PostType) => void;
  /** Arrays of string IDs */
  deletingPostIds: string[];
  updatingPostIds: string[];
}

const Posts: React.FC<PostsProps> = ({
  posts,
  onDeletePost,
  onUpdatePost,
  deletingPostIds,
  updatingPostIds,
}) => {
  const [showModal, setShowModal] = useState<boolean>(false);
  const [currentPost, setCurrentPost] = useState<PostType | null>(null);

  const handleEditClick = (post: PostType) => {
    setCurrentPost(post);
    setShowModal(true);
    console.log(`Editing post with ID ${post.id}`);
  };

  const handleSave = (updatedPost: PostType) => {
    onUpdatePost(updatedPost);
    console.log(`Post with ID ${updatedPost.id} updated.`);
    setShowModal(false);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setCurrentPost(null);
  };

  return (
    <div>
      {posts.map((post) => {
        // Use `author` instead of `user`
        const authorUsername = post.author?.username || 'Unknown User';
        const createdAt = post.created_at
          ? new Date(post.created_at).toLocaleString()
          : '';

        return (
          <Card key={post.id} className="mb-3">
            <Card.Body>
              <Card.Title>{post.title}</Card.Title>
              <Card.Subtitle className="mb-2 text-muted">
                By {authorUsername} on {createdAt}
              </Card.Subtitle>
              <Card.Text>{post.content}</Card.Text>

              {post.images && post.images.length > 0 && (
                <div className="mb-2">
                  {post.images.map((img) => (
                    <img
                      key={img.id}
                      src={img.image}
                      alt="Post"
                      style={{ width: '100px', marginRight: '10px' }}
                    />
                  ))}
                </div>
              )}

              {/* Update Button */}
              <Button
                variant="primary"
                className="me-2"
                onClick={() => handleEditClick(post)}
                disabled={updatingPostIds.includes(post.id)}
              >
                {updatingPostIds.includes(post.id) ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      aria-hidden="true"
                    />{' '}
                    Updating...
                  </>
                ) : (
                  'Update'
                )}
              </Button>

              {/* Delete Button */}
              <Button
                variant="danger"
                onClick={() => {
                  if (window.confirm('Are you sure you want to delete this post?')) {
                    onDeletePost(post.id);
                  }
                }}
                disabled={deletingPostIds.includes(post.id)}
              >
                {deletingPostIds.includes(post.id) ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      aria-hidden="true"
                    />{' '}
                    Deleting...
                  </>
                ) : (
                  'Delete'
                )}
              </Button>
            </Card.Body>
          </Card>
        );
      })}

      {/* Edit Post Modal */}
      {currentPost && (
        <EditPostModal
          show={showModal}
          onHide={handleCloseModal}
          post={currentPost}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default Posts;
