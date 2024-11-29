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

      {/* Display tags */}
      <div>
        <strong>Tags:</strong>
        {post.tags.length > 0 ? (
          post.tags.map((tag) => <span key={tag.id} className="tag">{tag.name}</span>)
        ) : (
          <span>No tags available</span>
        )}
      </div>

      {/* Display images */}
      <div>
        <strong>Images:</strong>
        {post.images.length > 0 ? (
          post.images.map((image) => (
            <div key={image.id} className="image-container">
              <img src={image.image} alt={`Post image ${image.id}`} style={{ width: '100%', height: 'auto' }} />
            </div>
          ))
        ) : (
          <p>No images available</p>
        )}
      </div>

      {/* Display ratings */}
      <div>
        <strong>Ratings:</strong>
        {post.ratings.length > 0 ? (
          post.ratings.map((rating) => (
            <span key={rating.id} className="rating">
              {rating.value} stars by user {rating.user}
            </span>
          ))
        ) : (
          <p>No ratings available</p>
        )}
      </div>

      {/* Display creation and update times */}
      <p className="text-muted">
        Posted on {new Date(post.created_at).toLocaleDateString()}
        {post.created_at !== post.updated_at && ` (updated on ${new Date(post.updated_at).toLocaleDateString()})`}
      </p>
    </div>
  );
};

export default Post;
