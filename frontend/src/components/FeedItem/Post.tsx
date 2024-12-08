// Post.tsx

import React from 'react';

interface PostProps {
  post: {
    id: number;
    title: string;
    content: string;
    author: string;
    created_at: string;
    updated_at: string;
    tags?: { id: number; name: string }[]; // Optional array
    images?: { id: number; image: string }[]; // Optional array
    ratings?: { id: number; value: number; user: number }[]; // Optional array
  };
}

const Post: React.FC<PostProps> = ({ post }) => {
  return (
    <div className="post">
      <h2>{post.title}</h2>
      <p>{post.content}</p>
      <p>Author: {post.author}</p>
      <p>Created: {new Date(post.created_at).toLocaleString()}</p>
      <p>Updated: {new Date(post.updated_at).toLocaleString()}</p>

      {/* Safeguards for undefined properties */}
      {post.tags && post.tags.length > 0 && (
        <div>
          <h4>Tags:</h4>
          <ul>
            {post.tags.map((tag) => (
              <li key={tag.id}>{tag.name}</li>
            ))}
          </ul>
        </div>
      )}

      {post.images && post.images.length > 0 && (
        <div>
          <h4>Images:</h4>
          <ul>
            {post.images.map((image) => (
              <li key={image.id}>
                <img src={image.image} alt={`Image ${image.id}`} width="100" />
              </li>
            ))}
          </ul>
        </div>
      )}

      {post.ratings && post.ratings.length > 0 && (
        <div>
          <h4>Ratings:</h4>
          <ul>
            {post.ratings.map((rating) => (
              <li key={rating.id}>
                {rating.value} (User: {rating.user})
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Post;
