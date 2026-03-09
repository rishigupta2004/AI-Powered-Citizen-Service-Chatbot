import React from 'react';
import { motion } from 'framer-motion';

export function Mandala({ className = "", size = 200 }: { className?: string, size?: number }) {
  return (
    <div className={`relative flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      {/* Outer Glow */}
      <motion.div 
        className="absolute inset-0 rounded-full bg-saffron/20 blur-3xl"
        animate={{ scale: [1, 1.2, 1], opacity: [0.5, 0.8, 0.5] }}
        transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
      />
      
      {/* Outer Ring */}
      <motion.svg 
        className="absolute mandala-layer opacity-40 text-saffron" 
        viewBox="0 0 100 100" 
        style={{ width: '100%', height: '100%' }}
        animate={{ rotate: 360 }}
        transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
      >
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 4" />
        {[...Array(12)].map((_, i) => (
          <path key={`outer-${i}`} d="M 50 2 C 55 10, 45 10, 50 20" fill="none" stroke="currentColor" strokeWidth="0.5" 
                transform={`rotate(${i * 30} 50 50)`} />
        ))}
      </motion.svg>

      {/* Middle Ring */}
      <motion.svg 
        className="absolute mandala-layer opacity-60 text-white" 
        viewBox="0 0 100 100" 
        style={{ width: '75%', height: '75%' }}
        animate={{ rotate: -360 }}
        transition={{ duration: 45, repeat: Infinity, ease: "linear" }}
      >
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="1" />
        {[...Array(8)].map((_, i) => (
          <path key={`mid-${i}`} d="M 50 2 Q 60 25, 50 48 Q 40 25, 50 2" fill="none" stroke="currentColor" strokeWidth="1" 
                transform={`rotate(${i * 45} 50 50)`} />
        ))}
      </motion.svg>

      {/* Inner Star/Lotus */}
      <motion.svg 
        className="absolute mandala-layer text-green" 
        viewBox="0 0 100 100" 
        style={{ width: '50%', height: '50%' }}
        animate={{ rotate: 360 }}
        transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
      >
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="1 2" />
        {[...Array(16)].map((_, i) => (
          <line key={`inner-${i}`} x1="50" y1="2" x2="50" y2="48" stroke="currentColor" strokeWidth="1" 
                transform={`rotate(${i * 22.5} 50 50)`} />
        ))}
        <motion.circle 
          cx="50" 
          cy="50" 
          r="10" 
          fill="currentColor"
          animate={{ scale: [1, 1.1, 1], opacity: [0.8, 1, 0.8] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      </motion.svg>
    </div>
  );
}
