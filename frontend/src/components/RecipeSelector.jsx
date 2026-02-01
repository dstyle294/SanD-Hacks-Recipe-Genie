import React from 'react';
import { motion } from 'framer-motion';
import { ChefHat } from 'lucide-react';

const RecipeSelector = ({ recipes, onSelect }) => {
  return (
    <div className="w-full max-w-6xl mx-auto my-16 px-6">
      <h2 className="text-4xl font-extrabold text-center mb-12 bg-gradient-to-r from-teal-200 via-blue-200 to-purple-200 bg-clip-text text-transparent">
        👨‍🍳 Ready to Cook? Pick a Recipe
      </h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {recipes.map((recipe, idx) => (
          <motion.div
            key={idx}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: idx * 0.1 }}
            whileHover={{ y: -8, scale: 1.02 }}
            onClick={() => onSelect(recipe)}
            className="group cursor-pointer relative overflow-hidden bg-slate-900 rounded-[2rem] p-8 border border-slate-800 hover:border-teal-500/50 transition-all shadow-xl hover:shadow-[0_0_30px_rgba(20,184,166,0.2)]"
          >
            {/* Animated Gradient Background */}
            <div className="absolute inset-0 bg-gradient-to-br from-teal-500/0 via-blue-500/0 to-purple-500/0 group-hover:from-teal-500/10 group-hover:via-blue-500/10 group-hover:to-purple-500/5 transition-all duration-500" />

            <div className="relative z-10 flex flex-col items-center text-center">
              <div className="p-4 bg-slate-800 rounded-2xl mb-6 group-hover:bg-slate-700 transition-colors shadow-lg">
                <ChefHat className="w-10 h-10 text-teal-400 group-hover:text-teal-300 transition-colors" />
              </div>

              <h3 className="text-2xl font-bold text-slate-100 group-hover:text-white transition-colors mb-3">
                {recipe}
              </h3>
              <p className="text-slate-400 text-sm group-hover:text-slate-300">
                Tap to find the best tutorials
              </p>
            </div>

            {/* Shine effect */}
            <div className="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-10 group-hover:animate-shine" />
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default RecipeSelector;
