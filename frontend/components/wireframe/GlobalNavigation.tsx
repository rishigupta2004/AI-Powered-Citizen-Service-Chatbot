import React from 'react';
import { WireframeBox } from './WireframeBox';
import { WireframeIcon } from './WireframeIcon';
import { WireframeButton } from './WireframeButton';
import { Annotation } from './Annotation';

interface GlobalNavigationProps {
  onNavigate: (page: string) => void;
  currentPage: string;
}

export function GlobalNavigation({ onNavigate, currentPage }: GlobalNavigationProps) {
  const navItems = ['Home', 'Services', 'About Us', 'FAQ', 'Docs', 'Admin'];

  return (
    <nav className="border-b-2 border-gray-400 bg-white sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          {/* Logo */}
          <div className="relative">
            <WireframeBox label="LOGO" height="h-12" width="w-32" variant="filled" />
            <Annotation type="interaction" text="Click to return home" position="bottom" />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6 flex-1 justify-center">
            {navItems.map((item) => (
              <button
                key={item}
                onClick={() => onNavigate(item.toLowerCase())}
                className={`text-sm uppercase tracking-wider px-3 py-2 border-b-2 ${
                  currentPage === item.toLowerCase() 
                    ? 'border-gray-900' 
                    : 'border-transparent hover:border-gray-400'
                }`}
              >
                {item}
              </button>
            ))}
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-3">
            {/* Search */}
            <div className="hidden lg:block relative">
              <WireframeBox label="SEARCH" height="h-10" width="w-48" variant="outline" />
              <Annotation type="action" text="Open search modal" position="bottom" />
            </div>

            {/* Language Picker */}
            <div className="relative">
              <WireframeBox label="EN ▼" height="h-10" width="w-20" variant="outline" />
              <Annotation type="action" text="Language picker dropdown" position="bottom" />
            </div>

            {/* High Contrast Toggle */}
            <div className="relative">
              <button className="w-10 h-10 border-2 border-gray-600 flex items-center justify-center hover:bg-gray-100">
                <span className="text-xs">◐</span>
              </button>
              <Annotation type="action" text="High contrast toggle" position="bottom" />
            </div>

            {/* Mobile Menu Toggle */}
            <div className="md:hidden relative">
              <WireframeBox label="☰" height="h-10" width="w-10" variant="filled" />
              <Annotation type="action" text="Open mobile menu" position="bottom" />
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
