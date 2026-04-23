import React from 'react';

interface AnnotationProps {
  type: 'flow' | 'action' | 'state' | 'interaction';
  text: string;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

export function Annotation({ type, text, position = 'right' }: AnnotationProps) {
  const colors = {
    flow: 'border-gray-400 bg-gray-50',
    action: 'border-gray-500 bg-gray-100',
    state: 'border-gray-600 bg-gray-200',
    interaction: 'border-gray-400 bg-gray-50'
  };

  const positions = {
    top: '-top-8 left-1/2 -translate-x-1/2',
    bottom: '-bottom-8 left-1/2 -translate-x-1/2',
    left: 'right-full mr-2 top-1/2 -translate-y-1/2',
    right: 'left-full ml-2 top-1/2 -translate-y-1/2'
  };

  return (
    <div className={`absolute ${positions[position]} z-50 pointer-events-none`}>
      <div className={`border-2 ${colors[type]} px-2 py-1 text-xs whitespace-nowrap rounded shadow-sm`}>
        <span className="uppercase mr-1">[{type}]</span>
        {text}
      </div>
    </div>
  );
}
