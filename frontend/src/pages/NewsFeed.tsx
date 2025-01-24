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
    setToast({ show: true, message: 'Post created successfully!', variant: 'success' });
  };

  // Callback to add a new album
  const addNewAlbum = (newAlbum: AlbumType) => {
    setAlbums((prevAlbums) => [newAlbum, ...prevAlbums]);
    console.log('New album added:', newAlbum);
    setToast({ show: true, message: 'Album created successfully!', variant: 'success' });
  };

  // Handler for incoming posts messages via WebSocket
  const handlePostsMessage = useCallback(
    (data: any) => {
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
    },
    []
  );

  // Handler for incoming albums messages via WebSocket
  const handleAlbumsMessage = useCallback(
    (data: any) => {
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
    },
    []
  );

  // Establish WebSocket connections for 'posts' and 'albums'
  const { sendMessage: sendPostMessage } = useWebSocket('posts', { onMessage: handlePostsMessage });
  const { sendMessage: sendAlbumMessage } = useWebSocket('albums', { onMessage: handleAlbumsMessage });

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
      } catch (err: any) {
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
      setDeleteSuccess(`Post deleted successfully.`);
      setToast({ show: true, message: 'Post deleted successfully!', variant: 'success' });
    } catch (err: any) {
      console.error('Error deleting post:', err);
      setDeleteError('Error deleting post.');
      setToast({ show: true, message: 'Error deleting post.', variant: 'danger' });
    } finally {
      // Remove post ID from deleting list
      setDeletingPostIds((prev) => prev.filter((p) => p !== id));
    }
  };

  // Handler to delete an album
  const handleDeleteAlbum = async (id: number) => {
    if (!token) {
      setDeleteError('You must be logged in to delete an album.');
      return;
    }

    try {
      const response = await axios.delete(`${API_URL}/albums/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log(`Album with ID ${id} deleted successfully:`, response.status);

      // Remove the album from the local state upon successful deletion
      setAlbums((prev) => prev.filter((a) => a.id !== id));
      setDeleteSuccess('Album deleted successfully.');
      setToast({ show: true, message: 'Album deleted successfully!', variant: 'success' });
    } catch (err: any) {
      console.error('Error deleting album:', err);
      setDeleteError('Error deleting album.');
      setToast({ show: true, message: 'Error deleting album.', variant: 'danger' });
    }
  };

  // Handler to update a post
  const handleUpdatePost = async (updatedPost: PostType) => {
    if (!token) {
      setError('You must be logged in to update a post.');
      return;
    }

    setUpdatingPostIds((prev) => [...prev, updatedPost.id]);
    console.log(`Attempting to update post with ID ${updatedPost.id}`);

    try {
      const response = await axios.put(`${API_URL}/social/${updatedPost.id}/`, {
        title: updatedPost.title,
        content: updatedPost.content,
        // Include other fields if necessary
      }, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      console.log(`Post with ID ${updatedPost.id} updated successfully:`, response.status);

      // Update the post in the local state
      setPosts((prev) =>
        prev.map((p) => (p.id === updatedPost.id ? response.data : p))
      );
      setToast({ show: true, message: 'Post updated successfully!', variant: 'success' });
    } catch (err: any) {
      console.error('Error updating post:', err);
      setError('Error updating post.');
      setToast({ show: true, message: 'Error updating post.', variant: 'danger' });
    } finally {
      setUpdatingPostIds((prev) => prev.filter((p) => p !== updatedPost.id));
    }
  };

  // Handler to update an album
  const handleUpdateAlbum = async (updatedAlbum: AlbumType) => {
    if (!token) {
      setError('You must be logged in to update an album.');
      return;
    }

    try {
      const formData = new FormData();
      formData.append('title', updatedAlbum.title);
      formData.append('description', updatedAlbum.description);
      formData.append('visibility', updatedAlbum.visibility);
      if (updatedAlbum.photos) {
        Array.from(updatedAlbum.photos).forEach((photo) =>
          formData.append('image_files', photo.image)
        );
      }

      const response = await axios.put(`${API_URL}/albums/${updatedAlbum.id}/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log(`Album with ID ${updatedAlbum.id} updated successfully:`, response.status);

      // Update the album in the local state
      setAlbums((prev) =>
        prev.map((a) => (a.id === updatedAlbum.id ? response.data : a))
      );
      setToast({ show: true, message: 'Album updated successfully!', variant: 'success' });
    } catch (err: any) {
      console.error('Error updating album:', err);
      setError('Error updating album.');
      setToast({ show: true, message: 'Error updating album.', variant: 'danger' });
    }
  };

  return (
    <div className="newsfeed-container">
      {/* Left Sidebar */}
      <div className="left-sidebar">
        <Profile />
      </div>

      {/* Main Feed */}
      <div className="main-feed">
        {/* Create Post and Create Album Components */}
        <CreatePost onPostCreated={addNewPost} sendMessage={sendPostMessage} />
        <CreateAlbum onAlbumCreated={addNewAlbum} sendAlbumMessage={sendAlbumMessage} />

        {dataLoading ? (
          <div className="text-center mt-5">Loading...</div>
        ) : (
          <div>
            {/* Display error messages */}
            {error && <div className="alert alert-danger">{error}</div>}
            {deleteError && <div className="alert alert-danger">{deleteError}</div>}
            {deleteSuccess && <div className="alert alert-success">{deleteSuccess}</div>}

            {/* Posts Component */}
            <Posts
              posts={posts}
              onDeletePost={handleDeletePost}
              onUpdate={handleUpdatePost}
              deletingPostIds={deletingPostIds}
              updatingPostIds={updatingPostIds}
            />

            {/* Albums Component */}
            {albums.length > 0 ? (
              albums.map((album) => (
                <Album
                  key={album.id}
                  album={album}
                  onDelete={handleDeleteAlbum}
                  onUpdate={handleUpdateAlbum} // Pass onUpdate prop here
                />
              ))
            ) : (
              <div>No albums available</div>
            )}
          </div>
        )}
      </div>

      {/* Right Sidebar */}
      <div className="right-sidebar">
        <FriendRequests />
        <Birthdays />
        <Contacts />
      </div>

      {/* Toast Notifications */}
      <ToastContainer position="bottom-end">
        <Toast
          show={toast.show}
          onClose={() => setToast({ ...toast, show: false })}
          bg={toast.variant}
          delay={3000}
          autohide
        >
          <Toast.Body>{toast.message}</Toast.Body>
        </Toast>
      </ToastContainer>
    </div>
  );
};

export default NewsFeed;
