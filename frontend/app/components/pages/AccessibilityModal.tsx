import React, { useState } from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { WireframeButton } from '../wireframe/WireframeButton';
import { WireframeIcon } from '../wireframe/WireframeIcon';
import { Annotation } from '../wireframe/Annotation';

interface AccessibilityModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AccessibilityModal({ isOpen, onClose }: AccessibilityModalProps) {
  const [fontSize, setFontSize] = useState(100);
  const [colorMode, setColorMode] = useState('normal');
  const [language, setLanguage] = useState('en');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white border-4 border-gray-900 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative">
        <Annotation type="state" text="Accessibility & Language Settings popup/panel" position="right" />
        
        {/* Header */}
        <div className="p-6 border-b-2 border-gray-400 flex items-center justify-between sticky top-0 bg-white z-10">
          <div className="flex items-center gap-3">
            <WireframeIcon size="lg" label="⚙️" />
            <div className="h-6 w-64 border-b-2 border-gray-900 relative">
              <div className="absolute -bottom-6 left-0 text-xs text-gray-500">
                [ACCESSIBILITY & LANGUAGE SETTINGS]
              </div>
            </div>
          </div>
          <button onClick={onClose} className="text-2xl hover:opacity-70">×</button>
        </div>

        <div className="p-6 space-y-8">
          {/* Font Size Adjustment */}
          <div className="space-y-4 relative">
            <Annotation type="action" text="Adjust font size" position="right" />
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <div className="flex items-center justify-between mb-2">
              <div className="h-4 w-24 border border-gray-600"></div>
              <div className="h-6 w-16 border-2 border-gray-900 text-center text-xs">
                {fontSize}%
              </div>
            </div>
            <div className="relative">
              <div className="h-2 w-full border-2 border-gray-400 bg-gray-100 relative">
                <div
                  className="absolute h-4 w-4 bg-gray-900 border-2 border-gray-900 top-1/2 -translate-y-1/2 cursor-pointer"
                  style={{ left: `${fontSize - 50}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-xs mt-2">
                <span>50%</span>
                <span>100%</span>
                <span>200%</span>
              </div>
            </div>
          </div>

          {/* Color Mode */}
          <div className="space-y-4 relative">
            <Annotation type="action" text="Color mode (normal/high contrast)" position="right" />
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <div className="grid grid-cols-3 gap-4">
              {[
                { id: 'normal', label: 'Normal' },
                { id: 'high', label: 'High Contrast' },
                { id: 'dark', label: 'Dark Mode' }
              ].map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => setColorMode(mode.id)}
                  className={`p-4 border-2 text-center ${
                    colorMode === mode.id
                      ? 'border-gray-900 bg-gray-100'
                      : 'border-gray-400 hover:border-gray-600'
                  }`}
                >
                  <div className="h-12 w-12 mx-auto border border-gray-600 mb-2 bg-white"></div>
                  <div className="text-xs uppercase">{mode.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Language Dropdown */}
          <div className="space-y-4 relative">
            <Annotation type="action" text="Language dropdown" position="right" />
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <div className="space-y-2">
              <div className="h-4 w-24 border border-gray-600"></div>
              <div className="relative">
                <WireframeBox label="ENGLISH ▼" height="h-12" variant="outline" />
                <div className="absolute top-full left-0 right-0 mt-1 border-2 border-gray-400 bg-white shadow-lg hidden hover:block">
                  {['English', 'Hindi', 'Tamil', 'Bengali', 'Telugu'].map((lang) => (
                    <div key={lang} className="p-3 border-b border-gray-300 hover:bg-gray-100 cursor-pointer">
                      <div className="h-3 w-24 border border-gray-600"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Additional Settings */}
          <div className="space-y-4">
            <div className="h-5 w-48 border-b border-gray-700"></div>
            {[
              'Screen Reader Support',
              'Keyboard Navigation',
              'Reduce Motion',
              'Underline Links'
            ].map((setting, i) => (
              <div key={i} className="flex items-center justify-between p-3 border border-gray-400 hover:bg-gray-50">
                <div className="h-4 w-48 border border-gray-600"></div>
                <div className="w-12 h-6 border-2 border-gray-600 rounded-full relative">
                  <div className="w-4 h-4 bg-gray-600 rounded-full absolute top-0.5 left-0.5"></div>
                </div>
              </div>
            ))}
          </div>

          {/* Accessibility Info/Help Section */}
          <div className="border-t-2 border-gray-400 pt-6 space-y-4 relative">
            <Annotation type="flow" text="Accessibility info/help section" position="right" />
            <div className="h-5 w-48 border-b border-gray-700"></div>
            <div className="bg-gray-50 border border-gray-400 p-4 space-y-2">
              <div className="flex items-start gap-3">
                <WireframeIcon size="sm" label="ℹ️" />
                <div className="flex-1 space-y-2">
                  <div className="h-3 w-full border border-gray-600"></div>
                  <div className="h-3 w-full border border-gray-600"></div>
                  <div className="h-3 w-2/3 border border-gray-600"></div>
                </div>
              </div>
            </div>
            <div className="flex gap-3">
              <WireframeButton label="LEARN MORE" variant="ghost" size="sm" />
              <WireframeButton label="KEYBOARD SHORTCUTS" variant="ghost" size="sm" />
            </div>
          </div>

          {/* Feedback Form Box */}
          <div className="border-t-2 border-gray-400 pt-6 space-y-4 relative">
            <Annotation type="action" text="Feedback form box" position="right" />
            <div className="h-5 w-48 border-b border-gray-700 relative">
              <div className="absolute -bottom-6 left-0 text-xs text-gray-500">
                [ACCESSIBILITY FEEDBACK]
              </div>
            </div>
            <div className="space-y-3 mt-4">
              <div className="space-y-2">
                <div className="h-4 w-32 border border-gray-600"></div>
                <WireframeBox label="YOUR FEEDBACK..." height="h-24" variant="outline" />
              </div>
              <div className="space-y-2">
                <div className="h-4 w-32 border border-gray-600"></div>
                <WireframeBox label="EMAIL (OPTIONAL)" height="h-12" variant="outline" />
              </div>
              <WireframeButton label="SUBMIT FEEDBACK" variant="secondary" />
            </div>
          </div>

          {/* Actions */}
          <div className="border-t-2 border-gray-400 pt-6 flex items-center justify-between">
            <WireframeButton label="RESET TO DEFAULT" variant="ghost" />
            <div className="flex gap-3">
              <WireframeButton label="CANCEL" variant="secondary" onClick={onClose} />
              <WireframeButton label="SAVE SETTINGS" variant="primary" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
