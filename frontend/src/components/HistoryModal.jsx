import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Calendar, Package, MapPin, AlertCircle, History, Youtube, ChevronRight } from 'lucide-react';
import * as api from '../api';

const HistoryModal = ({ isOpen, onClose, type, user }) => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("DEBUG: HistoryModal useEffect", { isOpen, type, userId: user?.id });
    if (isOpen && user) {
      const fetchData = async () => {
        setLoading(true);
        setItems([]); // Clear previous items to avoid type mismatch crashes
        try {
          if (type === 'pantry') {
            console.log("DEBUG: Fetching pantry history...");
            const data = await api.getPantry();
            console.log("DEBUG: Pantry data received:", data);
            setItems(Array.isArray(data) ? data : []);
          } else {
            console.log("DEBUG: Fetching recipe history...");
            const data = await api.getRecipeHistory();
            console.log("DEBUG: Recipe data received:", data);
            setItems(Array.isArray(data) ? data : []);
          }
        } catch (err) {
          console.error("DEBUG: Failed to fetch history:", err);
        } finally {
          setLoading(false);
        }
      };
      fetchData();
    }
  }, [isOpen, type, user]);

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
          />

          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl flex flex-col max-h-[85vh] overflow-hidden"
          >
            {/* Header */}
            <div className="p-6 border-b border-slate-800 flex justify-between items-center bg-slate-900/50">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-teal-500/10 rounded-lg">
                  {type === 'pantry' ? <Package className="w-5 h-5 text-teal-400" /> : <History className="w-5 h-5 text-teal-400" />}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">
                    {type === 'pantry' ? 'My Pantry History' : 'Saved Recipes'}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium">
                    {type === 'pantry' ? 'Past ingredients scanned & estimated' : 'Your collection of cooking guides'}
                  </p>
                </div>
              </div>
              <button
                onClick={onClose}
                className="p-2 hover:bg-slate-800 rounded-full transition-colors group"
              >
                <X className="w-5 h-5 text-slate-400 group-hover:text-white" />
              </button>
            </div>

            {/* Content Area - Definitive scrolling container */}
            <div className="flex-1 overflow-y-auto min-h-0 px-6 py-4 custom-scrollbar">
              {loading ? (
                <div className="py-20 flex flex-col items-center justify-center gap-4">
                  <div className="w-8 h-8 border-2 border-teal-500 border-t-transparent rounded-full animate-spin" />
                  <p className="text-slate-500 font-medium">Loading your history...</p>
                </div>
              ) : items.length === 0 ? (
                <div className="py-20 text-center">
                  <div className="w-16 h-16 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-4">
                    <AlertCircle className="w-8 h-8 text-slate-600" />
                  </div>
                  <h4 className="text-white font-bold mb-1">No items found</h4>
                  <p className="text-slate-500 text-sm">Start scanning your pantry to see history here!</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {type === 'pantry' ? (
                    items.map((item) => (
                      <div key={item.id} className="p-4 bg-slate-800/30 border border-slate-800 rounded-2xl flex items-center justify-between group hover:border-teal-500/30 transition-all">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-xl flex items-center justify-center text-sm font-bold ${item.urgency === 'high' ? 'bg-red-500/10 text-red-400' :
                            item.urgency === 'medium' ? 'bg-amber-500/10 text-amber-400' :
                              'bg-emerald-500/10 text-emerald-400'
                            }`}>
                            {item.ingredient_name[0].toUpperCase()}
                          </div>
                          <div>
                            <h4 className="text-slate-200 font-bold">{item.ingredient_name}</h4>
                            <div className="flex items-center gap-3 mt-1 text-xs text-slate-500">
                              <span className="flex items-center gap-1">
                                <Calendar className="w-3 h-3" />
                                {new Date(item.scan_date).toLocaleDateString()}
                              </span>
                              <span className="flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                {item.storage}
                              </span>
                            </div>
                          </div>
                        </div>
                        <div className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-wider ${item.urgency === 'high' ? 'bg-red-500/10 text-red-500' :
                          item.urgency === 'medium' ? 'bg-amber-500/10 text-amber-500' :
                            'bg-emerald-500/10 text-emerald-500'
                          }`}>
                          {item.days_until_expiry}d left
                        </div>
                      </div>
                    ))
                  ) : (
                    items.map((recipe) => (
                      <div key={recipe.id} className="p-4 bg-slate-800/30 border border-slate-800 rounded-2xl flex items-center gap-4 group hover:border-teal-500/30 transition-all">
                        <img
                          src={recipe.thumbnail}
                          alt={recipe.recipe_name}
                          className="w-20 h-20 object-cover rounded-xl border border-slate-700"
                        />
                        <div className="flex-1 min-w-0">
                          <h4 className="text-slate-200 font-bold truncate">{recipe.recipe_name}</h4>
                          <p className="text-xs text-slate-500 mt-1 line-clamp-1">
                            {Array.isArray(recipe.ingredients) ? recipe.ingredients.join(', ') : 'No ingredients listed'}
                          </p>
                          <a
                            href={recipe.video_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1.5 mt-2 text-xs font-bold text-teal-400 hover:text-teal-300 transition-colors"
                          >
                            <Youtube className="w-3.5 h-3.5" />
                            Watch Guide
                          </a>
                        </div>
                        <ChevronRight className="w-5 h-5 text-slate-700 group-hover:text-teal-500 transition-colors" />
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
};

export default HistoryModal;
