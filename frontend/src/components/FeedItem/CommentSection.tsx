import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { useAuth } from '../../contexts/AuthContext'
import { Form, Button, ListGroup, Alert, Spinner } from 'react-bootstrap'

interface CommentType {
  id: string
  user: string  // serialized as StringRelatedField
  content: string
  created_at: string
}

interface Props {
  postId: string
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'

const CommentSection: React.FC<Props> = ({ postId }) => {
  const { token, user } = useAuth()
  const [comments, setComments] = useState<CommentType[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [newComment, setNewComment] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const api = axios.create({
    baseURL: API_URL,
    headers: { Authorization: `Bearer ${token}` },
  })

  useEffect(() => {
    setLoading(true)
    api
      .get(`/comments/comments/?post_id=${postId}`)
      .then((res) => {
        const arr = Array.isArray(res.data) ? res.data : res.data.results ?? []
        setComments(arr)
        setError(null)
      })
      .catch((err) => {
        console.error('Failed to fetch comments', err)
        setError('Could not load comments.')
      })
      .finally(() => setLoading(false))
  }, [postId, token])

  const addComment = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!newComment.trim() || !token) return
    setSubmitting(true)
    try {
      const res = await api.post('/comments/comments/', {
        content: newComment,
        content_type: 'post',
        object_id: postId,
      })
      setComments((prev) => [res.data, ...prev])
      setNewComment('')
      setError(null)
    } catch (err: any) {
      console.error('Failed to post comment', err)
      setError(err.response?.data?.detail || 'Could not post comment.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="mt-3">
      {error && <Alert variant="danger">{error}</Alert>}
      <Form onSubmit={addComment} className="d-flex mb-2">
        <Form.Control
          type="text"
          placeholder="Write a comment…"
          value={newComment}
          onChange={(e) => setNewComment(e.target.value)}
          disabled={!user || submitting}
        />
        <Button type="submit" disabled={!newComment.trim() || submitting} className="ms-2">
          {submitting ? <Spinner animation="border" size="sm" /> : 'Post'}
        </Button>
      </Form>

      {loading ? (
        <div className="text-center"><Spinner /></div>
      ) : (
        <ListGroup variant="flush">
          {comments.map((c) => (
            <ListGroup.Item key={c.id}>
              <strong>{c.user}</strong> •{' '}
              <em>{new Date(c.created_at).toLocaleString()}</em>
              <div>{c.content}</div>
            </ListGroup.Item>
          ))}
          {comments.length === 0 && <div className="text-center text-muted">No comments yet.</div>}
        </ListGroup>
      )}
    </div>
  )
}

export default CommentSection
