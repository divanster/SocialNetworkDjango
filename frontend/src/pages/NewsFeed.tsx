// frontend/src/pages/NewsFeed.tsx
import React, { useEffect, useState } from 'react';
import fetchNewsFeed from '../services/api';
import { Post, Comment, Reaction, Album, Story } from '../components/FeedItem';

const NewsFeed: React.FC = () => {
    const [feed, setFeed] = useState<any>({ posts: [], comments: [], reactions: [], albums: [], stories: [] });

    useEffect(() => {
        const getFeed = async () => {
            const data = await fetchNewsFeed();
            setFeed(data);
        };
        getFeed();
    }, []);

    return (
        <div className="newsfeed-container">
            <h1>News Feed</h1>
            {feed.posts.map((post: any) => (
                <Post key={post.id} post={post} />
            ))}
            {feed.comments.map((comment: any) => (
                <Comment key={comment.id} comment={comment} />
            ))}
            {feed.reactions.map((reaction: any) => (
                <Reaction key={reaction.id} reaction={reaction} />
            ))}
            {feed.albums.map((album: any) => (
                <Album key={album.id} album={album} />
            ))}
            {feed.stories.map((story: any) => (
                <Story key={story.id} story={story} />
            ))}
        </div>
    );
};

export default NewsFeed;
