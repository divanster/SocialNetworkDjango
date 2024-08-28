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
    onDelete: (id: number) => void;  // Handler to delete a post
    onUpdate: (updatedPost: {
        id: number;
        title: string;
        content: string;
        author: string;
        created_at: string;
        updated_at: string;
        tags: { id: number; name: string }[];
        images: { id: number; image: string }[];
        ratings: { id: number; value: number; user: number }[];
    }) => void;  // Handler to update a post
}

const Posts: React.FC<PostsProps> = ({ posts, onDelete, onUpdate }) => {
    if (!posts || posts.length === 0) {
        return <p>No posts available</p>;
    }

    return (
        <div className="posts">
            {posts.map(post => (
                <div key={post.id}>
                    <Post post={post} />
                    <button onClick={() => onDelete(post.id)}>Delete</button>
                    <button onClick={() => onUpdate(post)}>Update</button>
                </div>
            ))}
        </div>
    );
};

export default Posts;
