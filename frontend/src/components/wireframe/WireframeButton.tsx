import React from 'react';

interface WireframeButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  onClick?: () => void;
  className?: string;
}

export function WireframeButton({ 
  label, 
  variant = 'primary', 
  size = 'md',
  onClick,
  className = ''
}: WireframeButtonProps) {
  const variants = {
    primary: 'border-2 border-gray-900 bg-gray-900 text-white',
    secondary: 'border-2 border-gray-600 bg-white text-gray-900',
    ghost: 'border-2 border-gray-400 bg-white text-gray-600'
  };

  const sizes = {
    sm: 'px-3 py-1 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  };

  return (
    <button 
      onClick={onClick}
      className={`${variants[variant]} ${sizes[size]} ${className} uppercase tracking-wider hover:opacity-80 transition-opacity`}
    >
      {label}
    </button>
  );
}
