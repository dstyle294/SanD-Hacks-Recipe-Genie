import React from 'react';
import { motion } from 'framer-motion';
import { X, Check, Clock, Refrigerator, Archive, Snowflake } from 'lucide-react';

const IngredientsList = ({ ingredients, expiryInfo, onRemove, onConfirm }) => {
  if (!ingredients.length) return null;

  const getUrgencyColor = (urgency) => {
    switch (urgency) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/50';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/50';
      default: return 'bg-slate-500/20 text-slate-400 border-slate-500/50';
    }
  };

  const getStorageIcon = (storage) => {
    switch (storage) {
      case 'refrigerate': return <Refrigerator className="w-3 h-3" />;
      case 'freezer': return <Snowflake className="w-3 h-3" />;
      case 'pantry': return <Archive className="w-3 h-3" />;
      default: return <Archive className="w-3 h-3" />;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-4xl mx-auto my-8 p-6 bg-slate-900 rounded-2xl border border-slate-800"
    >
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold flex items-center">
          <span className="mr-2">🥑</span> Detected Ingredients
        </h2>
        <button
          onClick={onConfirm}
          className="px-6 py-2 bg-teal-600 hover:bg-teal-500 text-white rounded-lg font-semibold flex items-center transition-colors"
        >
          Confirm & Cook <Check className="ml-2 w-4 h-4" />
        </button>
      </div>

      <div className="flex flex-wrap gap-3">
        {ingredients.map((ing, idx) => {
          const expiry = expiryInfo?.[ing] || { days: 7, urgency: 'medium', storage: 'pantry' };

          return (
            <motion.div
              key={`${ing}-${idx}`}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: idx * 0.05 }}
              className="flex flex-col px-4 py-2 bg-slate-800 rounded-xl border border-slate-700 text-slate-300 group hover:border-teal-500/50 transition-all min-w-[140px]"
            >
              <div className="flex items-center justify-between mb-1">
                <span className="capitalize font-medium">{ing}</span>
                <button
                  onClick={() => onRemove(ing)}
                  className="p-0.5 rounded-full hover:bg-red-500/20 hover:text-red-400 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center gap-2 text-xs">
                <div className={`flex items-center gap-1 px-2 py-0.5 rounded border ${getUrgencyColor(expiry.urgency)}`}>
                  <Clock className="w-3 h-3" />
                  <span>{expiry.days}d</span>
                </div>
                <div className="flex items-center gap-1 text-slate-500" title={expiry.storage}>
                  {getStorageIcon(expiry.storage)}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
};

export default IngredientsList;
