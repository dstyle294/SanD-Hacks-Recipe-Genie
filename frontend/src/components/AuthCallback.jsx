import React, { useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import * as api from '../api';

const AuthCallback = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const handleCallback = async () => {
      const params = new URLSearchParams(location.search);
      const code = params.get('code');

      if (code) {
        try {
          const data = await api.authCallback(code);
          localStorage.setItem('auth_token', data.token);
          onLoginSuccess(data.user);
          navigate('/');
        } catch (err) {
          console.error("Auth failed", err);
          navigate('/');
        }
      }
    };

    handleCallback();
  }, [location, navigate, onLoginSuccess]);

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center">
      <div className="w-16 h-16 border-4 border-teal-500 border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-slate-400 font-medium">Authenticating with Google...</p>
    </div>
  );
};

export default AuthCallback;
