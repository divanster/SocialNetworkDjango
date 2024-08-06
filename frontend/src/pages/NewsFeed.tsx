import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useWebSocket } from '../contexts/WebSocketContext';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import CreatePost from '../components/CentralNewsFeed/CreatePost';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';
import './NewsFeed.css';
import { Post } from '../types/post';
import { Album as AlbumType } from '../types/album';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const getHeaders = () => ({
  headers: {
    Authorization: `Bearer ${localStorage.getItem('token') || ''}`,
  },
});

const NewsFeed: React.FC = () => {
  const { socket } = useWebSocket();
  const [posts, setPosts] = useState<Post[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (socket) {
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.message) {
          setPosts((prevPosts) => [data.message, ...prevPosts]);
        } else {
          console.error('WebSocket error: No message field in response');
        }
      };

      socket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      socket.onclose = (event) => {
        console.log('WebSocket connection closed:', event);
      };
    }
  }, [socket]);

  useEffect(() => {
    const fetchNewsFeedData = async () => {
      try {
        const response = await axios.get(`${API_URL}/newsfeed/feed/`, getHeaders());
        setPosts(response.data.posts || []);
        setAlbums(response.data.albums || []);
      } catch (err) {
        console.error('Failed to fetch news feed data:', err);
        setError('Failed to fetch news feed data');
      } finally {
        setLoading(false);
      }
    };
    fetchNewsFeedData();
  }, []);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

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
      <div className="central-news-feed">
        <CreatePost />
        <CreateAlbum />
        {posts.length > 0 ? <Posts posts={posts} /> : <p>No posts available</p>}
        {albums.length > 0 ? albums.map((album) => (
          <Album key={album.id} album={album} />
        )) : <p>No albums available</p>}
      </div>
    </div>
  );
};

export default NewsFeed;
