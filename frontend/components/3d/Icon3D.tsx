import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface Icon3DProps {
  icon: LucideIcon;
  gradient?: string;
  size?: number;
  className?: string;
  animate?: boolean;
}

export function Icon3D({
  icon: Icon,
  gradient = 'from-blue-500 to-blue-600',
  size = 64,
  className = '',
  animate = true,
}: Icon3DProps) {
  return (
    <motion.div
      className={`relative ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        perspective: '1000px',
        transformStyle: 'preserve-3d',
      }}
      whileHover={
        animate
          ? {
              rotateY: 360,
              scale: 1.1,
            }
          : undefined
      }
      transition={{
        duration: 0.8,
        ease: 'easeOut',
      }}
    >
      {/* Shadow layer */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-[var(--radius-2xl)] blur-lg opacity-50`}
        style={{
          transform: 'translateZ(-20px)',
        }}
      />

      {/* Middle layer */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-[var(--radius-2xl)] opacity-80`}
        style={{
          transform: 'translateZ(-10px)',
        }}
      />

      {/* Top layer with icon */}
      <div
        className={`absolute inset-0 bg-gradient-to-br ${gradient} rounded-[var(--radius-2xl)] flex items-center justify-center shadow-[var(--shadow-12)]`}
        style={{
          transform: 'translateZ(0px)',
        }}
      >
        <Icon className="text-white" size={size * 0.5} />
      </div>

      {/* Shine effect */}
      <div
        className="absolute inset-0 bg-gradient-to-tr from-white/0 via-white/30 to-white/0 rounded-[var(--radius-2xl)] opacity-0 group-hover:opacity-100 transition-opacity"
        style={{
          transform: 'translateZ(1px)',
        }}
      />
    </motion.div>
  );
}
