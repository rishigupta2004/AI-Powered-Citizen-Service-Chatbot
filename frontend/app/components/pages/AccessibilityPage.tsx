import React, { useState } from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { WireframeButton } from '../wireframe/WireframeButton';
import { WireframeIcon } from '../wireframe/WireframeIcon';
import { Annotation } from '../wireframe/Annotation';

export function AccessibilityPage() {
  const [fontSize, setFontSize] = useState(100);
  const [contrast, setContrast] = useState('normal');
  const [screenReader, setScreenReader] = useState(false);

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="max-w-7xl mx-auto px-4 py-8">
        <div className="h-12 w-96 border-2 border-gray-900 mb-4"></div>
        <div className="space-y-2">
          <div className="h-4 w-[600px] border border-gray-400"></div>
          <div className="h-4 w-[500px] border border-gray-400"></div>
        </div>
      </section>

      {/* Quick Settings Panel */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="border-4 border-gray-900 bg-gray-50 p-8 relative">
          <Annotation type="flow" text="Quick accessibility controls" position="right" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { label: 'Font Size', icon: 'A+' },
              { label: 'Contrast', icon: '◐' },
              { label: 'Screen Reader', icon: '♿' },
              { label: 'Keyboard Nav', icon: '⌨' }
            ].map((setting, i) => (
              <div key={i} className="text-center space-y-3">
                <WireframeIcon size="xl" label={setting.icon} />
                <div className="h-4 w-32 mx-auto border border-gray-600"></div>
                <WireframeButton label="TOGGLE" variant="secondary" size="sm" />
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Detailed Settings */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Settings */}
          <div className="lg:col-span-2 space-y-6">
            {/* Visual Settings */}
            <div className="border-2 border-gray-400 p-6 relative">
              <Annotation type="interaction" text="Adjustable controls" position="right" />
              <div className="h-6 w-48 border-b-2 border-gray-900 mb-6"></div>
              
              {/* Font Size */}
              <div className="space-y-4 mb-8">
                <div className="flex items-center justify-between">
                  <div className="h-4 w-32 border border-gray-600"></div>
                  <div className="h-6 w-16 border-2 border-gray-900 text-center">{fontSize}%</div>
                </div>
                <div className="relative">
                  <Annotation type="state" text="Slider control" position="bottom" />
                  <div className="h-2 w-full border-2 border-gray-400 bg-gray-100 relative">
                    <div
                      className="absolute h-4 w-4 bg-gray-900 border-2 border-gray-900 top-1/2 -translate-y-1/2"
                      style={{ left: `${fontSize - 50}%` }}
                    ></div>
                  </div>
                  <div className="flex justify-between text-xs mt-2">
                    <span>50%</span>
                    <span>100%</span>
                    <span>150%</span>
                  </div>
                </div>
              </div>

              {/* Contrast Mode */}
              <div className="space-y-4 mb-8">
                <div className="h-4 w-32 border border-gray-600"></div>
                <div className="grid grid-cols-3 gap-3 relative">
                  <Annotation type="action" text="Select contrast mode" position="bottom" />
                  {['Normal', 'High', 'Inverse'].map((mode) => (
                    <button
                      key={mode}
                      onClick={() => setContrast(mode.toLowerCase())}
                      className={`p-4 border-2 ${
                        contrast === mode.toLowerCase()
                          ? 'border-gray-900 bg-gray-100'
                          : 'border-gray-400'
                      }`}
                    >
                      <div className="h-4 w-full border border-gray-600 mx-auto mb-2"></div>
                      <div className="text-xs">{mode.toUpperCase()}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Color Blindness */}
              <div className="space-y-4">
                <div className="h-4 w-32 border border-gray-600"></div>
                <div className="space-y-2">
                  {['None', 'Protanopia', 'Deuteranopia', 'Tritanopia'].map((type) => (
                    <div key={type} className="flex items-center gap-3 p-3 border border-gray-400 hover:bg-gray-50 cursor-pointer">
                      <div className="w-5 h-5 border-2 border-gray-600 rounded-full"></div>
                      <div className="h-4 w-32 border border-gray-600"></div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Navigation Settings */}
            <div className="border-2 border-gray-400 p-6">
              <div className="h-6 w-48 border-b-2 border-gray-900 mb-6"></div>
              
              <div className="space-y-6">
                {/* Toggle Options */}
                {[
                  'Keyboard Navigation Highlights',
                  'Skip to Content Links',
                  'Focus Indicators',
                  'Reading Guide',
                  'Link Underlines'
                ].map((option, i) => (
                  <div key={i} className="flex items-center justify-between p-3 border border-gray-400 hover:bg-gray-50 relative">
                    {i === 0 && <Annotation type="interaction" text="Toggle on/off" position="right" />}
                    <div className="h-4 w-48 border border-gray-600"></div>
                    <div className="w-12 h-6 border-2 border-gray-600 rounded-full relative">
                      <div className="w-4 h-4 bg-gray-600 rounded-full absolute top-0.5 left-0.5"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Audio Settings */}
            <div className="border-2 border-gray-400 p-6">
              <div className="h-6 w-48 border-b-2 border-gray-900 mb-6"></div>
              
              <div className="space-y-6">
                {/* Screen Reader */}
                <div className="flex items-center justify-between p-4 bg-gray-50 border-2 border-gray-500">
                  <div className="flex items-center gap-3">
                    <WireframeIcon size="md" label="🔊" />
                    <div className="h-4 w-32 border border-gray-700"></div>
                  </div>
                  <div className="w-12 h-6 border-2 border-gray-900 rounded-full bg-gray-900 relative">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-0.5 right-0.5"></div>
                  </div>
                </div>

                {/* Audio Description */}
                <div className="space-y-3">
                  <div className="h-4 w-32 border border-gray-600"></div>
                  <div className="flex gap-3">
                    <WireframeButton label="TEST AUDIO" variant="secondary" size="sm" />
                    <WireframeButton label="CONFIGURE" variant="ghost" size="sm" />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar - Preview & Help */}
          <div className="space-y-6">
            {/* Live Preview */}
            <div className="border-2 border-gray-400 p-6 relative">
              <Annotation type="state" text="Live preview of settings" position="left" />
              <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
              <WireframeBox label="PREVIEW AREA" height="h-64" variant="filled" />
              <div className="mt-4 text-center">
                <WireframeButton label="RESET TO DEFAULT" variant="ghost" size="sm" />
              </div>
            </div>

            {/* Keyboard Shortcuts */}
            <div className="border-2 border-gray-400 p-6 relative">
              <Annotation type="flow" text="Keyboard shortcuts reference" position="left" />
              <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="h-4 w-20 border border-gray-600"></div>
                    <div className="h-4 w-24 border border-gray-500 bg-gray-50"></div>
                  </div>
                ))}
              </div>
              <div className="mt-4">
                <WireframeButton label="VIEW ALL" variant="ghost" size="sm" />
              </div>
            </div>

            {/* Resources */}
            <div className="border-2 border-gray-400 p-6">
              <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
              <div className="space-y-3">
                {['Guide', 'Tutorial', 'Support'].map((link) => (
                  <div key={link} className="flex items-center gap-2 p-2 border border-gray-400 hover:bg-gray-50 cursor-pointer">
                    <WireframeIcon size="sm" label="→" />
                    <div className="h-3 w-24 border border-gray-600"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Save Settings */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="border-t-2 border-gray-400 pt-8 flex items-center justify-between relative">
          <Annotation type="state" text="Settings persist across sessions" position="right" />
          <div className="flex items-center gap-3">
            <WireframeIcon size="sm" label="✓" />
            <div className="h-4 w-48 border border-gray-600"></div>
          </div>
          <div className="flex gap-3">
            <WireframeButton label="RESET ALL" variant="ghost" />
            <WireframeButton label="SAVE SETTINGS" variant="primary" />
          </div>
        </div>
      </section>
    </div>
  );
}
