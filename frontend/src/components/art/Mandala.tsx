import React, { useEffect, useRef } from 'react';
import { animate } from 'animejs';

export function Mandala({ className = "", size = 200 }: { className?: string, size?: number }) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const layers = containerRef.current.querySelectorAll('.mandala-layer');
    
    animate({
      targets: layers,
      rotateZ: [
        { value: 360, duration: 20000, easing: 'linear' },
      ],
      loop: true,
      delay: anime.stagger(200, {start: 0})
    });

    animate({
      targets: '.mandala-pulse',
      scale: [1, 1.05, 1],
      opacity: [0.5, 1, 0.5],
      duration: 3000,
      loop: true,
      easing: 'easeInOutSine'
    });
  }, []);

  return (
    <div ref={containerRef} className={`relative flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
      {/* Outer Glow */}
      <div className="absolute inset-0 rounded-full bg-saffron/20 blur-3xl mandala-pulse"></div>
      
      {/* Outer Ring */}
      <svg className="absolute mandala-layer opacity-40 text-saffron" viewBox="0 0 100 100" style={{ width: '100%', height: '100%' }}>
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="0.5" strokeDasharray="2 4" />
        {[...Array(12)].map((_, i) => (
          <path key={`outer-${i}`} d="M 50 2 C 55 10, 45 10, 50 20" fill="none" stroke="currentColor" strokeWidth="0.5" 
                transform={`rotate(${i * 30} 50 50)`} />
        ))}
      </svg>

      {/* Middle Ring */}
      <svg className="absolute mandala-layer opacity-60 text-white" viewBox="0 0 100 100" style={{ width: '75%', height: '75%' }}>
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="1" />
        {[...Array(8)].map((_, i) => (
          <path key={`mid-${i}`} d="M 50 2 Q 60 25, 50 48 Q 40 25, 50 2" fill="none" stroke="currentColor" strokeWidth="1" 
                transform={`rotate(${i * 45} 50 50)`} />
        ))}
      </svg>

      {/* Inner Star/Lotus */}
      <svg className="absolute mandala-layer text-green" viewBox="0 0 100 100" style={{ width: '50%', height: '50%' }}>
        <circle cx="50" cy="50" r="48" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="1 2" />
        {[...Array(16)].map((_, i) => (
          <line key={`inner-${i}`} x1="50" y1="2" x2="50" y2="48" stroke="currentColor" strokeWidth="1" 
                transform={`rotate(${i * 22.5} 50 50)`} />
        ))}
        <circle cx="50" cy="50" r="10" fill="currentColor" className="mandala-pulse" />
      </svg>
    </div>
  );
}
