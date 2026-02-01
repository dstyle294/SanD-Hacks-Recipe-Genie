import React, { useRef } from 'react';
import { motion } from 'framer-motion';
import { Upload, Camera, Sparkles } from 'lucide-react';

const UploadZone = ({ onFileSelect, isAnalyzing }) => {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-2xl w-full"
      >
        <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-teal-400 to-blue-500 bg-clip-text text-transparent">
          Recipe Genie
        </h1>
        <p className="text-xl text-slate-400 mb-12">
          Scan your pantry. Unlock culinary magic.
        </p>

        <motion.div
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          className="relative group cursor-pointer border-2 border-dashed border-slate-700 hover:border-teal-500 rounded-3xl p-12 bg-slate-900/50 backdrop-blur-sm transition-colors"
          onClick={() => fileInputRef.current?.click()}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            className="hidden"
            accept="image/*"
          />

          <div className="flex flex-col items-center space-y-4">
            {isAnalyzing ? (
              <div className="relative">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 border-t-4 border-teal-500 rounded-full"
                />
                <Sparkles className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-teal-300 w-8 h-8" />
              </div>
            ) : (
              <div className="w-20 h-20 bg-slate-800 rounded-full flex items-center justify-center group-hover:bg-slate-700 transition-colors">
                <Camera className="w-10 h-10 text-teal-400" />
              </div>
            )}

            <h3 className="text-2xl font-semibold text-slate-200">
              {isAnalyzing ? "Analyzing Ingredients..." : "Upload Pantry Photo"}
            </h3>
            <p className="text-slate-500">
              Drag & drop or Click to browse
            </p>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default UploadZone;
