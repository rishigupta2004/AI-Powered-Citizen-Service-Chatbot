import React from 'react';

interface WireframeIconProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  label?: string;
}

export function WireframeIcon({ size = 'md', label }: WireframeIconProps) {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  return (
    <div className={`${sizes[size]} border-2 border-gray-400 rounded-full flex items-center justify-center bg-white`}>
      {label && <span className="text-[8px] text-gray-500">{label}</span>}
    </div>
  );
}
