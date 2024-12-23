// frontend/src/pages/NewsFeed.tsx

import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import useWebSocket from '../hooks/useWebSocket';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import CreatePost from '../components/CentralNewsFeed/CreatePost';
import CreateAlbum from '../components/CentralNewsFeed/CreateAlbum';
import './NewsFeed.css';
import { Post as PostType } from '../types/post';
import { Album as AlbumType } from '../types/album';
import { useAuth } from '../contexts/AuthContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const NewsFeed: React.FC = () => {
  const { token, loading: authLoading } = useAuth();

  const [posts, setPosts] = useState<PostType[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [dataLoading, setDataLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Handler for incoming posts messages
  const handlePostsMessage = useCallback((data: any) => {
    if (data.message) {
      setPosts((prev) => {
        const exists = prev.some((p) => p.id === data.message.id);
        return exists ? prev : [data.message, ...prev];
      });
    } else {
      console.error('Posts WebSocket error: no "message" field');
    }
  }, []);

  // Handler for incoming albums messages
  const handleAlbumsMessage = useCallback((data: any) => {
    if (data.message) {
      setAlbums((prev) => {
        const exists = prev.some((a) => a.id === data.message.id);
        return exists ? prev : [data.message, ...prev];
      });
    } else {
      console.error('Albums WebSocket error: no "message" field');
    }
  }, []);

  // Establish WebSocket connections for 'posts' and 'albums'
  useWebSocket('posts', { onMessage: handlePostsMessage });
  useWebSocket('albums', { onMessage: handleAlbumsMessage });

  // Fetch data if we have a token and not loading
  useEffect(() => {
    if (authLoading) {
      // Authentication is still loading
      return;
    }

    if (!token) {
      setError('User is not authenticated.');
      setDataLoading(false);
      return;
    }

    const fetchData = async () => {
      try {
        const response = await axios.get(`${API_URL}/newsfeed/feed/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPosts(response.data.posts || []);
        setAlbums(response.data.albums || []);
      } catch (err) {
        console.error('Failed to fetch news feed data:', err);
        setError('Failed to fetch news feed data');
      } finally {
        setDataLoading(false);
      }
    };
    fetchData();
  }, [token, authLoading]);

  // Local event handlers to update state
  const handleDeletePost = (id: number) => {
    setPosts((prev) => prev.filter((p) => p.id !== id));
  };

  const handleUpdatePost = (updatedPost: PostType) => {
    setPosts((prev) => prev.map((p) => (p.id === updatedPost.id ? updatedPost : p)));
  };

  const handleDeleteAlbum = (id: number) => {
    setAlbums((prev) => prev.filter((a) => a.id !== id));
  };

  if (authLoading || dataLoading) return <p>Loading...</p>;
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
        {posts.length > 0 ? (
          <Posts posts={posts} onDelete={handleDeletePost} onUpdate={handleUpdatePost} />
        ) : (
          <p>No posts available</p>
        )}
        {albums.length > 0 ? (
          albums.map((album) => (
            <Album key={album.id} album={album} onDelete={handleDeleteAlbum} />
          ))
        ) : (
          <p>No albums available</p>
        )}
      </div>
    </div>
  );
};

export default NewsFeed;
