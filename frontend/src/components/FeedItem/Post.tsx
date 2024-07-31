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
            <div>
                <strong>Tags:</strong>
                {post.tags.map(tag => (
                    <span key={tag.id} className="tag">{tag.name}</span>
                ))}
            </div>
            <div>
                <strong>Images:</strong>
                {post.images.map(image => (
                    <img key={image.id} src={image.image} alt="Post" style={{ width: '100%', height: 'auto' }} />
                ))}
            </div>
            <div>
                <strong>Ratings:</strong>
                {post.ratings.map(rating => (
                    <span key={rating.id} className="rating">{rating.value} stars by user {rating.user}</span>
                ))}
            </div>
            <p className="text-muted">
                Posted on {new Date(post.created_at).toLocaleDateString()}
                {post.created_at !== post.updated_at && ` (updated on ${new Date(post.updated_at).toLocaleDateString()})`}
            </p>
        </div>
    );
};

export default Post;
