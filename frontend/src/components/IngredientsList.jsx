import React from 'react';
import { motion } from 'framer-motion';
import { X, Check } from 'lucide-react';

const IngredientsList = ({ ingredients, onRemove, onConfirm }) => {
  if (!ingredients.length) return null;

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
        {ingredients.map((ing, idx) => (
          <motion.div
            key={`${ing}-${idx}`}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: idx * 0.05 }}
            className="flex items-center px-4 py-2 bg-slate-800 rounded-full border border-slate-700 text-slate-300 group hover:border-teal-500/50 hover:text-white transition-all"
          >
            <span className="capitalize">{ing}</span>
            <button
              onClick={() => onRemove(ing)}
              className="ml-2 p-0.5 rounded-full hover:bg-red-500/20 hover:text-red-400 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default IngredientsList;
