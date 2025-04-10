// src/pages/NewsFeed.tsx
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import useWebSocket from '../hooks/useWebSocket';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import SharedItem from '../components/FeedItem/SharedItem';
import Profile from '../components/LeftSidebar/Profile';
import FriendRequests from '../components/RightSidebar/FriendRequests';
import Birthdays from '../components/RightSidebar/Birthdays';
import Contacts from '../components/RightSidebar/Contacts';
import CreatePosting from '../components/CentralNewsFeed/CreatePosting';
import './NewsFeed.css';

import { Post as PostType } from '../types/post';
import { Album as AlbumType } from '../types/album';
import { SharedItem as SharedItemType } from '../types/sharedItem';
import { useAuth } from '../contexts/AuthContext';
import { Toast, ToastContainer } from 'react-bootstrap';

// Import online status context
import { useOnlineStatus } from '../contexts/OnlineStatusContext';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const NewsFeed: React.FC = () => {
  const { token, user, loading: authLoading } = useAuth();

  const [posts, setPosts] = useState<PostType[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [sharedItems, setSharedItems] = useState<SharedItemType[]>([]);
  const [dataLoading, setDataLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [deleteSuccess, setDeleteSuccess] = useState<string | null>(null);

  const [updatingPostIds, setUpdatingPostIds] = useState<string[]>([]);
  const [deletingPostIds, setDeletingPostIds] = useState<string[]>([]);

  const [toast, setToast] = useState<{ show: boolean; message: string; variant: string }>({
    show: false,
    message: '',
    variant: 'success',
  });

  // Import online status data
  const { onlineUsers, userDetails } = useOnlineStatus();

  // Callbacks for adding new items (unchanged)
  const addNewPost = (newPost: PostType) => {
    setPosts((prevPosts) => [newPost, ...prevPosts]);
    setToast({ show: true, message: 'Post created successfully!', variant: 'success' });
  };

  const addNewAlbum = (newAlbum: AlbumType) => {
    setAlbums((prevAlbums) => [newAlbum, ...prevAlbums]);
    setToast({ show: true, message: 'Album created successfully!', variant: 'success' });
  };

  const addNewSharedItem = (newSharedItem: SharedItemType) => {
    setSharedItems((prevSharedItems) => [newSharedItem, ...prevSharedItems]);
    setToast({ show: true, message: 'Content shared successfully!', variant: 'success' });
  };

  // WebSocket handlers (unchanged)
  const handlePostsMessage = useCallback(
    (data: any) => {
      if (data.message && data.type === 'post') {
        setPosts((prev) => {
          const exists = prev.some((p) => p.id === data.message.id);
          return exists ? prev : [data.message, ...prev];
        });
      } else if (data.message && data.type === 'shared_item') {
        setSharedItems((prev) => {
          const exists = prev.some((s) => s.id === data.message.id);
          return exists ? prev : [data.message, ...prev];
        });
      }
    },
    []
  );

  const handleAlbumsMessage = useCallback(
    (data: any) => {
      if (data.message && data.type === 'album') {
        setAlbums((prev) => {
          const exists = prev.some((a) => a.id === data.message.id);
          return exists ? prev : [data.message, ...prev];
        });
      }
    },
    []
  );

  // Use our custom WebSocket hook for posts and albums.
  const { sendMessage: sendPostMessage } = useWebSocket('posts', { onMessage: handlePostsMessage });
  const { sendMessage: sendAlbumMessage } = useWebSocket('albums', { onMessage: handleAlbumsMessage });

  // Fetch Data on Mount
  useEffect(() => {
    if (authLoading) return;
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
        setSharedItems(response.data.shared_items || []);
        setError(null);
      } catch (err: any) {
        setError('Failed to fetch news feed data');
      } finally {
        setDataLoading(false);
      }
    };

    fetchData();
  }, [token, authLoading]);

  // CRUD handlers (unchanged)
  const handleDeletePost = async (id: string) => {
    if (!token) {
      setDeleteError('You must be logged in to delete a post.');
      return;
    }
    setDeletingPostIds((prev) => [...prev, id]);
    try {
      await axios.delete(`${API_URL}/social/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts((prev) => prev.filter((p) => p.id !== id));
      setDeleteSuccess('Post deleted successfully.');
      setToast({ show: true, message: 'Post deleted successfully!', variant: 'success' });
    } catch (err: any) {
      setDeleteError('Error deleting post.');
      setToast({ show: true, message: 'Error deleting post.', variant: 'danger' });
    } finally {
      setDeletingPostIds((prev) => prev.filter((p) => p !== id));
    }
  };

  const handleUpdatePost = async (updatedPost: PostType) => {
    if (!token) {
      setError('You must be logged in to update a post.');
      return;
    }
    setUpdatingPostIds((prev) => [...prev, updatedPost.id]);
    try {
      const response = await axios.put(`${API_URL}/social/${updatedPost.id}/`, updatedPost, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      setPosts((prev) =>
        prev.map((p) => (p.id === updatedPost.id ? response.data : p))
      );
      setToast({ show: true, message: 'Post updated successfully!', variant: 'success' });
    } catch (err: any) {
      setError('Error updating post.');
      setToast({ show: true, message: 'Error updating post.', variant: 'danger' });
    } finally {
      setUpdatingPostIds((prev) => prev.filter((p) => p !== updatedPost.id));
    }
  };

  const handleDeleteAlbum = async (id: string) => {
    if (!token) {
      setDeleteError('You must be logged in to delete an album.');
      return;
    }
    try {
      await axios.delete(`${API_URL}/albums/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAlbums((prev) => prev.filter((a) => a.id !== id));
      setDeleteSuccess('Album deleted successfully.');
      setToast({ show: true, message: 'Album deleted successfully!', variant: 'success' });
    } catch (err: any) {
      setDeleteError('Error deleting album.');
      setToast({ show: true, message: 'Error deleting album.', variant: 'danger' });
    }
  };

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
        updatedAlbum.photos.forEach((photo) => {
          formData.append('image_files', photo.image);
        });
      }

      const response = await axios.put(`${API_URL}/albums/${updatedAlbum.id}/`, formData, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setAlbums((prev) =>
        prev.map((a) => (a.id === updatedAlbum.id ? response.data : a))
      );
      setToast({ show: true, message: 'Album updated successfully!', variant: 'success' });
    } catch (err: any) {
      setError('Error updating album.');
      setToast({ show: true, message: 'Error updating album.', variant: 'danger' });
    }
  };

  const handleDeleteSharedItem = async (id: string) => {
    if (!token) {
      setDeleteError('You must be logged in to delete shared content.');
      return;
    }
    try {
      await axios.delete(`${API_URL}/shared/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSharedItems((prev) => prev.filter((s) => s.id !== id));
      setDeleteSuccess('Shared content deleted successfully.');
      setToast({ show: true, message: 'Shared content deleted successfully!', variant: 'success' });
    } catch (err: any) {
      setDeleteError('Error deleting shared content.');
      setToast({ show: true, message: 'Error deleting shared content.', variant: 'danger' });
    }
  };

  return (
    <div className="newsfeed-container d-flex">
      {/* Optionally display online status (for example, at the top of the NewsFeed or in a sidebar) */}
      <div className="online-status-bar">
        <strong>{onlineUsers.length}</strong> user(s) online
        {/* If you want to display details, you could map over onlineUsers and/or use userDetails */}
      </div>

      {/* Left Sidebar */}
      <div className="left-sidebar me-3">
        <Profile />
      </div>

      {/* Main Feed */}
      <div className="main-feed flex-grow-1">
        <CreatePosting
          onPostCreated={addNewPost}
          onAlbumCreated={addNewAlbum}
          sendMessage={sendPostMessage}
          sendAlbumMessage={sendAlbumMessage}
        />

        {dataLoading ? (
          <div className="text-center mt-5">Loading...</div>
        ) : (
          <>
            {error && <div className="alert alert-danger">{error}</div>}
            {deleteError && <div className="alert alert-danger">{deleteError}</div>}
            {deleteSuccess && <div className="alert alert-success">{deleteSuccess}</div>}

            <SharedItem sharedItems={sharedItems} onDeleteSharedItem={handleDeleteSharedItem} />

            <Posts
              posts={posts}
              onDeletePost={handleDeletePost}
              onUpdatePost={handleUpdatePost}
              deletingPostIds={deletingPostIds}
              updatingPostIds={updatingPostIds}
            />

            {albums.length > 0 ? (
              albums.map((album) => (
                <Album
                  key={album.id}
                  album={album}
                  onDelete={handleDeleteAlbum}
                  onUpdate={handleUpdateAlbum}
                />
              ))
            ) : (
              <div>No albums available</div>
            )}
          </>
        )}
      </div>

      {/* Right Sidebar */}
      <div className="right-sidebar ms-3">
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
