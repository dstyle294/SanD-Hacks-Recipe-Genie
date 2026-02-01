import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import UploadZone from './components/UploadZone.jsx';
import IngredientsList from './components/IngredientsList.jsx';
import FilterDashboard from './components/FilterDashboard.jsx';
import RecipeSelector from './components/RecipeSelector.jsx';
import VideoResults from './components/VideoResults.jsx';
import LoadingScreen from './components/LoadingScreen.jsx';
import * as api from './api';

const App = () => {
  const [step, setStep] = useState('upload'); // upload | dashboard | selection | results
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [videos, setVideos] = useState([]);
  const [currentFilters, setCurrentFilters] = useState({});

  // 1. Analyze Pantry
  const handleFileSelect = async (file) => {
    setLoading(true);
    setLoadingMessage("Scanning your pantry...");
    try {
      const data = await api.analyzePantry(file);
      setIngredients(data.ingredients);
      setStep('dashboard');
    } catch (err) {
      console.error(err);
      alert("Failed to analyze image.");
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveIngredient = (ing) => {
    setIngredients(ingredients.filter(i => i !== ing));
  };

  // 2. Brainstorm Recipes
  const handleBrainstorm = async (filters) => {
    setLoading(true);
    setLoadingMessage("Dreaming up delicious ideas...");
    setCurrentFilters(filters);

    // Construct preference string as backend expects
    const prefs = `Time: ${filters.time}. Type: ${filters.mealType}. Cuisine: ${filters.cuisine}.`;

    try {
      const data = await api.suggestRecipes(ingredients, prefs);
      setRecipes(data.recipes);
      setStep('selection');
    } catch (err) {
      console.error(err);
      alert("Failed to suggest recipes.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Find Videos
  const handleSelectRecipe = async (recipe) => {
    setSelectedRecipe(recipe);
    setLoading(true);
    setLoadingMessage("Finding top-rated tutorials...");

    // Note: We switch step to 'results' only after success or handled error to keep context?
    // Actually, if we use a global loader, we can keep the current step or pre-switch.
    // Let's pre-switch to results so when loader finishes we are there.

    try {
      const filterObj = {
        channel: currentFilters.youtuber,
        cuisine: currentFilters.cuisine
      };

      const data = await api.findVideos(recipe, ingredients, filterObj);
      console.log('📺 Received videos from API:', data);
      console.log('📺 Number of videos:', data.videos?.length);
      setVideos(data.videos);
      setStep('results');
    } catch (err) {
      console.error(err);
      alert("Failed to find videos.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 overflow-x-hidden relative">
      <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 pointer-events-none" />

      <main className="relative z-10 container mx-auto pb-20">

        <AnimatePresence mode='wait'>
          {loading ? (
            <motion.div key="loader" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center">
              <LoadingScreen message={loadingMessage} />
            </motion.div>
          ) : (
            <>
              {step === 'upload' && (
                <motion.div key="upload" exit={{ opacity: 0, y: -20 }}>
                  <UploadZone onFileSelect={handleFileSelect} isAnalyzing={loading} />
                </motion.div>
              )}

              {step === 'dashboard' && (
                <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <IngredientsList
                    ingredients={ingredients}
                    onRemove={handleRemoveIngredient}
                    onConfirm={() => { }}
                  />
                  <FilterDashboard
                    onBrainstorm={handleBrainstorm}
                    isLoading={loading}
                  />
                </motion.div>
              )}

              {step === 'selection' && (
                <motion.div key="selection" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <div className="pt-8">
                    <button onClick={() => setStep('dashboard')} className="mb-4 mx-4 text-slate-400 hover:text-white transition-colors">← Back to Filters</button>
                    <RecipeSelector recipes={recipes} onSelect={handleSelectRecipe} />
                  </div>
                </motion.div>
              )}

              {step === 'results' && (
                <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  <div className="pt-8 px-4">
                    <button onClick={() => setStep('selection')} className="mb-4 text-slate-400 hover:text-white transition-colors">← Back to Recipes</button>
                    <h1 className="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">{selectedRecipe}</h1>
                    <VideoResults videos={videos} isLoading={false} />
                  </div>
                </motion.div>
              )}
            </>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
