import React from 'react';
import { motion } from 'framer-motion';
import { ChefHat, Flame, Heart, Zap, Crosshair } from 'lucide-react';

const RecipeSelector = ({ recipes, onSelect, onBack }) => {
  return (
    <div className="w-full max-w-6xl mx-auto my-16 px-6">
      <div className="flex justify-between items-center mb-12">
        <button
          onClick={onBack}
          className="px-4 py-2 bg-slate-900 border border-slate-800 rounded-xl text-slate-400 hover:text-white hover:border-teal-500/50 transition-all font-medium text-sm"
        >
          ← Back to Pantry
        </button>
        <h2 className="text-4xl font-extrabold bg-gradient-to-r from-teal-200 via-blue-200 to-purple-200 bg-clip-text text-transparent">
          👨‍🍳 Pick a Recipe
        </h2>
        <div className="w-[100px]" /> {/* Spacer */}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {(recipes || []).map((recipe, idx) => {
          const { nutritional_info, health_score, name } = recipe;
          const scoreColor = health_score > 80 ? 'text-emerald-400' : health_score > 50 ? 'text-amber-400' : 'text-rose-400';

          return (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.1 }}
              whileHover={{ y: -8, scale: 1.02 }}
              onClick={() => onSelect(recipe.name)}
              className="group cursor-pointer relative overflow-hidden bg-slate-900 rounded-[2rem] p-8 border border-slate-800 hover:border-teal-500/50 transition-all shadow-xl hover:shadow-[0_0_30px_rgba(20,184,166,0.2)] flex flex-col h-full"
            >
              {/* Health Score Badge */}
              <div className="absolute top-6 right-6 flex flex-col items-center">
                <div className={`text-2xl font-black ${scoreColor}`}>
                  {health_score}
                </div>
                <div className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Health</div>
              </div>

              <div className="relative z-10">
                <div className="p-3 bg-slate-800 w-fit rounded-xl mb-6 group-hover:bg-slate-700 transition-colors shadow-lg">
                  <ChefHat className="w-6 h-6 text-teal-400 group-hover:text-teal-300 transition-colors" />
                </div>

                <h3 className="text-2xl font-bold text-slate-100 group-hover:text-white transition-colors mb-6 line-clamp-2 min-h-[4rem]">
                  {name}
                </h3>

                {/* Nutrition Grid */}
                <div className="grid grid-cols-2 gap-3 mt-auto">
                  <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800/50 group-hover:border-teal-500/10 transition-colors">
                    <div className="flex items-center gap-2 mb-1">
                      <Flame className="w-3.5 h-3.5 text-orange-400" />
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Calories</span>
                    </div>
                    <div className="text-sm font-bold text-slate-200">{nutritional_info?.calories} kcal</div>
                  </div>
                  <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800/50 group-hover:border-teal-500/10 transition-colors">
                    <div className="flex items-center gap-2 mb-1">
                      <Zap className="w-3.5 h-3.5 text-blue-400" />
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Protein</span>
                    </div>
                    <div className="text-sm font-bold text-slate-200">{nutritional_info?.protein}g</div>
                  </div>
                  <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800/50 group-hover:border-teal-500/10 transition-colors">
                    <div className="flex items-center gap-2 mb-1">
                      <Crosshair className="w-3.5 h-3.5 text-purple-400" />
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Carbs</span>
                    </div>
                    <div className="text-sm font-bold text-slate-200">{nutritional_info?.carbs}g</div>
                  </div>
                  <div className="bg-slate-950/50 p-3 rounded-2xl border border-slate-800/50 group-hover:border-teal-500/10 transition-colors">
                    <div className="flex items-center gap-2 mb-1">
                      <Heart className="w-3.5 h-3.5 text-rose-400" />
                      <span className="text-[10px] text-slate-500 uppercase font-bold">Fat</span>
                    </div>
                    <div className="text-sm font-bold text-slate-200">{nutritional_info?.fat}g</div>
                  </div>
                </div>
              </div>

              {/* Shine effect */}
              <div className="absolute top-0 -inset-full h-full w-1/2 z-5 block transform -skew-x-12 bg-gradient-to-r from-transparent to-white opacity-5 group-hover:animate-shine" />
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default RecipeSelector;
