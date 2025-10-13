import React from 'react';
import { motion } from 'motion/react';

interface FloatingElementsProps {
  count?: number;
  className?: string;
}

export function FloatingElements({ count = 8, className = '' }: FloatingElementsProps) {
  const elements = Array.from({ length: count });

  const getRandomValues = () => ({
    x: Math.random() * 100,
    y: Math.random() * 100,
    size: Math.random() * 100 + 50,
    duration: Math.random() * 20 + 15,
    delay: Math.random() * 5,
    opacity: Math.random() * 0.1 + 0.05,
    blur: Math.random() * 3 + 1,
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
              y: [0, -30, 0],
              x: [0, 15, -15, 0],
              scale: [1, 1.1, 0.9, 1],
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
