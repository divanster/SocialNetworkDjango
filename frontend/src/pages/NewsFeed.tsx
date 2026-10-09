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
import Suggestions from '../components/RightSidebar/Suggestions';
import CreatePosting from '../components/CentralNewsFeed/CreatePosting';
import './NewsFeed.css';
import { BsChatSquareHeart } from 'react-icons/bs';

import { Post as PostType } from '../types/post';
import { Album as AlbumType } from '../types/album';
import { SharedItem as SharedItemType } from '../types/sharedItem';
import { useAuth } from '../contexts/AuthContext';
import { useOnlineStatus } from '../contexts/OnlineStatusContext';
import { Toast, ToastContainer } from 'react-bootstrap';
import { deleteAlbum as deleteAlbumRequest, listStories, updateAlbum as updateAlbumRequest } from '../services/contentService';

interface StoryType {
  id: string;
  user?: { id: string; full_name: string; profile_picture: string } | string;
  user_name?: string;
  content: string;
  media_url?: string | null;
  media_type?: 'text' | 'image' | 'video';
  created_at: string;
  updated_at: string;
}

const NewsFeed: React.FC = () => {
  const { token, loading: authLoading } = useAuth();
  const { onlineUsers } = useOnlineStatus();

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

  useEffect(() => {
    if (authLoading) return;
    if (!token) {
      setError('User not authenticated.');
      setLoading(false);
      return;
    }
    (async () => {
      try {
        const [feedRes, storiesData] = await Promise.all([axios.get('/newsfeed/feed/'), listStories()]);
        setPosts(feedRes.data.posts || []);
        setAlbums(feedRes.data.albums || []);
        setSharedItems(feedRes.data.shared_items || []);
        setStories(storiesData || []);
        setError(null);
      } catch {
        setError('Failed to fetch newsfeed or stories.');
      } finally {
        setLoading(false);
      }
    })();
  }, [token, authLoading]);

  const onPostEvent = useCallback((data: any) => {
    if (data.type === 'post') addNewPost(data.message);
    else if (data.type === 'shared_item') addNewSharedItem(data.message);
  }, []);
  const onAlbumEvent = useCallback((data: any) => {
    if (data.type === 'album') addNewAlbum(data.message);
  }, []);
  const { sendMessage: sendPostMessage } = useWebSocket('posts', { onMessage: onPostEvent });
  const { sendMessage: sendAlbumMessage } = useWebSocket('albums', { onMessage: onAlbumEvent });

  const hasFeedContent = posts.length > 0 || albums.length > 0 || sharedItems.length > 0;

  const handleDeletePost = async (id: string) => {
    if (!token) {
      setDeleteError('Login required.');
      return;
    }
    setDeletingPostIds((ids) => [...ids, id]);
    try {
      await axios.delete(`/social/${id}/`);
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
      const res = await axios.put(`/social/${up.id}/`, up);
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
      await deleteAlbumRequest(id);
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
      const updated = await updateAlbumRequest(ua.id, fd);
      setAlbums((a) => a.map((x) => (x.id === ua.id ? updated : x)));
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
      await axios.delete(`/shared/${id}/`);
      setSharedItems((s) => s.filter((x) => x.id !== id));
      setToast({ show: true, message: 'Shared item deleted!', variant: 'success' });
    } catch {
      setDeleteError('Error deleting shared item.');
    }
  };

  return (
    <div className="newsfeed-page">
      <div className="newsfeed-container">
        <aside className="left-sidebar">
          <Profile />
        </aside>

        <main className="main-feed" aria-label="Main feed">
          <div className="feed-header">
            <h4>Home</h4>
            <span className="online-badge" aria-label={`${onlineUsers.length} users online`}>
              {onlineUsers.length} online
            </span>
          </div>

          <CreatePosting
            onPostCreated={addNewPost}
            onAlbumCreated={addNewAlbum}
            onStoryCreated={(story) => setStories((prev) => [story as StoryType, ...prev])}
            sendMessage={sendPostMessage}
            sendAlbumMessage={sendAlbumMessage}
          />

          <section id="stories">
            <StoryCarousel
              stories={stories}
              onStoryDeleted={(storyId) =>
                setStories((prev) => prev.filter((story) => String(story.id) !== String(storyId)))
              }
            />
          </section>

          {loading ? (
            <div className="text-center my-5">Loading...</div>
          ) : (
            <>
              {error && <div className="alert alert-danger">{error}</div>}
              {deleteError && <div className="alert alert-danger">{deleteError}</div>}
              {deleteSuccess && <div className="alert alert-success">{deleteSuccess}</div>}

              {!hasFeedContent ? (
                <div className="feed-empty-state">
                  <BsChatSquareHeart className="feed-empty-icon" aria-hidden="true" />
                  <h5>Your feed is quiet right now</h5>
                  <p>Create your first post to start sharing with friends.</p>
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                  >
                    Create your first post
                  </button>
                </div>
              ) : (
                <>
                  <SharedItem sharedItems={sharedItems} onDeleteSharedItem={handleDeleteSharedItem} />

                  <Posts
                    posts={posts}
                    onDeletePost={handleDeletePost}
                    onUpdatePost={handleUpdatePost}
                    deletingPostIds={deletingPostIds}
                    updatingPostIds={updatingPostIds}
                  />

                  <section id="albums">
                    {albums.map((alb) => (
                      <div key={alb.id} className="post-card">
                        <Album album={alb} onDelete={handleDeleteAlbum} onUpdate={handleUpdateAlbum} />
                      </div>
                    ))}
                  </section>
                </>
              )}
            </>
          )}
        </main>

        <aside className="right-sidebar">
          <Suggestions />
          <FriendRequests />
          <Birthdays />
          <Contacts />
        </aside>
      </div>

      <ToastContainer position="bottom-end" className="p-3">
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
