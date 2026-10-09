import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Button } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { API_URL } from '../../services/api';

interface ReactionButtonProps {
  postId: string;
  contentType?: 'post' | 'comment';
}

interface ReactionItem {
  user_username: string;
}

const ReactionButton: React.FC<ReactionButtonProps> = ({ postId, contentType = 'post' }) => {
  const { token, user } = useAuth();
  const [count, setCount] = useState(0);
  const [liked, setLiked] = useState(false);

  const api = axios.create({
    baseURL: API_URL,
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
  });

  useEffect(() => {
    if (!token) return;
    api
      .get(`/reactions/?content_type=${contentType}&object_id=${postId}`)
      .then((res) => {
        const arr: ReactionItem[] = Array.isArray(res.data) ? res.data : res.data.results ?? [];
        setCount(arr.length);
        setLiked(arr.some((r) => r.user_username === user?.username));
      })
      .catch(() => undefined);
  }, [postId, token, contentType, api, user?.username]);

  const toggle = async () => {
    try {
      if (liked) {
        await api.delete('/reactions/remove_reaction/', {
          data: { content_type: contentType, object_id: postId, emoji: 'like' },
        });
      } else {
        await api.post('/reactions/', {
          content_type: contentType,
          object_id: postId,
          emoji: 'like',
        });
      }
      const res = await api.get(`/reactions/?content_type=${contentType}&object_id=${postId}`);
      const arr: ReactionItem[] = Array.isArray(res.data) ? res.data : res.data.results ?? [];
      setCount(arr.length);
      setLiked(arr.some((r) => r.user_username === user?.username));
    } catch {
      // Keep current UI state if reaction refresh fails.
    }
  };

  return (
    <Button size="sm" variant={liked ? 'primary' : 'outline-primary'} onClick={toggle}>
      {liked ? <>👍 {count}</> : <>{count > 0 ? <>👍 {count}</> : '👍 Like'}</>}
    </Button>
  );
};

export default ReactionButton;
