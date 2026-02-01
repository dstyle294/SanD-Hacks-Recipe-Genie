import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
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

export default api;
