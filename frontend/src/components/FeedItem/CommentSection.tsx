import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';

interface CommentType {
  id: string;
  author_name: string;
  content: string;
  created_at: string;
}

interface Props {
  postId: string;
  comments: CommentType[];
  onAdded: (c: CommentType) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const CommentSection: React.FC<Props> = ({ postId, comments, onAdded }) => {
  const { token } = useAuth();
  const [text, setText] = useState('');

  const addComment = async () => {
    if (!text.trim() || !token) return;
    const { data } = await axios.post(
      `${API_URL}/posts/${postId}/comments/`,
      { content: text },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    onAdded(data);
    setText('');
  };

  return (
    <div className="comment-section">
      {comments.map((c) => (
        <div key={c.id} className="comment">
          <strong>{c.author_name}</strong> {c.content}
        </div>
      ))}
      <input
        placeholder="Write a comment…"
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && addComment()}
      />
    </div>
  );
};

export default CommentSection;
