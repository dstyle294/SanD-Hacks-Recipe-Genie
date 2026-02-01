import React from 'react';
import { motion } from 'framer-motion';

const LoadingScreen = ({ message, subMessage }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[50vh] py-20 text-center">
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          rotate: [0, 180, 360],
          borderRadius: ["20%", "50%", "20%"]
        }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        className="w-24 h-24 bg-gradient-to-tr from-teal-400 via-blue-500 to-purple-600 shadow-[0_0_40px_rgba(45,212,191,0.6)] mb-10"
      />
      <h2 className="text-4xl font-extrabold bg-gradient-to-r from-teal-200 via-blue-200 to-purple-200 bg-clip-text text-transparent mb-6">
        {message || "Cooking up magic..."}
      </h2>
      <p className="text-slate-400 text-xl max-w-lg leading-relaxed">
        {subMessage || "Our AI Chef is working hard to find the best options for you."}
      </p>
    </div>
  );
};

export default LoadingScreen;
