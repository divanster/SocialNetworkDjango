// frontend/src/store/index.ts

import { configureStore } from '@reduxjs/toolkit';
import postsReducer from './postsSlice'; // Correct path
import albumsReducer from './albumsSlice'; // Assuming you have an albumsSlice.ts
// ... import other reducers as necessary

const store = configureStore({
  reducer: {
    posts: postsReducer,
    albums: albumsReducer,
    // ... add other reducers here
  },
  devTools: process.env.NODE_ENV !== 'production', // Enable Redux DevTools in development
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
