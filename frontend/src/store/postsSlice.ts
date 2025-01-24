// frontend/src/store/postsSlice.ts

import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { Post } from '../types/post'; // Ensure this path is correct

interface PostsState {
  items: Post[];
  loading: boolean;
  error: string | null;
}

const initialState: PostsState = {
  items: [],
  loading: false,
  error: null,
};

const postsSlice = createSlice({
  name: 'posts',
  initialState,
  reducers: {
    fetchPostsStart(state: PostsState) {
      state.loading = true;
      state.error = null;
    },
    fetchPostsSuccess(state: PostsState, action: PayloadAction<Post[]>) {
      state.items = action.payload;
      state.loading = false;
    },
    fetchPostsFailure(state: PostsState, action: PayloadAction<string>) {
      state.loading = false;
      state.error = action.payload;
    },
    addPost(state: PostsState, action: PayloadAction<Post>) {
      state.items.unshift(action.payload);
    },
    updatePost(state: PostsState, action: PayloadAction<Post>) {
      const index = state.items.findIndex((p) => p.id === action.payload.id);
      if (index !== -1) {
        state.items[index] = action.payload;
      }
    },
    deletePost(state: PostsState, action: PayloadAction<string>) {
  state.items = state.items.filter((p) => p.id !== action.payload);
},
    // ... other reducers ...
  },
});

export const {
  fetchPostsStart,
  fetchPostsSuccess,
  fetchPostsFailure,
  addPost,
  updatePost,
  deletePost,
} = postsSlice.actions;

export default postsSlice.reducer;
