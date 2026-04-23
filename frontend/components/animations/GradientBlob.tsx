import React from 'react';
import { motion } from 'framer-motion';

interface GradientBlobProps {
  colors?: string[];
  size?: number;
  blur?: number;
  opacity?: number;
  speed?: number;
  className?: string;
}

export function GradientBlob({
  colors = ['#FF9933', '#000080', '#138808'],
  size = 400,
  blur = 80,
  opacity = 0.6,
  speed = 20,
  className = '',
}: GradientBlobProps) {
  return (
    <motion.div
      className={`absolute rounded-full ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        background: `linear-gradient(135deg, ${colors.join(', ')})`,
        filter: `blur(${blur}px)`,
        opacity,
      }}
      animate={{
        x: [0, 50, -50, 0],
        y: [0, -50, 50, 0],
        scale: [1, 1.1, 0.9, 1],
        rotate: [0, 90, 180, 270, 360],
      }}
      transition={{
        duration: speed,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
}
