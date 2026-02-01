import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Play, FileText, X, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const VideoCard = ({ video }) => {
  const [showGuide, setShowGuide] = useState(false);
  const [showVideo, setShowVideo] = useState(false);

  // Parse details
  const scoreColor = video.smart_score > 80 ? 'text-green-400' : video.smart_score > 50 ? 'text-yellow-400' : 'text-red-400';
  const ringColor = video.smart_score > 80 ? '#4ade80' : video.smart_score > 50 ? '#facc15' : '#f87171';

  return (
    <>
      <motion.div
        layout
        className="bg-slate-900 rounded-2xl overflow-hidden border border-slate-800 shadow-xl hover:shadow-2xl transition-all group"
      >
        {/* Thumbnail */}
        <div className="relative aspect-video bg-slate-950 cursor-pointer overflow-hidden" onClick={() => setShowVideo(true)}>
          <img
            src={video.thumbnail}
            alt={video.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-black/40 group-hover:bg-black/20 transition-colors flex items-center justify-center">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
              <Play className="w-6 h-6 text-white ml-1" />
            </div>
          </div>

          {/* Smart Score Badge */}
          <div className="absolute top-2 right-2 bg-slate-900/80 backdrop-blur-md rounded-full px-3 py-1 flex items-center border border-slate-700">
            <span className={`text-xs font-bold ${scoreColor} mr-1`}>{Math.round(video.smart_score)}%</span>
            <span className="text-[10px] text-slate-400 uppercase tracking-wider">Match</span>
          </div>
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="font-bold text-lg leading-tight mb-2 line-clamp-2" title={video.title}>
            {video.title}
          </h3>

          <div className="flex justify-between items-center text-sm text-slate-500 mb-4">
            <span className="font-medium text-slate-400">{video.channel}</span>
            <span>{parseInt(video.views).toLocaleString()} views</span>
          </div>

          <div className="flex space-x-2">
            <button
              onClick={() => setShowGuide(true)}
              className="flex-1 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-sm font-medium transition-colors flex items-center justify-center"
            >
              <FileText className="w-4 h-4 mr-2" /> Read Guide
            </button>
            <a
              href={video.url}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition-colors flex items-center"
              title="Open on YouTube"
            >
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
        </div>
      </motion.div>

      {/* Guide Modal */}
      <AnimatePresence>
        {showGuide && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
            onClick={() => setShowGuide(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-slate-900 w-full max-w-2xl max-h-[85vh] rounded-2xl shadow-2xl overflow-hidden flex flex-col border border-slate-700"
            >
              <div className="p-6 border-b border-slate-700 flex justify-between items-center bg-slate-900 z-10">
                <h3 className="text-xl font-bold truncate pr-4">Make it Accessible</h3>
                <button onClick={() => setShowGuide(false)} className="p-2 hover:bg-slate-800 rounded-full transition-colors">
                  <X className="w-5 h-5 text-slate-400" />
                </button>
              </div>

              <div className="p-6 overflow-y-auto custom-scrollbar prose prose-invert prose-slate max-w-none">
                <ReactMarkdown>{video.accessible_guide || "*No guide generated.*"}</ReactMarkdown>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Video Modal */}
      <AnimatePresence>
        {showVideo && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/90 backdrop-blur-md"
            onClick={() => setShowVideo(false)}
          >
            <div className="w-full max-w-4xl aspect-video rounded-xl overflow-hidden shadow-2xl border border-slate-800 relative">
              <button
                onClick={() => setShowVideo(false)}
                className="absolute -top-12 right-0 text-white hover:text-slate-300 transition-colors flex items-center"
              >
                Close <X className="ml-2 w-6 h-6" />
              </button>
              <iframe
                width="100%"
                height="100%"
                src={`https://www.youtube.com/embed/${video.url.split('v=')[1]}`}
                title="YouTube video player"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
              />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

const VideoResults = ({ videos, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-32 text-center">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 180, 360]
          }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
          className="w-20 h-20 bg-gradient-to-tr from-teal-400 to-blue-500 rounded-2xl shadow-[0_0_30px_rgba(45,212,191,0.5)] mb-8"
        />
        <h2 className="text-3xl font-extrabold bg-gradient-to-r from-teal-200 to-blue-200 bg-clip-text text-transparent">
          Cooking up your results...
        </h2>
        <p className="text-slate-400 mt-4 text-lg max-w-md">
          Our AI Chef is verifying ingredients, checking transcripts, and ranking the best tutorials just for you.
        </p>
      </div>
    );
  }

  if (!videos.length) return null;

  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-12">
      <h2 className="text-3xl font-bold mb-10 flex items-center text-white">
        <span className="bg-teal-500/10 p-2 rounded-lg mr-3 border border-teal-500/20">🎥</span> Verified Results
      </h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {videos.map((video, idx) => (
          <VideoCard key={idx} video={video} />
        ))}
      </div>
    </div>
  );
};

export default VideoResults;
