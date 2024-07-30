// frontend/src/components/FeedItem/Post.tsx
import React from 'react';

interface PostProps {
    post: {
        id: number;
        title: string;
        content: string;
        author: string;
        created_at: string;
        updated_at: string;
        tags: { id: number; name: string }[];
        images: { id: number; image: string }[];
        ratings: { id: number; value: number; user: number }[];
    };
}

const Post: React.FC<PostProps> = ({ post }) => {
    return (
        <div className="post">
            <h2>{post.title}</h2>
            <p>{post.content}</p>
            <p><strong>Author:</strong> {post.author}</p>
        </div>
    );
};

export default Post;
