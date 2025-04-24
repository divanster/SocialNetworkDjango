// frontend/src/components/CentralNewsFeed/Posts.tsx
import React, { useState } from 'react';
import { Card, Button, Spinner, Form } from 'react-bootstrap';
import EditPostModal from './EditPostModal';
import ReactionButton from '../FeedItem/ReactionButton';
import { useAuth } from '../../contexts/AuthContext';
import { Post as PostType } from '../../types/post';

interface PostsProps {
  posts: PostType[];
  onDeletePost: (id: string) => void;
  onUpdatePost: (updated: PostType) => void;
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
  const { user } = useAuth();
  const [showModal, setShowModal] = useState(false);
  const [currentPost, setCurrentPost] = useState<PostType | null>(null);
  const [openCommentsFor, setOpenCommentsFor] = useState<string | null>(null);
  const [newComment, setNewComment] = useState('');

  const openEdit = (post: PostType) => {
    setCurrentPost(post);
    setShowModal(true);
  };
  const closeEdit = () => {
    setCurrentPost(null);
    setShowModal(false);
  };
  const saveEdit = (updated: PostType) => {
    onUpdatePost(updated);
    closeEdit();
  };

  const toggleComments = (postId: string) => {
    setOpenCommentsFor((prev) => (prev === postId ? null : postId));
  };
  const submitComment = (postId: string) => {
    // TODO: wire up your comments endpoint
    console.log('Submit comment for', postId, newComment);
    setNewComment('');
  };

  return (
    <>
      {posts.filter(Boolean).map((post) => {
        // 1) authorUsername from object
        const authorUsername = post.author?.username || 'Unknown User';
        // 2) only the author can edit/delete
        const iAmAuthor = !!(
          user &&
          post.author &&
          (post.author.id === user.id || post.author.username === user.username)
        );
        // 3) images array
        const images = post.images ?? [];
        // 4) formatted date
        const createdAt = post.created_at
          ? new Date(post.created_at).toLocaleString()
          : '';

        return (
          <Card key={post.id} className="mb-4 post-card">
            <Card.Body>
              <Card.Title>{post.title}</Card.Title>
              <Card.Subtitle className="mb-2 text-muted">
                By {authorUsername} on {createdAt}
              </Card.Subtitle>
              <Card.Text>{post.content}</Card.Text>

              {images.length > 0 && (
                <div className="d-flex flex-wrap mb-3">
                  {images.map((img) => (
                    <img
                      key={img.id}
                      src={img.image}
                      alt=""
                      style={{
                        width: 100,
                        height: 100,
                        objectFit: 'cover',
                        borderRadius: 4,
                        marginRight: 8,
                      }}
                    />
                  ))}
                </div>
              )}
            </Card.Body>

            <Card.Footer className="d-flex justify-content-between align-items-center">
              <div>
                {/* 👍 Like */}
                <ReactionButton postId={post.id} />

                {/* 💬 Comment */}
                <Button
                  variant="link"
                  className="p-0 me-3"
                  onClick={() => toggleComments(post.id)}
                >
                  💬 {post.comments_count ?? 0}
                </Button>

                {/* 🔗 Share */}
                <Button
                  variant="link"
                  className="p-0"
                  onClick={() => console.log('Share', post.id)}
                >
                  🔗 Share
                </Button>
              </div>

              {iAmAuthor && (
                <div>
                  {/* Edit */}
                  <Button
                    variant="outline-primary"
                    className="me-2"
                    onClick={() => openEdit(post)}
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
                        Updating…
                      </>
                    ) : (
                      'Edit'
                    )}
                  </Button>

                  {/* Delete */}
                  <Button
                    variant="outline-danger"
                    onClick={() =>
                      window.confirm('Delete this post?') && onDeletePost(post.id)
                    }
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
                        Deleting…
                      </>
                    ) : (
                      'Delete'
                    )}
                  </Button>
                </div>
              )}
            </Card.Footer>

            {openCommentsFor === post.id && (
              <Card.Footer>
                <Form
                  onSubmit={(e) => {
                    e.preventDefault();
                    submitComment(post.id);
                  }}
                >
                  <Form.Control
                    type="text"
                    placeholder="Write a comment…"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                  />
                </Form>
              </Card.Footer>
            )}
          </Card>
        );
      })}

      {/* Edit Modal */}
      {currentPost && (
        <EditPostModal
          show={showModal}
          onHide={closeEdit}
          post={currentPost}
          onSave={saveEdit}
        />
      )}
    </>
  );
};

export default Posts;
