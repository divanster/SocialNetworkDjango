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
  ratings: { id: number; value: number; user: number }[]; // Consider enriching the user object here
}

interface PostsProps {
  posts: PostType[]; // Use the full post type
  onDelete: (id: number) => void; // Function to handle post deletion
  onUpdate: (updatedPost: PostType) => void; // Function to handle post update (pass full post object)
}

const Posts: React.FC<PostsProps> = ({ posts, onDelete, onUpdate }) => {
  // Handle the case where there are no posts
  if (!posts || posts.length === 0) {
    return <p>No posts available</p>;
  }

  return (
    <div className="posts">
      {/* Map through each post to render it */}
      {posts.map(post => (
        <div key={post.id} className="post-item">
          {/* Render the Post component */}
          <Post post={post} />

          {/* Button to delete the post */}
          <button
            onClick={() => onDelete(post.id)}
            className="delete-button">
            Delete
          </button>

          {/* Button to update the post */}
          <button
            onClick={() => onUpdate(post)}
            className="update-button">
            Update
          </button>
        </div>
      ))}
    </div>
  );
};

export default Posts;
