import React from 'react';
import { motion } from 'framer-motion';

export function AbstractCitizen({ className = "", color = "#FF9933" }: { className?: string, color?: string }) {
  return (
    <motion.svg 
      className={`w-full h-full ${className}`} 
      viewBox="0 0 200 200" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      animate={{ 
        y: [-10, 10, -10],
      }}
      transition={{ 
        duration: 4, 
        repeat: Infinity, 
        ease: "easeInOut" 
      }}
    >
      {/* Background Glow */}
      <motion.circle 
        cx="100" 
        cy="100" 
        r="80" 
        fill={color} 
        fillOpacity="0.1"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
      />
      
      {/* Character Base */}
      <path d="M100 40 C116.569 40 130 53.4315 130 70 C130 86.5685 116.569 100 100 100 C83.4315 100 70 86.5685 70 70 C70 53.4315 83.4315 40 100 40 Z" fill={color} fillOpacity="0.9"/>
      
      {/* Abstract Body/Clothing */}
      <path d="M40 180 C40 146.863 66.8629 120 100 120 C133.137 120 160 146.863 160 180 L160 200 L40 200 L40 180 Z" fill="url(#paint0_linear)"/>
      <path d="M70 120 L130 200 L160 200 C160 166.863 133.137 140 100 140 L70 120 Z" fill={color} fillOpacity="0.8"/>

      {/* Decorative elements */}
      <motion.circle 
        className="citizen-decor" 
        cx="40" 
        cy="80" 
        r="8" 
        fill="#138808"
        animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut", delay: 0 }}
      />
      <motion.circle 
        className="citizen-decor" 
        cx="160" 
        cy="60" 
        r="5" 
        fill="#FF9933"
        animate={{ scale: [1.2, 0.8, 1.2], opacity: [1, 0.5, 1] }}
        transition={{ duration: 2.5, repeat: Infinity, ease: "easeInOut", delay: 0.5 }}
      />
      <motion.circle 
        className="citizen-decor" 
        cx="140" 
        cy="110" 
        r="12" 
        fill="currentColor" 
        fillOpacity="0.2"
        animate={{ scale: [1, 1.3, 1] }}
        transition={{ duration: 3, repeat: Infinity, ease: "easeInOut", delay: 1 }}
      />
      
      <defs>
        <linearGradient id="paint0_linear" x1="100" y1="120" x2="100" y2="200" gradientUnits="userSpaceOnUse">
          <stop stopColor="currentColor" stopOpacity="0.2"/>
          <stop offset="1" stopColor="currentColor" stopOpacity="0.8"/>
        </linearGradient>
      </defs>
    </motion.svg>
  );
}
