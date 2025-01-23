// frontend/src/store/albumsSlice.ts

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
    fetchAlbumsStart(state: AlbumsState) { // Explicit type
      state.loading = true;
      state.error = null;
    },
    fetchAlbumsSuccess(state: AlbumsState, action: PayloadAction<Album[]>) { // Explicit types
      state.items = action.payload;
      state.loading = false;
    },
    fetchAlbumsFailure(state: AlbumsState, action: PayloadAction<string>) { // Explicit types
      state.loading = false;
      state.error = action.payload;
    },
    addAlbum(state: AlbumsState, action: PayloadAction<Album>) { // Explicit types
      state.items.unshift(action.payload);
    },
    updateAlbum(state: AlbumsState, action: PayloadAction<Album>) { // Explicit types
      const index = state.items.findIndex((a) => a.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    deleteAlbum(state: AlbumsState, action: PayloadAction<number>) { // Explicit types
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
