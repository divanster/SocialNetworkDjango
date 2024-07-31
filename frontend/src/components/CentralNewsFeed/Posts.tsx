// frontend/src/components/CentralNewsFeed/Posts.tsx
import React from 'react';
import Post from '../FeedItem/Post';

interface PostsProps {
    posts: {
        id: number;
        title: string;
        content: string;
        author: string;
        created_at: string;
        updated_at: string;
        tags: { id: number; name: string }[];
        images: { id: number; image: string }[];
        ratings: { id: number; value: number; user: number }[];
    }[];
}

const Posts: React.FC<PostsProps> = ({ posts }) => {
    if (!posts || posts.length === 0) {
        return <p>No posts available</p>;
    }

    return (
        <div className="posts">
            {posts.map(post => (
                <Post key={post.id} post={post} />
            ))}
        </div>
    );
};

export default Posts;
