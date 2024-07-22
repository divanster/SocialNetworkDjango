// src/services/api.ts

import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api', // Replace with your API base URL
});

export const fetchRecipes = () => api.get('/recipes');

export default api;
