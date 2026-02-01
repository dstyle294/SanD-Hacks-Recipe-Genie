import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, LogOut, Settings, History, Package, ChevronDown, UserCircle2 } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import * as api from '../api';

const UserMenu = ({ user, onAuthSuccess, onLogout, onViewPantry, onViewHistory }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      const data = await api.authGoogle(credentialResponse.credential);
      onAuthSuccess(data);
      setIsOpen(false);
    } catch (err) {
      console.error("Auth failed:", err);
      alert("Authentication failed. Please try again.");
    }
  };

  if (!user) {
    return (
      <div className="relative z-50">
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => alert("Login Failed")}
          useOneTap
          theme="filled_black"
          shape="pill"
        />
      </div>
    );
  }

  return (
    <div className="relative z-50">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-3 p-1.5 pr-4 bg-slate-900 border border-slate-800 rounded-full hover:border-teal-500/50 transition-all group"
      >
        <div className="w-9 h-9 rounded-full overflow-hidden border-2 border-slate-800 group-hover:border-teal-500/30 transition-all">
          {user.picture ? (
            <img src={user.picture} alt={user.full_name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full bg-slate-800 flex items-center justify-center">
              <User className="w-5 h-5 text-slate-400" />
            </div>
          )}
        </div>
        <div className="text-left hidden sm:block">
          <p className="text-xs font-bold text-white leading-tight">{user.full_name}</p>
          <p className="text-[10px] text-slate-500 font-medium">Verified Account</p>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 z-40"
            />
            <motion.div
              initial={{ opacity: 0, y: 10, scale: 0.95 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: 10, scale: 0.95 }}
              className="absolute right-0 mt-3 w-64 bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              <div className="p-4 border-b border-slate-800 bg-slate-800/20">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Signed in as</p>
                <p className="text-sm font-bold text-white truncate">{user.email}</p>
              </div>

              <div className="p-2">
                <button
                  onClick={() => {
                    console.log("DEBUG: UserMenu - My Pantry History clicked");
                    onViewPantry();
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-xl transition-all group"
                >
                  <Package className="w-4 h-4 text-slate-500 group-hover:text-teal-400" />
                  <span className="text-sm font-medium">My Pantry History</span>
                </button>
                <button
                  onClick={() => {
                    console.log("DEBUG: UserMenu - Saved Recipes clicked");
                    onViewHistory();
                    setIsOpen(false);
                  }}
                  className="w-full flex items-center gap-3 px-3 py-2.5 text-slate-300 hover:text-white hover:bg-slate-800 rounded-xl transition-all group"
                >
                  <History className="w-4 h-4 text-slate-500 group-hover:text-teal-400" />
                  <span className="text-sm font-medium">Saved Recipes</span>
                </button>
              </div>

              <div className="p-2 border-t border-slate-800">
                <button
                  onClick={() => { onLogout(); setIsOpen(false); }}
                  className="w-full flex items-center gap-3 px-3 py-2.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-xl transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  <span className="text-sm font-medium">Sign Out</span>
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UserMenu;
