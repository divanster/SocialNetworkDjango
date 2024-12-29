// frontend/src/components/CentralNewsFeed/Posts.tsx

import React, { useState } from 'react';
import { Post as PostType } from '../../types/post';
import { Card, Button, Spinner } from 'react-bootstrap';
import EditPostModal from './EditPostModal'; // Ensure this component exists

interface PostsProps {
  posts: PostType[];
  onDelete: (id: number) => void;
  onUpdate: (updatedPost: PostType) => void;
  deletingPostIds: number[]; // IDs of posts being deleted
  updatingPostIds: number[]; // IDs of posts being updated
}

const Posts: React.FC<PostsProps> = ({
  posts,
  onDelete,
  onUpdate,
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
    onUpdate(updatedPost);
    console.log(`Post with ID ${updatedPost.id} updated.`);
  };

  return (
    <div>
      {posts.map((post) => (
        <Card key={post.id} className="mb-3">
          <Card.Body>
            <Card.Title>{post.title}</Card.Title>
            <Card.Subtitle className="mb-2 text-muted">
              By {post.user.username} on {new Date(post.created_at).toLocaleString()}
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
                  onDelete(post.id);
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
      ))}

      {/* Edit Post Modal */}
      {currentPost && (
        <EditPostModal
          show={showModal}
          onHide={() => setShowModal(false)}
          post={currentPost}
          onSave={handleSave}
        />
      )}
    </div>
  );
};

export default Posts;
