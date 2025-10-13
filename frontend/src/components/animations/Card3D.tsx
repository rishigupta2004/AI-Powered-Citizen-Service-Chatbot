import React, { useState, useRef, MouseEvent } from 'react';
import { motion } from 'motion/react';

interface Card3DProps {
  children: React.ReactNode;
  className?: string;
  intensity?: number;
  shine?: boolean;
}

export function Card3D({ children, className = '', intensity = 20, shine = true }: Card3DProps) {
  const [rotateX, setRotateX] = useState(0);
  const [rotateY, setRotateY] = useState(0);
  const [isHovering, setIsHovering] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const card = cardRef.current;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateXValue = ((y - centerY) / centerY) * -intensity;
    const rotateYValue = ((x - centerX) / centerX) * intensity;

    setRotateX(rotateXValue);
    setRotateY(rotateYValue);
  };

  const handleMouseEnter = () => {
    setIsHovering(true);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    setRotateX(0);
    setRotateY(0);
  };

  return (
    <motion.div
      ref={cardRef}
      className={`relative ${className}`}
      style={{
        perspective: '1000px',
        transformStyle: 'preserve-3d',
      }}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      animate={{
        rotateX,
        rotateY,
      }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 30,
      }}
    >
      {children}
      {shine && isHovering && (
        <motion.div
          className="absolute inset-0 pointer-events-none overflow-hidden rounded-[inherit]"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovering ? 1 : 0 }}
          transition={{ duration: 0.3 }}
        >
          <div
            className="absolute inset-0"
            style={{
              background: `radial-gradient(600px circle at ${rotateY * 10 + 50}% ${-rotateX * 10 + 50}%, rgba(255,255,255,0.3), transparent 40%)`,
            }}
          />
        </motion.div>
      )}
    </motion.div>
  );
}
