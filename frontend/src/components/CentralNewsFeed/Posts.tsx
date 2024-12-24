// frontend/src/components/CentralNewsFeed/Posts.tsx

import React from 'react';
import { Post as PostType } from '../../types/post';
import { Card, Button } from 'react-bootstrap';

interface PostsProps {
  posts: PostType[];
  onDelete: (id: number) => void;
  onUpdate: (updatedPost: PostType) => void;
}

const Posts: React.FC<PostsProps> = ({ posts, onDelete, onUpdate }) => {
  return (
    <div>
      {posts.map((post) => (
        <Card key={post.id} className="mb-3">
          <Card.Body>
            <Card.Title>{post.title}</Card.Title>
            <Card.Subtitle className="mb-2 text-muted">
              By {post.author} on {new Date(post.created_at).toLocaleString()}
            </Card.Subtitle>
            <Card.Text>{post.content}</Card.Text>
            {post.images && post.images.length > 0 && (
              <div className="mb-2">
                {post.images.map((img) => (
                  <img
                    key={img.id}
                    src={img.image}
                    alt="Post"
                    style={{ width: '100px', marginRight: '10px' }}
                  />
                ))}
              </div>
            )}
            <Button variant="danger" onClick={() => onDelete(post.id)}>
              Delete
            </Button>
            {/* Add an update button or modal as needed */}
          </Card.Body>
        </Card>
      ))}
    </div>
  );
};

export default Posts;
