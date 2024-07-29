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
        </div>
    );
};

export default Post;

// frontend/src/components/FeedItem/Comment.tsx
import React from 'react';

interface CommentProps {
    comment: {
        id: number;
        user: number;
        post: number;
        content: string;
        created_at: string;
        updated_at: string;
    };
}

const Comment: React.FC<CommentProps> = ({ comment }) => {
    return (
        <div className="comment">
            <p>{comment.content}</p>
            <p><strong>User:</strong> {comment.user}</p>
        </div>
    );
};

export default Comment;

// frontend/src/components/FeedItem/Reaction.tsx
import React from 'react';

interface ReactionProps {
    reaction: {
        id: number;
        user: number;
        post: number;
        emoji: string;
        created_at: string;
    };
}

const Reaction: React.FC<ReactionProps> = ({ reaction }) => {
    return (
        <div className="reaction">
            <p><strong>User:</strong> {reaction.user}</p>
            <p><strong>Emoji:</strong> {reaction.emoji}</p>
        </div>
    );
};

export default Reaction;

// frontend/src/components/FeedItem/Album.tsx
import React from 'react';

interface AlbumProps {
    album: {
        id: number;
        user: number;
        title: string;
        description: string;
        created_at: string;
        updated_at: string;
        photos: { id: number; album: number; image: string; description: string; created_at: string }[];
    };
}

const Album: React.FC<AlbumProps> = ({ album }) => {
    return (
        <div className="album">
            <h3>{album.title}</h3>
            <p>{album.description}</p>
        </div>
    );
};

export default Album;

// frontend/src/components/FeedItem/Story.tsx
import React from 'react';

interface StoryProps {
    story: {
        id: number;
        user: number;
        content: string;
        created_at: string;
        updated_at: string;
    };
}

const Story: React.FC<StoryProps> = ({ story }) => {
    return (
        <div className="story">
            <p>{story.content}</p>
        </div>
    );
};

export default Story;

// frontend/src/components/FeedItem/index.tsx
export { default as Post } from './Post';
export { default as Comment } from './Comment';
export { default as Reaction } from './Reaction';
export { default as Album } from './Album';
export { default as Story } from './Story';
