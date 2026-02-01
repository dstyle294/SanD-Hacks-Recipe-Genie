import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, ChefHat } from 'lucide-react';

const UnifiedLoader = ({ isVisible, message }) => {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-slate-950/80 backdrop-blur-xl flex flex-col items-center justify-center p-6"
        >
          {/* Background Glow */}
          <div className="absolute w-[300px] h-[300px] bg-teal-500/20 blur-[100px] rounded-full animate-pulse" />

          <div className="relative flex flex-col items-center">
            {/* Animated Icon */}
            <motion.div
              animate={{
                scale: [1, 1.1, 1],
                rotate: [0, 5, -5, 0]
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="w-24 h-24 bg-gradient-to-br from-teal-400 to-emerald-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-teal-500/40 mb-8"
            >
              <ChefHat className="text-white w-12 h-12" />
            </motion.div>

            {/* Loading Text */}
            <motion.h3
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-2xl font-bold text-white text-center mb-3"
            >
              {message || "Working some magic..."}
            </motion.h3>

            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-teal-400 animate-pulse" />
              <p className="text-slate-400 font-medium">Please wait a moment</p>
            </div>

            {/* Progress Bar (Indeterminate) */}
            <div className="mt-8 w-48 h-1 bg-slate-800 rounded-full overflow-hidden">
              <motion.div
                animate={{ x: ["-100%", "100%"] }}
                transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                className="w-1/2 h-full bg-gradient-to-r from-teal-500 to-emerald-500"
              />
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};

export default UnifiedLoader;
