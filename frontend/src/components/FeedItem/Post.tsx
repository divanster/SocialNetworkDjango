// frontend/src/components/CentralNewsFeed/Posts.tsx

import React from 'react';
import { Post as PostType } from '../../types/post';

interface PostsProps {
  posts: PostType[];
  onDeletePost: (id: string) => void;            // string ID
  onUpdatePost: (updatedPost: PostType) => void; // entire post object
  deletingPostIds: string[];                     // string array
  updatingPostIds: string[];                     // string array
}

const Posts: React.FC<PostsProps> = ({
  posts,
  onDeletePost,
  onUpdatePost,
  deletingPostIds,
  updatingPostIds,
}) => {
  return (
    <div className="posts">
      {posts.map((post) => (
        <div key={post.id} className="post">
          <h3>{post.title}</h3>
          <p>{post.content}</p>

          <button
            onClick={() => onDeletePost(post.id)}
            disabled={deletingPostIds.includes(post.id)}
          >
            Delete
          </button>

          <button
            onClick={() => onUpdatePost(post)}
            disabled={updatingPostIds.includes(post.id)}
          >
            Update
          </button>
        </div>
      ))}
    </div>
  );
};

export default Posts;
