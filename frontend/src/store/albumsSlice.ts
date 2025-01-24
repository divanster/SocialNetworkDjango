// src/store/albumsSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Album } from '../types/album';

interface AlbumsState {
  items: Album[];
  loading: boolean;
  error: string | null;
}

const initialState: AlbumsState = {
  items: [],
  loading: false,
  error: null,
};

const albumsSlice = createSlice({
  name: 'albums',
  initialState,
  reducers: {
    fetchAlbumsStart(state) {
      state.loading = true;
      state.error = null;
    },
    fetchAlbumsSuccess(state, action: PayloadAction<Album[]>) {
      state.items = action.payload;
      state.loading = false;
    },
    fetchAlbumsFailure(state, action: PayloadAction<string>) {
      state.loading = false;
      state.error = action.payload;
    },
    addAlbum(state, action: PayloadAction<Album>) {
      state.items.unshift(action.payload);
    },
    updateAlbum(state, action: PayloadAction<Album>) {
      const index = state.items.findIndex((a) => a.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    deleteAlbum(state, action: PayloadAction<string>) { // Changed from number to string
      state.items = state.items.filter((a) => a.id !== action.payload);
    },
    // ... other reducers ...
  },
});

export const {
  fetchAlbumsStart,
  fetchAlbumsSuccess,
  fetchAlbumsFailure,
  addAlbum,
  updateAlbum,
  deleteAlbum,
} = albumsSlice.actions;

export default albumsSlice.reducer;
