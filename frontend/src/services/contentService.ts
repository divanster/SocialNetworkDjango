import axios from 'axios';
import { handleApiError } from './api';
import { Album, Photo } from '../types/album';

export interface StoryTag {
  tagged_user_id: string;
  tagged_user_username: string | null;
}

export interface StoryItem {
  id: string;
  user: string;
  user_name: string;
  content: string;
  media_type: 'text' | 'image' | 'video';
  media_url: string | null;
  visibility: string;
  created_at: string;
  updated_at: string;
  tags: StoryTag[];
}

const asArray = <T>(payload: any): T[] => {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
};

export const listAlbums = async (): Promise<Album[]> => {
  try {
    const response = await axios.get('/albums/');
    return asArray<Album>(response.data);
  } catch (error) {
    handleApiError(error, 'Error listing albums');
    throw error;
  }
};

export const getAlbumById = async (albumId: string): Promise<Album> => {
  try {
    const response = await axios.get(`/albums/${albumId}/`);
    return response.data;
  } catch (error) {
    handleApiError(error, `Error getting album: ${albumId}`);
    throw error;
  }
};

export const createAlbum = async (payload: FormData): Promise<Album> => {
  try {
    const response = await axios.post('/albums/', payload);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error creating album');
    throw error;
  }
};

export const updateAlbum = async (albumId: string, payload: FormData): Promise<Album> => {
  try {
    const response = await axios.patch(`/albums/${albumId}/`, payload);
    return response.data;
  } catch (error) {
    handleApiError(error, `Error updating album: ${albumId}`);
    throw error;
  }
};

export const deleteAlbum = async (albumId: string): Promise<void> => {
  try {
    await axios.delete(`/albums/${albumId}/`);
  } catch (error) {
    handleApiError(error, `Error deleting album: ${albumId}`);
    throw error;
  }
};

export const listPhotos = async (albumId?: string): Promise<Photo[]> => {
  try {
    const response = await axios.get('/albums/photos/', {
      params: albumId ? { album: albumId } : undefined,
    });
    return asArray<Photo>(response.data);
  } catch (error) {
    handleApiError(error, 'Error listing photos');
    throw error;
  }
};

export const uploadPhoto = async (payload: FormData): Promise<Photo> => {
  try {
    const response = await axios.post('/albums/photos/', payload);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error uploading photo');
    throw error;
  }
};

export const updatePhoto = async (photoId: string, payload: FormData): Promise<Photo> => {
  try {
    const response = await axios.patch(`/albums/photos/${photoId}/`, payload);
    return response.data;
  } catch (error) {
    handleApiError(error, `Error updating photo: ${photoId}`);
    throw error;
  }
};

export const deletePhoto = async (photoId: string): Promise<void> => {
  try {
    await axios.delete(`/albums/photos/${photoId}/`);
  } catch (error) {
    handleApiError(error, `Error deleting photo: ${photoId}`);
    throw error;
  }
};

export const listStories = async (): Promise<StoryItem[]> => {
  try {
    const response = await axios.get('/stories/');
    return asArray<StoryItem>(response.data);
  } catch (error) {
    handleApiError(error, 'Error listing stories');
    throw error;
  }
};

export const createStory = async (payload: FormData): Promise<StoryItem> => {
  try {
    const response = await axios.post('/stories/', payload);
    return response.data;
  } catch (error) {
    handleApiError(error, 'Error creating story');
    throw error;
  }
};

export const deleteStory = async (storyId: string): Promise<void> => {
  try {
    await axios.delete(`/stories/${storyId}/`);
  } catch (error) {
    handleApiError(error, `Error deleting story: ${storyId}`);
    throw error;
  }
};

export const deleteTag = async (tagId: string): Promise<void> => {
  try {
    await axios.delete(`/tagging/${tagId}/`);
  } catch (error) {
    handleApiError(error, `Error deleting tag: ${tagId}`);
    throw error;
  }
};
