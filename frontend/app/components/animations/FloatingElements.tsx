import React from 'react';
import { motion } from 'framer-motion';

interface FloatingElementsProps {
  count?: number;
  className?: string;
}

export function FloatingElements({ count = 8, className = '' }: FloatingElementsProps) {
  const elements = Array.from({ length: count });

  const getRandomValues = () => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 72 + 36,
    duration: Math.random() * 16 + 12,
    delay: Math.random() * 3,
    opacity: Math.random() * 0.08 + 0.04,
    blur: Math.random() * 2 + 0.6,
  });

  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      {elements.map((_, i) => {
        const values = getRandomValues();
        return (
          <motion.div
            key={i}
            className="absolute rounded-full bg-gradient-to-br from-[var(--secondary)] via-[var(--primary)] to-[var(--accent)]"
            style={{
              left: `${values.x}%`,
              top: `${values.y}%`,
              width: `${values.size}px`,
              height: `${values.size}px`,
              opacity: values.opacity,
              filter: `blur(${values.blur}px)`,
            }}
            animate={{
              y: [0, -22, 0],
              x: [0, 10, -10, 0],
              scale: [1, 1.06, 0.94, 1],
            }}
            transition={{
              duration: values.duration,
              repeat: Infinity,
              delay: values.delay,
              ease: 'easeInOut',
            }}
          />
        );
      })}
    </div>
  );
}
