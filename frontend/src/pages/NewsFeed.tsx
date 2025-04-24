// frontend/src/pages/NewsFeed.tsx
import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import useWebSocket from '../hooks/useWebSocket';
import Posts from '../components/CentralNewsFeed/Posts';
import Album from '../components/FeedItem/Album';
import SharedItem from '../components/FeedItem/SharedItem';
import StoryCarousel from '../components/FeedItem/StoryCarousel';
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
import { useOnlineStatus } from '../contexts/OnlineStatusContext';
import { Toast, ToastContainer } from 'react-bootstrap';

interface StoryType {
  id: string;
  user: { id: string; full_name: string; profile_picture: string };
  content: string;
  created_at: string;
  updated_at: string;
}

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const NewsFeed: React.FC = () => {
  const { token, user, loading: authLoading } = useAuth();
  const { onlineUsers, userDetails } = useOnlineStatus();

  const [posts, setPosts] = useState<PostType[]>([]);
  const [albums, setAlbums] = useState<AlbumType[]>([]);
  const [sharedItems, setSharedItems] = useState<SharedItemType[]>([]);
  const [stories, setStories] = useState<StoryType[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
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

  // Helpers for adding new items
  const addNewPost = (np: PostType) => {
    setPosts((p) => [np, ...p]);
    setToast({ show: true, message: 'Post created successfully!', variant: 'success' });
  };
  const addNewAlbum = (na: AlbumType) => {
    setAlbums((a) => [na, ...a]);
    setToast({ show: true, message: 'Album created successfully!', variant: 'success' });
  };
  const addNewSharedItem = (ns: SharedItemType) => {
    setSharedItems((s) => [ns, ...s]);
    setToast({ show: true, message: 'Content shared successfully!', variant: 'success' });
  };

  // Fetch feed + stories
  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      setError('User not authenticated.');
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const [feedRes, storiesRes] = await Promise.all([
          axios.get(`${API_URL}/newsfeed/feed/`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
          axios.get(`${API_URL}/stories/`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
        setPosts(feedRes.data.posts || []);
        setAlbums(feedRes.data.albums || []);
        setSharedItems(feedRes.data.shared_items || []);
        setStories(storiesRes.data || []);
        setError(null);
      } catch (e) {
        setError('Failed to fetch newsfeed or stories.');
      } finally {
        setLoading(false);
      }
    })();
  }, [token, authLoading]);

  // WebSocket handlers
  const onPostEvent = useCallback((data: any) => {
    if (data.type === 'post') addNewPost(data.message);
    else if (data.type === 'shared_item') addNewSharedItem(data.message);
  }, []);
  const onAlbumEvent = useCallback((data: any) => {
    if (data.type === 'album') addNewAlbum(data.message);
  }, []);
  const { sendMessage: sendPostMessage } = useWebSocket('posts', { onMessage: onPostEvent });
  const { sendMessage: sendAlbumMessage } = useWebSocket('albums', { onMessage: onAlbumEvent });

  // CRUD handlers
  const handleDeletePost = async (id: string) => {
    if (!token) {
      setDeleteError('Login required.');
      return;
    }
    setDeletingPostIds((ids) => [...ids, id]);
    try {
      await axios.delete(`${API_URL}/social/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setPosts((p) => p.filter((x) => x.id !== id));
      setDeleteSuccess('Post deleted.');
    } catch {
      setDeleteError('Error deleting.');
    } finally {
      setDeletingPostIds((ids) => ids.filter((x) => x !== id));
      setToast({ show: true, message: deleteSuccess || 'Deleted!', variant: 'success' });
    }
  };
  const handleUpdatePost = async (up: PostType) => {
    if (!token) {
      setError('Login required.');
      return;
    }
    setUpdatingPostIds((ids) => [...ids, up.id]);
    try {
      const res = await axios.put(`${API_URL}/social/${up.id}/`, up, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      setPosts((p) => p.map((x) => (x.id === up.id ? res.data : x)));
      setToast({ show: true, message: 'Post updated!', variant: 'success' });
    } catch {
      setError('Error updating.');
    } finally {
      setUpdatingPostIds((ids) => ids.filter((x) => x !== up.id));
    }
  };
  const handleDeleteAlbum = async (id: string) => {
    if (!token) {
      setDeleteError('Login required.');
      return;
    }
    try {
      await axios.delete(`${API_URL}/albums/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setAlbums((a) => a.filter((x) => x.id !== id));
      setToast({ show: true, message: 'Album deleted!', variant: 'success' });
    } catch {
      setDeleteError('Error deleting album.');
    }
  };
  const handleUpdateAlbum = async (ua: AlbumType) => {
    if (!token) {
      setError('Login required.');
      return;
    }
    try {
      const fd = new FormData();
      fd.append('title', ua.title);
      fd.append('description', ua.description);
      fd.append('visibility', ua.visibility);
      ua.photos?.forEach((ph) => fd.append('image_files', ph.image));
      const res = await axios.put(`${API_URL}/albums/${ua.id}/`, fd, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      setAlbums((a) => a.map((x) => (x.id === ua.id ? res.data : x)));
      setToast({ show: true, message: 'Album updated!', variant: 'success' });
    } catch {
      setError('Error updating album.');
    }
  };
  const handleDeleteSharedItem = async (id: string) => {
    if (!token) {
      setDeleteError('Login required.');
      return;
    }
    try {
      await axios.delete(`${API_URL}/shared/${id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setSharedItems((s) => s.filter((x) => x.id !== id));
      setToast({ show: true, message: 'Shared item deleted!', variant: 'success' });
    } catch {
      setDeleteError('Error deleting shared item.');
    }
  };

  return (
    <div className="newsfeed-container">
      {/* Left Sidebar */}
      <aside className="left-sidebar">
        <Profile />
      </aside>

      {/* Main Feed */}
      <main className="main-feed">
        {/* Header + online count badge */}
        <div className="feed-header">
          <h4>Home</h4>
          <span className="online-badge">{onlineUsers.length} online</span>
        </div>

        {/* Composer */}
        <CreatePosting
          onPostCreated={addNewPost}
          onAlbumCreated={addNewAlbum}
          sendMessage={sendPostMessage}
          sendAlbumMessage={sendAlbumMessage}
        />

        {/* Stories */}
        <StoryCarousel stories={stories} />

        {/* Loading / Errors */}
        {loading ? (
          <div className="text-center my-5">Loading...</div>
        ) : (
          <>
            {error && <div className="alert alert-danger">{error}</div>}
            {deleteError && <div className="alert alert-danger">{deleteError}</div>}
            {deleteSuccess && <div className="alert alert-success">{deleteSuccess}</div>}

            {/* Shared items */}
            <SharedItem
              sharedItems={sharedItems}
              onDeleteSharedItem={handleDeleteSharedItem}
            />

            {/* Posts */}
            <Posts
              posts={posts}
              onDeletePost={handleDeletePost}
              onUpdatePost={handleUpdatePost}
              deletingPostIds={deletingPostIds}
              updatingPostIds={updatingPostIds}
            />

            {/* Albums */}
            {albums.length > 0 ? (
              albums.map((alb) => (
                <div key={alb.id} className="post-card">
                  <Album
                    album={alb}
                    onDelete={handleDeleteAlbum}
                    onUpdate={handleUpdateAlbum}
                  />
                </div>
              ))
            ) : (
              <div>No albums available</div>
            )}
          </>
        )}
      </main>

      {/* Right Sidebar */}
      <aside className="right-sidebar">
        <FriendRequests />
        <Birthdays />
        <Contacts />
      </aside>

      {/* Toast */}
      <ToastContainer position="bottom-end">
        <Toast
          show={toast.show}
          onClose={() => setToast((t) => ({ ...t, show: false }))}
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
