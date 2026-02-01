import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add a request interceptor to include the token in headers
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const analyzePantry = async (imageFile) => {
  const formData = new FormData();
  formData.append('file', imageFile);
  const response = await api.post('/analyze-pantry', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const suggestRecipes = async (ingredients, preferences) => {
  const response = await api.post('/suggest-recipes', {
    ingredients,
    preferences,
  });
  return response.data;
};

export const findVideos = async (selectedRecipe, ingredients, filters) => {
  const response = await api.post('/find-videos', {
    selected_recipe: selectedRecipe,
    ingredients,
    filters,
  });
  return response.data;
};

export const authGoogle = async (idToken) => {
  const response = await api.post('/auth/google', { token: idToken });
  return response.data;
};

export const getMe = async () => {
  const response = await api.get('/auth/me');
  return response.data;
};

export const getPantry = async () => {
  const response = await api.get('/pantry');
  return response.data;
};

export const saveRecipe = async (recipeData) => {
  const response = await api.post('/recipes/save', recipeData);
  return response.data;
};

export const getRecipeHistory = async () => {
  const response = await api.get('/recipes/history');
  return response.data;
};

export default api;
