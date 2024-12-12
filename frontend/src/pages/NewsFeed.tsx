import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { useWebSocket } from '../contexts/WebSocketManager';
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
  const { getSocket } = useWebSocket();
  const { token, loading } = useAuth(); // Include loading state
  const [posts, setPosts] = useState<PostType[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [error, setError] = useState<string | null>(null);

  /**
   * Handles WebSocket connection for posts and albums.
   */
  const connectWebSocket = useCallback(
    (url: string, onMessage: (event: MessageEvent) => void) => {
      if (!token) {
        console.error('No authentication token available for WebSocket connection.');
        return;
      }

      const socket = getSocket(`${url}?token=${token}`);
      if (!socket) return;

      socket.onmessage = onMessage;

      socket.onerror = (error) => {
        console.error(`WebSocket error for ${url}:`, error);
      };

      socket.onclose = (event) => {
        console.log(`WebSocket connection closed for ${url}:`, event);
        if (!event.wasClean) {
          console.log(`Reconnecting to ${url}...`);
          setTimeout(() => connectWebSocket(url, onMessage), 5000); // Retry after 5 seconds
        }
      };
    },
    [getSocket, token]
  );

  /**
   * Establishes WebSocket connections for posts and albums when token changes.
   */
  useEffect(() => {
    if (!loading && token) {
      connectWebSocket('ws://localhost:8000/ws/posts/', (event) => {
        const data = JSON.parse(event.data);
        if (data.message) {
          setPosts((prevPosts) => {
            const postExists = prevPosts.some((post) => post.id === data.message.id);
            if (!postExists) {
              return [data.message, ...prevPosts];
            }
            return prevPosts.map((post) =>
              post.id === data.message.id ? { ...post, ...data.message } : post
            );
          });
        } else {
          console.error('WebSocket error: No message field in response');
        }
      });

      connectWebSocket('ws://localhost:8000/ws/albums/', (event) => {
        const data = JSON.parse(event.data);
        if (data.message) {
          setAlbums((prevAlbums) => {
            const albumExists = prevAlbums.some((album) => album.id === data.message.id);
            if (!albumExists) {
              return [data.message, ...prevAlbums];
            }
            return prevAlbums.map((album) =>
              album.id === data.message.id ? { ...album, ...data.message } : album
            );
          });
        } else {
          console.error('WebSocket error: No message field in response');
        }
      });
    }
  }, [connectWebSocket, token, loading]);

  /**
   * Fetches the news feed data (posts and albums) when the component is mounted or token changes.
   */
  useEffect(() => {
    const fetchNewsFeedData = async () => {
      if (!token) {
        setError('User is not authenticated.');
        return;
      }

      try {
        const response = await axios.get(`${API_URL}/newsfeed/feed/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        setPosts(response.data.posts || []);
        setAlbums(response.data.albums || []);
      } catch (err) {
        console.error('Failed to fetch news feed data:', err);
        setError('Failed to fetch news feed data');
      }
    };

    if (token) {
      fetchNewsFeedData();
    } else {
      setError('User is not authenticated.');
    }
  }, [token]);

  /**
   * Deletes a post by ID.
   */
  const handleDeletePost = (id: number) => {
    setPosts((prevPosts) => prevPosts.filter((post) => post.id !== id));
  };

  /**
   * Updates a post with new data.
   */
  const handleUpdatePost = (updatedPost: PostType) => {
    setPosts((prevPosts) => prevPosts.map((post) => (post.id === updatedPost.id ? updatedPost : post)));
  };

  /**
   * Deletes an album by ID.
   */
  const handleDeleteAlbum = (id: number) => {
    setAlbums((prevAlbums) => prevAlbums.filter((album) => album.id !== id));
  };

  /**
   * Handles loading and error states for the NewsFeed component.
   */
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
