import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../../contexts/AuthContext';
import './ReactionBar.css';

const EMOJIS = ['👍','❤️','😂','😮','😢','😡'];

interface Props {
  postId: string;
  counts: Record<string, number>; // { "👍": 3, "❤️": 1 ... }
  onReacted: (emoji: string) => void;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const ReactionBar: React.FC<Props> = ({ postId, counts, onReacted }) => {
  const { token } = useAuth();
  const [hovering, setHovering] = useState(false);

  const sendReaction = async (emoji: string) => {
    if (!token) return;
    onReacted(emoji); // optimistic update
    await axios.post(`${API_URL}/posts/${postId}/reactions/`, { emoji }, {
      headers: { Authorization: `Bearer ${token}` },
    });
  };

  return (
    <div
      className="reaction-bar"
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
    >
      {/* Default Like button */}
      <button onClick={() => sendReaction('👍')}>Like</button>

      {/* Counts */}
      <div className="reaction-counts">
        {Object.entries(counts).map(([emoji, n]) => (
          <span key={emoji}>{emoji} {n}</span>
        ))}
      </div>

      {/* Emoji Picker */}
      {hovering && (
        <div className="emoji-picker">
          {EMOJIS.map((e) => (
            <span key={e} onClick={() => sendReaction(e)}>{e}</span>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReactionBar;
