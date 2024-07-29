// frontend/src/components/FeedItem/Comment.tsx
import React from 'react';

interface CommentProps {
    comment: {
        id: number;
        user: number;
        post: number;
        content: string;
        created_at: string;
        updated_at: string;
    };
}

const Comment: React.FC<CommentProps> = ({ comment }) => {
    return (
        <div className="comment">
            <p>{comment.content}</p>
            <p><strong>User:</strong> {comment.user}</p>
        </div>
    );
};

export default Comment;
