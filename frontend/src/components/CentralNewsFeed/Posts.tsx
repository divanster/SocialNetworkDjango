// frontend/src/components/CentralNewsFeed/Posts.tsx
import React, { useState } from 'react'
import { Card, Button, Spinner } from 'react-bootstrap'
import EditPostModal from './EditPostModal'
import ReactionButton from '../FeedItem/ReactionButton'
import CommentSection from '../FeedItem/CommentSection'
import { useAuth } from '../../contexts/AuthContext'
import { Post as PostType } from '../../types/post'
import Avatar from '../Common/Avatar'
import UserIdentityLink from '../Common/UserIdentityLink'

interface PostsProps {
  posts: PostType[]
  onDeletePost: (id: string) => void
  onUpdatePost: (updated: PostType) => void
  deletingPostIds: string[]
  updatingPostIds: string[]
}

const Posts: React.FC<PostsProps> = ({
  posts,
  onDeletePost,
  onUpdatePost,
  deletingPostIds,
  updatingPostIds,
}) => {
  const { user } = useAuth()
  const [showModal, setShowModal] = useState(false)
  const [currentPost, setCurrentPost] = useState<PostType | null>(null)
  const [openCommentsFor, setOpenCommentsFor] = useState<string | null>(null)

  const openEdit = (post: PostType) => {
    setCurrentPost(post)
    setShowModal(true)
  }
  const closeEdit = () => {
    setCurrentPost(null)
    setShowModal(false)
  }
  const saveEdit = (updated: PostType) => {
    onUpdatePost(updated)
    closeEdit()
  }

  const formatTimestamp = (value?: string) => {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return new Intl.DateTimeFormat(undefined, {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <>
      {posts.map((post) => {
        const authorUsername = post.author?.username || post.user || 'Unknown User'
        const authorId = post.author?.id
        const iAmAuthor =
          Boolean(user && (
            (authorId && authorId === user.id) ||
            authorUsername === user.username
          ))
        const images = post.images ?? []
        const createdAt = formatTimestamp(post.created_at)
        const showTitle = Boolean(post.title && post.title.trim().length > 0)

        return (
          <Card key={post.id} className="mb-4 post-card">
            <Card.Body>
              <div className="post-header">
                <UserIdentityLink userId={authorId} ariaLabel={`Open ${authorUsername} profile`}>
                  <Avatar
                    size={40}
                    name={authorUsername}
                    alt={`${authorUsername} avatar`}
                  />
                </UserIdentityLink>
                <div>
                  <div className="post-author">
                    <UserIdentityLink userId={authorId}>{authorUsername}</UserIdentityLink>
                  </div>
                  <div className="post-meta">{createdAt}</div>
                </div>
              </div>
              {showTitle && <Card.Title className="mt-3 mb-2">{post.title}</Card.Title>}
              <Card.Text>{post.content}</Card.Text>
              {images.length > 0 && (
                <div className="d-flex flex-wrap mb-3">
                  {images.map((img) => (
                    <img
                      key={img.id}
                      src={img.image}
                      alt={`${authorUsername} post`}
                      style={{
                        width: 132,
                        height: 132,
                        objectFit: 'cover',
                        borderRadius: 8,
                        marginRight: 8,
                        marginBottom: 8,
                      }}
                    />
                  ))}
                </div>
              )}
              <div className="post-stats">
                {typeof post.reactions_count === 'number' && (
                  <span>{post.reactions_count} likes</span>
                )}
                {typeof post.comments_count === 'number' && (
                  <span>{post.comments_count} comments</span>
                )}
              </div>
            </Card.Body>

            <Card.Footer className="d-flex justify-content-between align-items-center">
              <div className="d-flex align-items-center">
                <ReactionButton postId={post.id} />
                <Button
                  variant="link"
                  className="p-0 ms-3"
                  onClick={() =>
                    setOpenCommentsFor((prev) =>
                      prev === post.id ? null : post.id
                    )
                  }
                >
                  💬 Comments
                </Button>
                <Button
                  variant="link"
                  className="p-0 ms-3"
                  type="button"
                  aria-label="Share (coming soon)"
                  disabled
                >
                  🔗 Share
                </Button>
              </div>

              {iAmAuthor && (
                <div>
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
                        />
                        {' Updating…'}
                      </>
                    ) : (
                      'Edit'
                    )}
                  </Button>
                  <Button
                    variant="outline-danger"
                    onClick={() =>
                      window.confirm('Delete this post?') &&
                      onDeletePost(post.id)
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
                        />
                        {' Deleting…'}
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
                <CommentSection postId={post.id} />
              </Card.Footer>
            )}
          </Card>
        )
      })}

      {currentPost && (
        <EditPostModal
          show={showModal}
          onHide={closeEdit}
          post={currentPost}
          onSave={saveEdit}
        />
      )}
    </>
  )
}

export default Posts
