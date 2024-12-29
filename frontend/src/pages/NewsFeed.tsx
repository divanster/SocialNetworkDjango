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
import { Toast, ToastContainer } from 'react-bootstrap';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const NewsFeed: React.FC = () => {
  const { token, loading: authLoading } = useAuth();

  const [posts, setPosts] = useState<PostType[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [dataLoading, setDataLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);
  const [updatingPostIds, setUpdatingPostIds] = useState<number[]>([]);
  const [deletingPostIds, setDeletingPostIds] = useState<number[]>([]);

  const [toast, setToast] = useState<{ show: boolean; message: string; variant: string }>({
    show: false,
    message: '',
    variant: 'success',
  });

  // Callback to add a new post
  const addNewPost = (newPost: PostType) => {
    setPosts((prevPosts) => [newPost, ...prevPosts]);
    console.log('New post added:', newPost);
  };

  // Callback to add a new album
  const addNewAlbum = (newAlbum: AlbumType) => {
    setAlbums((prevAlbums) => [newAlbum, ...prevAlbums]);
    console.log('New album added:', newAlbum);
  };

  // Handler for incoming posts messages via WebSocket
  const handlePostsMessage = useCallback((data: any) => {
    if (data.message) {
      setPosts((prev) => {
        const exists = prev.some((p) => p.id === data.message.id);
        if (!exists) {
          console.log('New post received via WebSocket:', data.message);
          return [data.message, ...prev];
        }
        return prev;
      });
    } else {
      console.error('Posts WebSocket error: no "message" field');
    }
  }, []);

  // Handler for incoming albums messages via WebSocket
  const handleAlbumsMessage = useCallback((data: any) => {
    if (data.message) {
      setAlbums((prev) => {
        const exists = prev.some((a) => a.id === data.message.id);
        if (!exists) {
          console.log('New album received via WebSocket:', data.message);
          return [data.message, ...prev];
        }
        return prev;
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
        console.log('Fetching news feed data...');
        const response = await axios.get(`${API_URL}/newsfeed/feed/`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        setPosts(response.data.posts || []);
        setAlbums(response.data.albums || []);
        console.log('Fetched posts:', response.data.posts);
        console.log('Fetched albums:', response.data.albums);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch news feed data:', err);
        setError('Failed to fetch news feed data');
      } finally {
        setDataLoading(false);
      }
    };
    fetchData();
  }, [token, authLoading]);

  // Handler to delete a post
  const handleDeletePost = async (id: number) => {
    if (!token) {
      setDeleteError('You must be logged in to delete a post.');
      return;
    }

    // Add post ID to deleting list
    setDeletingPostIds((prev) => [...prev, id]);
    console.log(`Attempting to delete post with ID ${id}`);

    try {
      const response = await axios.delete(`${API_URL}/social/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log(`Post with ID ${id} deleted successfully:`, response.status);

      // Remove the post from the local state upon successful deletion
      setPosts((prev) => prev.filter((p) => p.id !== id));
      setDeleteSuccess('Post deleted successfully.');
      setDeleteError(null);
    } catch (err) {
      console.error('Error deleting post:', err);
      if (axios.isAxiosError(err)) {
        setDeleteError(err.response?.data?.detail || 'Failed to delete the post.');
      } else {
        setDeleteError('An unexpected error occurred.');
      }
      setDeleteSuccess(null);
    } finally {
      // Remove post ID from deleting list
      setDeletingPostIds((prev) => prev.filter((postId) => postId !== id));
    }
  };

  // Handler to update a post
  const handleUpdatePost = async (updatedPost: PostType) => {
    if (!token) {
      setError('You must be logged in to update a post.');
      return;
    }

    // Add post ID to updating list
    setUpdatingPostIds((prev) => [...prev, updatedPost.id]);
    console.log(`Attempting to update post with ID ${updatedPost.id}`);

    try {
      const response = await axios.put(`${API_URL}/social/${updatedPost.id}/`, updatedPost, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log(`Post with ID ${updatedPost.id} updated successfully:`, response.data);

      // Update the post in the local state
      setPosts((prev) => prev.map((p) => (p.id === updatedPost.id ? response.data : p)));
      setToast({ show: true, message: 'Post updated successfully!', variant: 'success' });
      setDeleteError(null);
    } catch (err) {
      console.error('Error updating post:', err);
      if (axios.isAxiosError(err)) {
        setDeleteError(err.response?.data?.detail || 'Failed to update the post.');
      } else {
        setDeleteError('An unexpected error occurred.');
      }
      setToast({ show: false, message: '', variant: 'success' });
    } finally {
      // Remove post ID from updating list
      setUpdatingPostIds((prev) => prev.filter((postId) => postId !== updatedPost.id));
    }
  };

  // Handler to delete an album
  const handleDeleteAlbum = async (id: number) => {
    if (!token) {
      setDeleteError('You must be logged in to delete an album.');
      return;
    }

    console.log(`Attempting to delete album with ID ${id}`);

    try {
      const response = await axios.delete(`${API_URL}/albums/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log(`Album with ID ${id} deleted successfully:`, response.status);

      setAlbums((prev) => prev.filter((a) => a.id !== id));
      setToast({ show: true, message: 'Album deleted successfully!', variant: 'success' });
      setDeleteError(null);
    } catch (err) {
      console.error('Error deleting album:', err);
      if (axios.isAxiosError(err)) {
        setDeleteError(err.response?.data?.detail || 'Failed to delete the album.');
      } else {
        setDeleteError('An unexpected error occurred.');
      }
    }
  };

  if (authLoading || dataLoading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div className="newsfeed-container">
      {/* Toast Notifications */}
      <ToastContainer position="top-end" className="p-3">
        <Toast
          onClose={() => setToast({ ...toast, show: false })}
          show={toast.show}
          bg={toast.variant}
          delay={3000}
          autohide
        >
          <Toast.Body>{toast.message}</Toast.Body>
        </Toast>
      </ToastContainer>

      {/* Display delete success or error messages */}
      {deleteSuccess && <div className="alert alert-success">{deleteSuccess}</div>}
      {deleteError && <div className="alert alert-danger">{deleteError}</div>}

      <div className="left-sidebar">
        <Profile />
      </div>
      <div className="right-sidebar">
        <FriendRequests />
        <Birthdays />
        <Contacts />
      </div>
      <div className="central-news-feed">
        <CreatePost onPostCreated={addNewPost} />
        <CreateAlbum onAlbumCreated={addNewAlbum} />
        {posts.length > 0 ? (
          <Posts
            posts={posts}
            onDelete={handleDeletePost}
            onUpdate={handleUpdatePost}
            deletingPostIds={deletingPostIds}
            updatingPostIds={updatingPostIds}
          />
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
