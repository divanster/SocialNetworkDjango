import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import CreatePost from '../components/CentralNewsFeed/CreatePost';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';
import './NewsFeed.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getHeaders = () => ({
    headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
    }
});

const NewsFeed: React.FC = () => {
    const [posts, setPosts] = useState<any[]>([]);
    const [albums, setAlbums] = useState<any[]>([]);

    useEffect(() => {
        const getNewsFeedData = async () => {
            try {
                const response = await axios.get(`${API_URL}/newsfeed/feed/`, getHeaders());
                console.log('Posts data:', response.data);
                setPosts(response.data.posts || []);
                setAlbums(response.data.albums || []);
            } catch (error) {
                console.error('Error fetching news feed data:', error);
            }
        };

        getNewsFeedData();
    }, []);

    return (
        <div className="newsfeed-container">
            <div className="left-sidebar">
                <Profile />
            </div>
            <div className="right-sidebar">
                <FriendRequests />
                <Birthdays />
                <Contacts />
            </div>
            <div className="central-news-feed newsfeed-content">
                <CreatePost />
                <CreateAlbum />
                {posts.length > 0 ? <Posts posts={posts} /> : <p>No posts available</p>}
                {albums.length > 0 ? albums.map(album => (
                    <Album key={album.id} album={album} />
                )) : <p>No albums available</p>}
            </div>
        </div>
    );
};

export default NewsFeed;
