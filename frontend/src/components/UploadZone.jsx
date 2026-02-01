import React, { useRef, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, Sparkles, RefreshCcw, X, Scan } from 'lucide-react';

const UploadZone = ({ onFileSelect, isAnalyzing }) => {
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [stream, setStream] = useState(null);
  const [cameraError, setCameraError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };

  const startCamera = async () => {
    try {
      setCameraError(null);
      setIsCameraActive(true); // Mount the video element first

      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment',
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      setStream(mediaStream);
    } catch (err) {
      console.error("Camera access error:", err);
      setCameraError("Could not access camera. Please check permissions.");
      setIsCameraActive(false);
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
    setStream(null);
    setIsCameraActive(false);
  };

  useEffect(() => {
    if (isCameraActive && stream && videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch(e => console.error("Video play error:", e));
    }
  }, [isCameraActive, stream]);

  const capturePhoto = () => {
    console.log("📸 Capture button clicked");
    if (videoRef.current && canvasRef.current && stream) {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      // Ensure video is playing and has dimensions
      if (video.videoWidth === 0 || video.videoHeight === 0) {
        console.warn("Video dimensions not ready yet");
        return;
      }

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      canvas.toBlob((blob) => {
        if (blob) {
          const file = new File([blob], "webcam-capture.jpg", { type: "image/jpeg" });
          onFileSelect(file);
          stopCamera();
        }
      }, 'image/jpeg', 0.95);
    }
  };

  useEffect(() => {
    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, [stream]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-3xl w-full"
      >
        <h1 className="text-6xl font-black mb-6 bg-gradient-to-r from-teal-400 via-blue-500 to-purple-500 bg-clip-text text-transparent">
          SnapChef
        </h1>
        <p className="text-xl text-slate-400 mb-12 font-medium">
          Scan your pantry. Unlock culinary magic.
        </p>

        <div className="relative group overflow-hidden bg-slate-900/50 backdrop-blur-xl border-2 border-slate-800 rounded-[2.5rem] shadow-2xl transition-all hover:border-teal-500/50">
          <AnimatePresence mode="wait">
            {!isCameraActive ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="p-16 flex flex-col items-center"
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  className="hidden"
                  accept="image/*"
                />

                <div className="flex gap-6 mb-10">
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => fileInputRef.current?.click()}
                    className="flex flex-col items-center gap-4 bg-slate-800 hover:bg-slate-700 p-8 rounded-3xl transition-colors shadow-lg border border-slate-700"
                  >
                    <Upload className="w-10 h-10 text-teal-400" />
                    <span className="text-sm font-bold uppercase tracking-widest text-slate-300">Upload Photo</span>
                  </motion.button>

                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={startCamera}
                    className="flex flex-col items-center gap-4 bg-teal-500 hover:bg-teal-400 p-8 rounded-3xl transition-colors shadow-lg shadow-teal-500/20"
                  >
                    <Camera className="w-10 h-10 text-white" />
                    <span className="text-sm font-bold uppercase tracking-widest text-white">Use Camera</span>
                  </motion.button>
                </div>

                <div className="space-y-2">
                  <h3 className="text-2xl font-bold text-slate-100">
                    {isAnalyzing ? "Analyzing Ingredients..." : "Get Started"}
                  </h3>
                  <p className="text-slate-500">
                    Snap a photo of your fridge or pantry
                  </p>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="camera"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="relative"
              >
                <div className="relative aspect-video bg-black overflow-hidden group/camera">
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-cover"
                  />

                  {/* Scanner overlay */}
                  <div className="absolute inset-0 pointer-events-none border-2 border-teal-500/20 m-8 rounded-2xl">
                    <div className="absolute top-0 left-0 w-8 h-8 border-t-4 border-l-4 border-teal-400 rounded-tl-xl" />
                    <div className="absolute top-0 right-0 w-8 h-8 border-t-4 border-r-4 border-teal-400 rounded-tr-xl" />
                    <div className="absolute bottom-0 left-0 w-8 h-8 border-b-4 border-l-4 border-teal-400 rounded-bl-xl" />
                    <div className="absolute bottom-0 right-0 w-8 h-8 border-b-4 border-r-4 border-teal-400 rounded-br-xl" />
                    <motion.div
                      animate={{ top: ['10%', '90%', '10%'] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
                      className="absolute left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-teal-400 to-transparent shadow-[0_0_15px_rgba(45,212,191,0.5)]"
                    />
                  </div>

                  <button
                    onClick={stopCamera}
                    className="absolute top-6 right-6 p-2 bg-slate-900/80 hover:bg-slate-900 text-white rounded-full backdrop-blur-md transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="p-8 bg-slate-900 flex justify-center items-center gap-6">
                  <motion.button
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                    onClick={capturePhoto}
                    className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-2xl group/btn"
                  >
                    <div className="w-12 h-12 border-4 border-slate-900 rounded-full group-hover/btn:scale-110 transition-transform" />
                  </motion.button>
                  <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Tap to Capture</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {isAnalyzing && (
            <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center z-50">
              <div className="relative">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-20 h-20 border-t-4 border-teal-500 rounded-full"
                />
                <Scan className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-teal-300 w-8 h-8" />
              </div>
              <p className="mt-6 text-teal-400 font-bold tracking-[0.2em] uppercase text-sm animate-pulse">Analyzing Pantry...</p>
            </div>
          )}
        </div>

        {cameraError && (
          <p className="mt-4 text-rose-500 text-sm font-medium">{cameraError}</p>
        )}

        <canvas ref={canvasRef} className="hidden" />
      </motion.div>
    </div>
  );
};

export default UploadZone;
