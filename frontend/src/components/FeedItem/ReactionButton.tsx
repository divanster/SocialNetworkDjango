import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Button } from 'react-bootstrap'
import { useAuth } from '../../contexts/AuthContext'

interface ReactionButtonProps {
  postId: string  // UUID of the object being reacted to
  contentType?: 'post' | 'comment'  // Specify content type (post or comment)
}

const ReactionButton: React.FC<ReactionButtonProps> = ({ postId, contentType = 'post' }) => {
  const { token, user } = useAuth()
  const [count, setCount] = useState(0)
  const [liked, setLiked] = useState(false)

  const api = axios.create({
    baseURL: process.env.REACT_APP_API_URL,
    headers: { Authorization: `Bearer ${token}` },
  })

  useEffect(() => {
    if (!token) return
    api
      .get(`/reactions/?content_type=${contentType}&object_id=${postId}`)
      .then((res) => {
        const arr = Array.isArray(res.data) ? res.data : res.data.results ?? []
        setCount(arr.length)
        setLiked(arr.some((r: any) => r.user === user?.username))
      })
      .catch(console.error)
  }, [postId, token, contentType, api, user?.username])

  const toggle = async () => {
    try {
      if (liked) {
        await api.delete('/reactions/remove_reaction/', {
          data: { content_type: contentType, object_id: postId, emoji: 'like' },
        })
      } else {
        await api.post('/reactions/', {
          content_type: contentType,
          object_id: postId,
          emoji: 'like',
        })
      }
      const res = await api.get(`/reactions/?content_type=${contentType}&object_id=${postId}`)
      const arr = Array.isArray(res.data) ? res.data : res.data.results ?? []
      setCount(arr.length)
      setLiked(!liked)
    } catch (err) {
      console.error('Reaction error', err)
    }
  }

  return (
    <Button size="sm" variant={liked ? 'primary' : 'outline-primary'} onClick={toggle}>
      {liked ? <>👍 {count}</> : <>{count > 0 ? <>👍 {count}</> : '👍 Like'}</>}
    </Button>
  )
}

export default ReactionButton
