import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Clock, Utensils, Globe, Tv, Sparkles } from 'lucide-react';
import clsx from 'clsx';

const FilterDashboard = ({ onBrainstorm, isLoading }) => {
  const [filters, setFilters] = useState({
    time: '30m',
    mealType: 'Savory',
    cuisine: '',
    youtuber: '',
  });

  const handleBrainstorm = () => {
    onBrainstorm(filters);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto my-12 p-10 bg-slate-900/60 backdrop-blur-2xl rounded-[2.5rem] border border-slate-700/50 shadow-2xl relative overflow-hidden"
    >
      {/* Decorative gradient blob */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2 pointer-events-none" />

      <div className="flex items-center space-x-4 mb-10 relative z-10">
        <div className="p-3 bg-slate-800 rounded-2xl shadow-lg border border-slate-700">
          <Sparkles className="w-8 h-8 text-purple-400" />
        </div>
        <div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-400 to-red-400 bg-clip-text text-transparent">
            Chef's Controls
          </h2>
          <p className="text-slate-400 text-sm">Fine-tune your culinary experience</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10 relative z-10">

        {/* Time */}
        <div className="space-y-4">
          <label className="flex items-center text-sm font-bold text-slate-300 uppercase tracking-wider">
            <Clock className="w-4 h-4 mr-2 text-teal-400" /> Time to Cook
          </label>
          <div className="flex bg-slate-950/50 p-2 rounded-2xl border border-slate-800 backdrop-blur-sm">
            {['15m', '30m', '1hr', '1hr+'].map((t) => (
              <button
                key={t}
                onClick={() => setFilters({ ...filters, time: t })}
                className={clsx(
                  "flex-1 py-3 rounded-xl text-sm font-bold transition-all duration-300",
                  filters.time === t
                    ? "bg-gradient-to-br from-teal-500 to-blue-600 text-white shadow-lg shadow-teal-900/50 scale-105"
                    : "text-slate-500 hover:text-slate-200 hover:bg-slate-800"
                )}
              >
                {t}
              </button>
            ))}
          </div>
        </div>

        {/* Meal Type */}
        <div className="space-y-4">
          <label className="flex items-center text-sm font-bold text-slate-300 uppercase tracking-wider">
            <Utensils className="w-4 h-4 mr-2 text-pink-400" /> Meal Type
          </label>
          <div className="flex flex-wrap gap-3">
            {['Savory', 'Sweet', 'Spicy', 'Healthy', 'Comfort'].map((type) => (
              <button
                key={type}
                onClick={() => setFilters({ ...filters, mealType: type })}
                className={clsx(
                  "px-5 py-2.5 rounded-full border text-sm font-semibold transition-all duration-300 shadow-sm hover:scale-105 active:scale-95",
                  filters.mealType === type
                    ? "border-transparent bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-purple-900/50"
                    : "border-slate-700 bg-slate-800/50 text-slate-400 hover:border-slate-500 hover:bg-slate-800 hover:text-white"
                )}
              >
                {type}
              </button>
            ))}
          </div>
        </div>

        {/* Cuisine */}
        <div className="space-y-4">
          <label className="flex items-center text-sm font-bold text-slate-300 uppercase tracking-wider">
            <Globe className="w-4 h-4 mr-2 text-blue-400" /> Cuisine (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. Indian, Italian, Mexican"
            value={filters.cuisine}
            onChange={(e) => setFilters({ ...filters, cuisine: e.target.value })}
            className="w-full px-5 py-4 bg-slate-950/50 border border-slate-700 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all font-medium"
          />
        </div>

        {/* YouTuber */}
        <div className="space-y-4">
          <label className="flex items-center text-sm font-bold text-slate-300 uppercase tracking-wider">
            <Tv className="w-4 h-4 mr-2 text-red-400" /> Prefer Channel (Optional)
          </label>
          <input
            type="text"
            placeholder="e.g. Ranveer Brar, Babish"
            value={filters.youtuber}
            onChange={(e) => setFilters({ ...filters, youtuber: e.target.value })}
            className="w-full px-5 py-4 bg-slate-950/50 border border-slate-700 rounded-2xl text-white placeholder-slate-600 focus:outline-none focus:border-pink-500 focus:ring-1 focus:ring-pink-500 transition-all font-medium"
          />
        </div>

      </div>

      <motion.button
        whileHover={{ scale: 1.02, boxShadow: "0 20px 40px -10px rgba(168, 85, 247, 0.4)" }}
        whileTap={{ scale: 0.98 }}
        onClick={handleBrainstorm}
        disabled={isLoading}
        className="w-full mt-12 py-5 bg-gradient-to-r from-purple-600 via-pink-600 to-red-500 rounded-2xl font-bold text-xl text-white shadow-2xl shadow-purple-900/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed overflow-hidden relative group"
      >
        <span className="relative z-10 flex items-center justify-center">
          <Sparkles className="w-5 h-5 mr-3 animate-pulse" /> Brainstorm Recipes
        </span>
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500 via-pink-500 to-red-400 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
      </motion.button>

    </motion.div>
  );
};

export default FilterDashboard;
