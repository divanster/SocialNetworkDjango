import React from 'react';
import Post from '../FeedItem/Post';

interface PostType {
    id: number;
    title: string;
    content: string;
    author: string;
    created_at: string;
    updated_at: string;
    tags: { id: number; name: string }[];
    images: { id: number; image: string }[];
    ratings: { id: number; value: number; user: number }[];
}

interface PostsProps {
    posts: PostType[];  // Use the full post type
    onDelete: (id: number) => void;
    onUpdate: (updatedPost: PostType) => void;  // Pass a full post object to onUpdate
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
                    <button onClick={() => onUpdate(post)}>Update</button>  {/* Pass the full post */}
                </div>
            ))}
        </div>
    );
};

export default Posts;
