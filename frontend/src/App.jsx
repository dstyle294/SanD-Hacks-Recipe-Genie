import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { GoogleOAuthProvider } from '@react-oauth/google';
import { Upload, ChefHat, Sparkles, Youtube, Search, ArrowRight, Play, Check, X, Clock, Refrigerator, Archive, Snowflake } from 'lucide-react';
import * as api from './api';

// Components
import UploadZone from './components/UploadZone';
import IngredientsList from './components/IngredientsList';
import FilterDashboard from './components/FilterDashboard';
import RecipeSelector from './components/RecipeSelector';
import VideoResults from './components/VideoResults';
import UnifiedLoader from './components/UnifiedLoader';
import AuthCallback from './components/AuthCallback';
import UserMenu from './components/UserMenu';
import HistoryModal from './components/HistoryModal';

const AppContent = () => {
  const [step, setStep] = useState('upload'); // upload | dashboard | selection | results
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState("");
  const [ingredients, setIngredients] = useState([]);
  const [expiryInfo, setExpiryInfo] = useState({});
  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);
  const [videos, setVideos] = useState([]);
  const [user, setUser] = useState(null);
  const [historyModal, setHistoryModal] = useState({ isOpen: false, type: 'pantry' });

  const navigate = useNavigate();

  // Check for existing session
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const userData = await api.getMe();
          setUser(userData);
        } catch (err) {
          localStorage.removeItem('auth_token');
        }
      }
    };
    checkAuth();
  }, []);

  const handleAuthSuccess = (data) => {
    localStorage.setItem('auth_token', data.token);
    setUser(data.user);
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    navigate('/');
  };

  // 1. Analyze Pantry
  const handleFileSelect = async (file) => {
    setLoading(true);
    setLoadingMessage("Scanning your pantry...");
    try {
      const data = await api.analyzePantry(file);
      setIngredients(data.ingredients);
      setExpiryInfo(data.expiry_info || {});
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
    const prefs = `Time: ${filters.time}. Type: ${filters.mealType}. Cuisine: ${filters.cuisine}.`;
    try {
      const data = await api.suggestRecipes(ingredients, prefs);
      setRecipes(data.recipes);
      setStep('selection');
    } catch (err) {
      console.error(err);
      alert("Failed to brainstorm recipes.");
    } finally {
      setLoading(false);
    }
  };

  // 3. Find Videos
  const handleRecipeSelect = async (recipeObj) => {
    const name = typeof recipeObj === 'string' ? recipeObj : recipeObj.name;
    setSelectedRecipe(name);
    setLoading(true);
    setLoadingMessage(`Finding the perfect ${name} guide...`);

    try {
      const data = await api.findVideos(name, ingredients, {});
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
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans selection:bg-teal-500/30">
      <UnifiedLoader isVisible={loading} message={loadingMessage} />

      {/* Hero / Header */}
      <header className="relative z-30 px-6 py-8 flex flex-col items-center">
        <div className="w-full max-w-7xl flex justify-between items-center mb-12">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-gradient-to-br from-teal-400 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg shadow-teal-500/20">
              <ChefHat className="text-white w-7 h-7" />
            </div>
            <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">
              Recipe Genie
            </h1>
          </div>

          <UserMenu
            user={user}
            onAuthSuccess={handleAuthSuccess}
            onLogout={handleLogout}
            onViewPantry={() => {
              console.log("DEBUG: onViewPantry called");
              setHistoryModal({ isOpen: true, type: 'pantry' });
            }}
            onViewHistory={() => {
              console.log("DEBUG: onViewHistory called");
              setHistoryModal({ isOpen: true, type: 'recipes' });
            }}
          />
        </div>

        <AnimatePresence mode="wait">
          {step === 'upload' && (
            <motion.div
              key="hero"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center max-w-3xl"
            >
              <h2 className="text-5xl sm:text-7xl font-black mb-6 leading-tight">
                Your Pantry is the <span className="text-teal-400 italic">Ingredients.</span><br />
                We are the <span className="text-emerald-400 italic">Chef.</span>
              </h2>
              <p className="text-slate-400 text-lg mb-10 max-w-xl mx-auto">
                Snap a photo of your fridge, and our AI will instantly suggest recipes, expiry dates, and HD cooking guides.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </header >

      <HistoryModal
        isOpen={historyModal.isOpen}
        type={historyModal.type}
        user={user}
        onClose={() => setHistoryModal({ ...historyModal, isOpen: false })}
      />

      {/* Main Transitions */}
      <main className="relative z-10 px-6 pb-20">
        <Routes>
          <Route path="/auth/callback" element={<AuthCallback onLoginSuccess={(u) => setUser(u)} />} />
          <Route path="/" element={
            <AnimatePresence mode="wait">
              {step === 'upload' && (
                <motion.div key="upload" exit={{ opacity: 0, y: -20 }}>
                  <UploadZone onFileSelect={handleFileSelect} isAnalyzing={loading} />
                </motion.div>
              )}

              {step === 'dashboard' && (
                <motion.div key="dashboard" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                  <IngredientsList
                    ingredients={ingredients}
                    expiryInfo={expiryInfo}
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
                <motion.div key="selection" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }}>
                  <RecipeSelector
                    recipes={recipes}
                    onSelect={handleRecipeSelect}
                    onBack={() => setStep('dashboard')}
                  />
                </motion.div>
              )}

              {step === 'results' && (
                <motion.div key="results" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                  <VideoResults
                    videos={videos}
                    recipeName={selectedRecipe}
                    ingredients={ingredients}
                    user={user}
                    onBack={() => setStep('selection')}
                  />
                </motion.div>
              )}
            </AnimatePresence>
          } />
        </Routes>
      </main>

      {/* Background Polish */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-teal-500/10 blur-[120px] rounded-full" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full" />
      </div>
    </div >
  );
};

const App = () => (
  <GoogleOAuthProvider clientId={import.meta.env.VITE_GOOGLE_CLIENT_ID || "placeholder"}>
    <Router>
      <AppContent />
    </Router>
  </GoogleOAuthProvider>
);

export default App;
