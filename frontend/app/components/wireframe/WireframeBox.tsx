import React from 'react';

interface WireframeBoxProps {
  label?: string;
  height?: string;
  width?: string;
  variant?: 'outline' | 'filled' | 'dashed';
  children?: React.ReactNode;
  className?: string;
}

export function WireframeBox({ 
  label, 
  height = 'h-32', 
  width = 'w-full', 
  variant = 'outline',
  children,
  className = ''
}: WireframeBoxProps) {
  const variants = {
    outline: 'border-2 border-gray-400',
    filled: 'border-2 border-gray-400 bg-gray-100',
    dashed: 'border-2 border-dashed border-gray-300'
  };

  return (
    <div className={`${variants[variant]} ${height} ${width} ${className} flex items-center justify-center relative`}>
      {label && (
        <span className="text-xs text-gray-500 uppercase tracking-wider">{label}</span>
      )}
      {children}
    </div>
  );
}
