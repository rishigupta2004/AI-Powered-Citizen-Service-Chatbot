import React, { useState } from 'react';
import { motion, useMotionValue, useSpring, useTransform } from 'framer-motion';
import { LucideIcon, ArrowRight } from 'lucide-react';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';

interface ServiceCard3DProps {
  icon: LucideIcon;
  name: string;
  description: string;
  badge: string;
  gradient: string;
  processingTime: string;
  fee: string;
  onClick?: () => void;
}

export function ServiceCard3D({
  icon: Icon,
  name,
  description,
  badge,
  gradient,
  processingTime,
  fee,
  onClick,
}: ServiceCard3DProps) {
  const [isHovering, setIsHovering] = useState(false);

  const x = useMotionValue(0);
  const y = useMotionValue(0);

  const mouseXSpring = useSpring(x, { stiffness: 300, damping: 30 });
  const mouseYSpring = useSpring(y, { stiffness: 300, damping: 30 });

  const rotateX = useTransform(mouseYSpring, [-0.5, 0.5], ['12deg', '-12deg']);
  const rotateY = useTransform(mouseXSpring, [-0.5, 0.5], ['-12deg', '12deg']);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const width = rect.width;
    const height = rect.height;
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    const xPct = mouseX / width - 0.5;
    const yPct = mouseY / height - 0.5;
    x.set(xPct);
    y.set(yPct);
  };

  const handleMouseLeave = () => {
    setIsHovering(false);
    x.set(0);
    y.set(0);
  };

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovering(true)}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{
        rotateX,
        rotateY,
        transformStyle: 'preserve-3d',
        perspective: '1000px',
      }}
      className="relative cursor-pointer group"
      whileHover={{ scale: 1.05 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
    >
      {/* Glowing shadow */}
      <motion.div
        className={`absolute -inset-1 bg-gradient-to-br ${gradient} rounded-[var(--radius-2xl)] blur-xl opacity-0 group-hover:opacity-60 transition-opacity`}
        style={{
          transform: 'translateZ(-50px)',
        }}
      />

      {/* Card container */}
      <div
        className="relative bg-[var(--card)] rounded-[var(--radius-2xl)] border-2 border-[var(--card-border)] overflow-hidden shadow-[var(--shadow-8)] group-hover:shadow-[var(--shadow-24)] transition-shadow"
        style={{
          transform: 'translateZ(0px)',
        }}
      >
        {/* Header with icon */}
        <div className="relative p-6 overflow-hidden">
          {/* Background gradient */}
          <div
            className={`absolute inset-0 bg-gradient-to-br ${gradient} opacity-10`}
            style={{
              transform: 'translateZ(-10px)',
            }}
          />

          {/* Badge */}
          <div className="absolute top-4 right-4" style={{ transform: 'translateZ(20px)' }}>
            <Badge className="bg-white text-[var(--primary)] shadow-[var(--shadow-4)]">
              {badge}
            </Badge>
          </div>

          {/* 3D Icon */}
          <motion.div
            className={`relative w-24 h-24 bg-gradient-to-br ${gradient} rounded-[var(--radius-2xl)] flex items-center justify-center mb-4 shadow-[var(--shadow-8)]`}
            style={{
              transform: 'translateZ(30px)',
            }}
            animate={{
              rotateY: isHovering ? [0, 360] : 0,
            }}
            transition={{
              duration: 0.8,
              ease: 'easeOut',
            }}
          >
            <Icon className="w-12 h-12 text-white" />
            {/* Icon shadow */}
            <div className="absolute inset-0 bg-black/20 rounded-[inherit] blur-md" style={{ transform: 'translateZ(-5px)' }} />
          </motion.div>

          {/* Title */}
          <h3
            className="text-xl font-bold text-[var(--foreground)] mb-2"
            style={{ transform: 'translateZ(10px)' }}
          >
            {name}
          </h3>
        </div>

        {/* Content */}
        <div className="px-6 pb-6 space-y-4">
          <p
            className="text-[var(--muted-foreground)] text-sm min-h-[3rem]"
            style={{ transform: 'translateZ(5px)' }}
          >
            {description}
          </p>

          {/* Info */}
          <div className="space-y-2" style={{ transform: 'translateZ(5px)' }}>
            <div className="flex items-center justify-between text-sm">
              <span className="text-[var(--muted-foreground)]">Processing:</span>
              <span className="font-medium text-[var(--foreground)]">{processingTime}</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-[var(--muted-foreground)]">Fee:</span>
              <span className="font-medium text-[var(--foreground)]">{fee}</span>
            </div>
          </div>

          {/* CTA Button */}
          <Button
            className={`w-full bg-gradient-to-r ${gradient} hover:opacity-90 transition-opacity shadow-[var(--shadow-4)] group/btn`}
            style={{ transform: 'translateZ(15px)' }}
          >
            View Details
            <ArrowRight className="w-4 h-4 ml-2 group-hover/btn:translate-x-1 transition-transform" />
          </Button>
        </div>

        {/* Shine overlay */}
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: useTransform(
              [mouseXSpring, mouseYSpring],
              ([xVal, yVal]) =>
                `radial-gradient(600px circle at ${(xVal as number + 0.5) * 100}% ${(yVal as number + 0.5) * 100}%, rgba(255,255,255,0.15), transparent 40%)`
            ),
            transform: 'translateZ(40px)',
          }}
        />
      </div>
    </motion.div>
  );
}
