import React from 'react';

export interface CommentType {
  id: string;
  user: string;         // username string from your DRF StringRelatedField
  content: string;
  created_at: string;
}

interface CommentProps {
  comment: CommentType;
  onDelete?: (id: string) => void;
}

const Comment: React.FC<CommentProps> = ({ comment, onDelete }) => {
  return (
    <div
      className="comment mb-2 p-2"
      style={{
        background: '#2f3640',
        borderRadius: 8,
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
        <strong style={{ color: '#00a8ff' }}>{comment.user}</strong>
        <small style={{ color: '#aaa' }}>
          {new Date(comment.created_at).toLocaleString()}
        </small>
      </div>
      <div style={{ marginTop: 4 }}>{comment.content}</div>
      {onDelete && (
        <button
          onClick={() => onDelete(comment.id)}
          style={{
            background: 'none',
            border: 'none',
            color: '#e74c3c',
            cursor: 'pointer',
            fontSize: '0.8rem',
            marginTop: 4,
          }}
        >
          Delete
        </button>
      )}
    </div>
  );
};

export default Comment;
