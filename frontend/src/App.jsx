import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Sparkles, LogIn, Utensils, Clock, Camera, Play, CheckCircle } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import ReactMarkdown from 'react-markdown';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import LoadingScreen from './components/LoadingScreen';

const API_URL = 'http://localhost:8000';
const GOOGLE_CLIENT_ID = "355577889961-qmhcoo6561fiaqgv7htdlc3lhva2tilo.apps.googleusercontent.com";

function AppContent() {
    const [token, setToken] = useState(localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [notifications, setNotifications] = useState([]);
    const [step, setStep] = useState(token ? 'upload' : 'login');
    const [ingredients, setIngredients] = useState([]);
    const [recipes, setRecipes] = useState([]);
    const [selectedRecipe, setSelectedRecipe] = useState(null);
    const [finalRecipe, setFinalRecipe] = useState(null);
    const [loading, setLoading] = useState(false);
    const [usePantry, setUsePantry] = useState(false);
    const [showCamera, setShowCamera] = useState(false);
    const webcamRef = useRef(null);

    useEffect(() => {
        if (token) {
            const savedName = localStorage.getItem('user_name');
            setUser({ name: savedName || 'Chef' });
        }
    }, [token]);

    const onDrop = async (acceptedFiles) => {
        setLoading(true);
        const formData = new FormData();
        formData.append('file', acceptedFiles[0]);

        try {
            const res = await axios.post(`${API_URL}/upload-ingredients`, formData, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setIngredients(res.data.ingredients);
            setStep('ingredients');
            toast.success('Ingredients detected!');
            setShowCamera(false);
        } catch (err) {
            console.error("Upload Error:", err);
            const msg = err.response?.data?.detail || 'Failed to detect ingredients';
            toast.error(`Error: ${msg}`);
        } finally {
            setLoading(false);
        }
    };

    const capture = useCallback(() => {
        // Trigger Full Screen Flash
        const flash = document.getElementById('camera-flash-overlay');
        if (flash) {
            flash.style.opacity = '1';
            // Play shutter sound effect if desired (optional, adding visual cues primarily)

            // Immediate UI feedback
            setTimeout(() => {
                flash.style.opacity = '0';
                setShowCamera(false); // Close camera immediately
                toast.success('Photo captured successfully! processing...');
            }, 100);
        }

        const imageSrc = webcamRef.current.getScreenshot();
        if (imageSrc) {
            // Process in background
            fetch(imageSrc)
                .then(res => res.blob())
                .then(blob => {
                    const file = new File([blob], "camera-capture.jpg", { type: "image/jpeg" });
                    onDrop([file]);
                });
        }
    }, [webcamRef]);

    const { getRootProps, getInputProps } = useDropzone({ onDrop, accept: { 'image/*': [] } });

    const handleGoogleSuccess = async (credentialResponse) => {
        setLoading(true);
        try {
            const res = await axios.post(`${API_URL}/auth/google`, {
                id_token: credentialResponse.credential
            });
            localStorage.setItem('token', res.data.access_token);
            if (res.data.user) {
                localStorage.setItem('user_name', res.data.user.full_name);
                setUser({ name: res.data.user.full_name });
            }
            setToken(res.data.access_token);
            setStep('upload');
            toast.success('Signed in with Google!');
        } catch (err) {
            console.error("Google Auth Error:", err);
            const msg = err.response?.data?.detail || 'Google Sign-In failed';
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    const generateRecipes = async (pref = '') => {
        setLoading(true);
        try {
            const res = await axios.post(`${API_URL}/generate-recipes`,
                { text: pref, use_pantry: usePantry },
                { headers: { Authorization: `Bearer ${token}` } }
            );
            setRecipes(res.data.recipes);
            setStep('recipes');
        } catch (err) {
            toast.error('Failed to generate recipes');
        } finally {
            setLoading(false);
        }
    };

    const pickRecipe = async (recipe) => {
        setLoading(true);
        setSelectedRecipe(recipe);
        try {
            const res = await axios.post(`${API_URL}/select-recipe`, recipe, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setFinalRecipe(res.data);
            setStep('final');
        } catch (err) {
            console.error("Video Search Error:", err);
            const msg = err.response?.data?.detail || 'Failed to find video. Please try again.';
            toast.error(msg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="main-layout min-h-screen">
            <ToastContainer theme="dark" />

            {/* Navbar */}
            <nav className="flex justify-between items-center py-8 mb-16 border-b border-white/5">
                <div className="text-3xl font-bold font-serif flex items-center gap-3 tracking-tight">
                    <span className="text-primary"><Utensils size={32} /></span>
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary via-yellow-200 to-primary animate-pulse">RECIPE GENIE</span>
                </div>
                {token && (
                    <div className="flex items-center gap-6">
                        <span className="text-text-dim font-light tracking-wide uppercase text-sm">Chef {user?.name}</span>
                        <button
                            className="btn-secondary text-xs uppercase tracking-widest hover:bg-primary hover:text-black border-primary/30"
                            onClick={() => { localStorage.clear(); setToken(null); setStep('login'); }}
                        >
                            End Service
                        </button>
                    </div>
                )}
            </nav>

            {/* Notifications */}
            <AnimatePresence>
                {notifications.length > 0 && notifications.map((notif, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                        className="mb-4 p-4 premium-card border-l-4 border-l-primary flex items-center gap-3 shadow-2xl"
                    >
                        <Clock size={16} className="text-primary" />
                        <span className="font-serif italic">{notif}</span>
                    </motion.div>
                ))}
            </AnimatePresence>

            {/* Main Content Areas */}
            <main className="animate-fade-in relative z-10">
                {step === 'login' && (
                    <div className="max-w-md mx-auto premium-card p-12 text-center relative overflow-hidden group">
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary to-transparent opacity-50" />

                        <div className="mb-8 flex justify-center text-primary relative">
                            <div className="absolute inset-0 bg-primary blur-3xl opacity-20 rounded-full" />
                            <Utensils size={64} className="relative z-10 drop-shadow-[0_0_15px_rgba(212,175,55,0.5)]" />
                        </div>

                        <h2 className="text-5xl font-bold mb-4 font-serif text-white tracking-tight">The AI Kitchen</h2>
                        <p className="text-text-dim mb-10 text-lg font-light leading-relaxed">
                            Where gastronomy meets intelligence.<br />
                            <span className="text-primary/60 italic text-sm">Sign in to curate your menu.</span>
                        </p>

                        <div className="flex justify-center transform hover:scale-105 transition-transform duration-300">
                            <GoogleLogin
                                onSuccess={handleGoogleSuccess}
                                onError={() => toast.error('Login Failed')}
                                theme="filled_black"
                                shape="pill"
                                text="continue_with"
                            />
                        </div>
                    </div>
                )}

                {step === 'upload' && (
                    <div className="text-center">
                        <h1 className="text-6xl font-bold mb-4 font-serif tracking-tight text-white">
                            What's in your <span className="text-primary italic">pantry?</span>
                        </h1>
                        <p className="text-text-dim text-xl mb-12 font-light tracking-wide">Capture your ingredients to begin the culinary journey.</p>

                        {!showCamera ? (
                            <div className="flex flex-col items-center gap-6">
                                <div {...getRootProps()} className="w-full max-w-2xl mx-auto premium-card p-12 border-dashed border border-primary/20 cursor-pointer hover:bg-white/5 transition-all group">
                                    <input {...getInputProps()} />
                                    <div className="flex flex-col items-center gap-6">
                                        <div className="p-6 rounded-full bg-primary/10 text-primary group-hover:scale-110 transition-transform duration-500 shadow-[0_0_20px_rgba(212,175,55,0.2)]">
                                            <Upload size={48} />
                                        </div>
                                        <div>
                                            <p className="text-xl font-serif text-white">Upload Image</p>
                                            <p className="text-text-dim text-sm mt-2 uppercase tracking-widest">Drag & drop or browse</p>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4 w-full max-w-2xl">
                                    <div className="h-[1px] bg-white/10 flex-1"></div>
                                    <span className="text-text-dim text-sm">OR</span>
                                    <div className="h-[1px] bg-white/10 flex-1"></div>
                                </div>

                                <button
                                    className="btn-secondary flex items-center gap-3 py-4 px-8 text-sm uppercase tracking-widest hover:shadow-[0_0_20px_rgba(212,175,55,0.3)]"
                                    onClick={() => setShowCamera(true)}
                                >
                                    <Camera size={20} /> Open Camera
                                </button>
                            </div>
                        ) : (
                            <div className="max-w-3xl mx-auto premium-card p-4 overflow-hidden relative">
                                <div className="aspect-video bg-black rounded-lg overflow-hidden mb-8 relative group border border-white/10 shadow-2xl">
                                    <Webcam
                                        audio={false}
                                        ref={webcamRef}
                                        screenshotFormat="image/jpeg"
                                        className="w-full h-full object-cover opacity-90"
                                        videoConstraints={{ facingMode: "environment" }}
                                    />
                                    {/* Vignette */}
                                    <div className="absolute inset-0 pointer-events-none bg-radial-gradient from-transparent to-black/60" />

                                    {/* Full Screen Flash Overlay - Portal-like behavior via fixed position */}
                                    <div id="camera-flash-overlay" className="fixed inset-0 bg-white opacity-0 z-[100] pointer-events-none transition-opacity duration-150 ease-out"></div>
                                </div>
                                <div className="flex justify-center gap-6">
                                    <button
                                        className="btn-secondary"
                                        onClick={() => setShowCamera(false)}
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        className="btn-primary flex items-center gap-2 shadow-[0_4px_15px_rgba(212,175,55,0.4)]"
                                        onClick={capture}
                                    >
                                        <Camera size={20} /> Capture Photo
                                    </button>
                                </div>
                            </div>
                        )}


                    </div>
                )}

                {step === 'ingredients' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="text-5xl font-bold mb-12 font-serif text-center uppercase tracking-[0.2em] text-primary">
                            Detected <span className="italic font-light text-white">Inventory</span>
                        </h2>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16">
                            {ingredients.map((ing, i) => (
                                <motion.div
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.08, duration: 0.5, ease: "easeOut" }}
                                    key={i}
                                    className="premium-card p-8 text-center relative group"
                                >
                                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                                    <p className="text-2xl font-semibold capitalize font-serif text-white mb-2">{ing.name}</p>
                                    <div className="h-[1px] w-8 bg-primary/30 mx-auto my-4 group-hover:w-16 transition-all duration-500" />
                                    <p className="text-text-dim text-xs flex items-center justify-center gap-2 uppercase tracking-[0.15em]">
                                        <Clock size={12} className="text-primary" /> {new Date(ing.expiry).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                    </p>
                                </motion.div>
                            ))}
                        </div>
                        <div className="premium-card p-8 mb-8 border border-primary/20 bg-black/40">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-2xl font-serif text-primary flex items-center gap-2"><Sparkles size={18} /> Chef's Preferences</h3>
                                <label className="flex items-center gap-3 cursor-pointer group">
                                    <span className="text-xs font-bold text-text-dim group-hover:text-primary transition-colors uppercase tracking-widest">Pantry Staples</span>
                                    <div
                                        onClick={() => setUsePantry(!usePantry)}
                                        className={`w-12 h-6 rounded-full p-1 transition-colors duration-300 border border-white/10 ${usePantry ? 'bg-primary' : 'bg-white/5'}`}
                                    >
                                        <div className={`w-4 h-4 bg-black rounded-full transition-transform duration-300 shadow-md ${usePantry ? 'translate-x-6' : 'translate-x-0'}`} />
                                    </div>
                                </label>
                            </div>
                            <div className="flex gap-4">
                                <input id="pref-text" placeholder="e.g. Spicy, Italian, Under 20 mins..." className="input-field flex-1 text-lg placeholder:text-white/20" />
                                <button
                                    className="btn-primary flex items-center gap-2 px-8"
                                    onClick={() => generateRecipes(document.getElementById('pref-text').value)}
                                >
                                    GENERATE MENU
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}

                {step === 'recipes' && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8 }}
                    >
                        <h2 className="text-5xl font-bold mb-12 font-serif text-center uppercase tracking-[0.2em] text-primary">
                            Chef's <span className="italic font-light text-white">Menu</span>
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
                            {recipes.map((rec, i) => (
                                <motion.div
                                    key={i}
                                    initial={{ opacity: 0, y: 30 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.12, duration: 0.6 }}
                                    className="premium-card group flex flex-col h-full overflow-hidden border-t-2 border-t-transparent hover:border-t-primary transition-all duration-500"
                                >
                                    <div className="h-56 overflow-hidden relative">
                                        <img
                                            src={rec.image_url}
                                            alt={rec.title}
                                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 filter brightness-90 group-hover:brightness-100"
                                            onError={(e) => {
                                                e.target.onerror = null;
                                                // Fallback if the search image fails
                                                e.target.src = "https://placehold.co/800x600?text=No+Image";
                                            }}
                                        />
                                        <div className="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-80" />
                                        <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md px-3 py-1 rounded text-xs font-bold flex items-center gap-1 text-primary border border-primary/20 shadow-lg">
                                            <Sparkles size={12} /> Score: {rec.health_score || 'N/A'}
                                        </div>
                                    </div>
                                    <div className="p-8 flex-1 flex flex-col relative bg-gradient-to-b from-transparent to-black/40">
                                        <h3 className="text-2xl font-serif font-bold mb-3 text-white group-hover:text-primary transition-colors">{rec.title}</h3>
                                        <p className="text-text-dim mb-6 flex-1 text-sm leading-relaxed font-light">"{rec.description}"</p>

                                        {/* Nutrition Info */}
                                        {rec.nutrition && (
                                            <div className="grid grid-cols-4 gap-2 mb-8 border-t border-white/5 pt-4">
                                                <div className="text-center group-hover:-translate-y-1 transition-transform duration-300">
                                                    <span className="block font-bold text-lg text-primary">{rec.nutrition.calories}</span>
                                                    <span className="text-[10px] text-text-dim uppercase tracking-wider">kcal</span>
                                                </div>
                                                <div className="text-center group-hover:-translate-y-1 transition-transform duration-300 delay-75">
                                                    <span className="block font-bold text-lg text-white">{rec.nutrition.protein}g</span>
                                                    <span className="text-[10px] text-text-dim uppercase tracking-wider">Prot</span>
                                                </div>
                                                <div className="text-center group-hover:-translate-y-1 transition-transform duration-300 delay-100">
                                                    <span className="block font-bold text-lg text-white">{rec.nutrition.carbs}g</span>
                                                    <span className="text-[10px] text-text-dim uppercase tracking-wider">Carb</span>
                                                </div>
                                                <div className="text-center group-hover:-translate-y-1 transition-transform duration-300 delay-150">
                                                    <span className="block font-bold text-lg text-white">{rec.nutrition.fat}g</span>
                                                    <span className="text-[10px] text-text-dim uppercase tracking-wider">Fat</span>
                                                </div>
                                            </div>
                                        )}

                                        <button
                                            className="btn-primary w-full mt-auto text-sm tracking-widest"
                                            onClick={() => pickRecipe(rec)}
                                            disabled={loading}
                                        >
                                            View Preparation
                                        </button>
                                    </div>
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {step === 'final' && finalRecipe && (
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 pb-20">
                        <div>
                            <h2 className="text-5xl font-bold mb-8 font-serif text-primary border-b border-white/10 pb-4">{selectedRecipe?.title}</h2>
                            <div className="premium-card p-10 prose prose-invert prose-headings:font-serif prose-p:font-light prose-li:text-gray-300 max-w-none text-lg leading-loose shadow-xl bg-black/40">
                                <ReactMarkdown>{finalRecipe.recipe_markdown}</ReactMarkdown>
                            </div>
                        </div>
                        <div className="flex flex-col gap-8 sticky top-8 h-fit">
                            <div className="premium-card p-2 aspect-video relative overflow-hidden shadow-2xl border-primary/20 bg-black">
                                <iframe
                                    className="w-full h-full rounded-sm"
                                    src={`https://www.youtube.com/embed/${finalRecipe.video.id}`}
                                    title="Cooking Video"
                                    frameBorder="0"
                                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                                    allowFullScreen
                                ></iframe>
                            </div>

                            {selectedRecipe?.nutrition && (
                                <div className="premium-card p-8 bg-gradient-to-br from-white/5 to-transparent border border-white/5">
                                    <h3 className="text-sm font-bold uppercase tracking-[0.3em] text-primary mb-6">Nutrition Snapshot</h3>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                            <span className="text-text-dim text-sm font-light">Calories</span>
                                            <span className="text-xl font-serif text-white">{selectedRecipe.nutrition.calories} <span className="text-[10px] text-text-dim">kcal</span></span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                            <span className="text-text-dim text-sm font-light">Protein</span>
                                            <span className="text-xl font-serif text-white">{selectedRecipe.nutrition.protein} <span className="text-[10px] text-text-dim">g</span></span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                            <span className="text-text-dim text-sm font-light">Carbs</span>
                                            <span className="text-xl font-serif text-white">{selectedRecipe.nutrition.carbs} <span className="text-[10px] text-text-dim">g</span></span>
                                        </div>
                                        <div className="flex justify-between items-center border-b border-white/5 pb-2">
                                            <span className="text-text-dim text-sm font-light">Fat</span>
                                            <span className="text-xl font-serif text-white">{selectedRecipe.nutrition.fat} <span className="text-[10px] text-text-dim">g</span></span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            <button
                                className="btn-secondary flex items-center justify-center gap-2 w-full py-5 uppercase tracking-[0.2em] text-sm hover:bg-white hover:text-black border-white/20 transition-all duration-500"
                                onClick={() => setStep('upload')}
                            >
                                Start New Service
                            </button>
                        </div>
                    </div>
                )}
            </main>

            {loading && <LoadingScreen />}
        </div>
    );
}

function App() {
    return (
        <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <AppContent />
        </GoogleOAuthProvider>
    );
}

export default App;
