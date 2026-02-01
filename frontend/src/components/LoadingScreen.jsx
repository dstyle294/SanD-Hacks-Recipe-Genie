import React from 'react';
import { motion } from 'framer-motion';
import { Utensils } from 'lucide-react';

const LoadingScreen = ({ text = "Consulting the AI Chef..." }) => {
    return (
        <div className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex flex-col items-center justify-center">
            {/* Minimal Pulsing Logo */}
            <motion.div
                className="relative mb-8 text-primary"
                animate={{
                    scale: [1, 1.1, 1],
                    opacity: [0.8, 1, 0.8]
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    ease: "easeInOut"
                }}
            >
                <div className="absolute inset-0 bg-primary blur-2xl opacity-20 rounded-full" />
                <Utensils size={48} className="relative z-10" />
            </motion.div>

            <motion.p
                className="text-lg font-light tracking-[0.2em] uppercase text-text-dim"
                animate={{ opacity: [0.4, 0.8, 0.4] }}
                transition={{ duration: 1.5, repeat: Infinity }}
            >
                {text}
            </motion.p>
        </div>
    );
};

export default LoadingScreen;
