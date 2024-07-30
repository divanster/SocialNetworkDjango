// frontend/src/components/CentralNewsFeed/Posts.tsx
import React from 'react';
import { Post } from '../FeedItem';

const Posts: React.FC<{ posts: any[] }> = ({ posts }) => {
    return (
        <div className="posts">
            {posts.map((post) => (
                <Post key={post.id} post={post} />
            ))}
        </div>
    );
};

export default Posts;
