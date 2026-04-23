import React, { useState } from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { Annotation } from '../wireframe/Annotation';

export function ResponsiveShowcase() {
  const [selectedPage, setSelectedPage] = useState('home');

  const pages = [
    { id: 'home', name: 'Homepage' },
    { id: 'service', name: 'Service Detail' },
    { id: 'faq', name: 'FAQ' },
    { id: 'admin', name: 'Admin Portal' }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="max-w-7xl mx-auto px-4 py-8 text-center">
        <div className="h-12 w-96 mx-auto border-4 border-gray-900 mb-4 relative">
          <Annotation type="state" text="Responsive Layouts Overview" position="top" />
        </div>
        <div className="h-4 w-[600px] mx-auto border border-gray-400"></div>
      </section>

      {/* Page Selector */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="flex gap-3 justify-center flex-wrap">
          {pages.map((page) => (
            <button
              key={page.id}
              onClick={() => setSelectedPage(page.id)}
              className={`px-6 py-3 border-2 ${
                selectedPage === page.id
                  ? 'border-gray-900 bg-gray-900 text-white'
                  : 'border-gray-400 hover:border-gray-600'
              }`}
            >
              {page.name.toUpperCase()}
            </button>
          ))}
        </div>
      </section>

      {/* Responsive Frames Display */}
      <section className="max-w-7xl mx-auto px-4 space-y-16">
        {/* Desktop Frame */}
        <div className="relative">
          <Annotation type="state" text="Desktop layout (full width)" position="right" />
          <div className="mb-6 text-center">
            <div className="inline-block px-6 py-2 border-2 border-gray-900 bg-gray-900 text-white">
              🖥️ DESKTOP VIEW
            </div>
          </div>
          <div className="border-4 border-gray-900 p-8 bg-white">
            {/* Desktop Layout Structure */}
            <div className="space-y-6">
              {/* Navigation */}
              <div className="h-16 border-2 border-gray-400 flex items-center px-6 gap-8">
                <WireframeBox label="LOGO" height="h-10" width="w-24" variant="filled" />
                <div className="flex gap-6 flex-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className="h-4 w-16 border border-gray-400"></div>
                  ))}
                </div>
                <WireframeBox label="SEARCH" height="h-8" width="w-32" variant="outline" />
              </div>

              {/* Hero/Content */}
              <div className="grid grid-cols-2 gap-8">
                <div className="space-y-4">
                  <div className="h-12 border-2 border-gray-900"></div>
                  <div className="space-y-2">
                    <div className="h-4 border border-gray-400"></div>
                    <div className="h-4 border border-gray-400"></div>
                    <div className="h-4 w-2/3 border border-gray-400"></div>
                  </div>
                  <div className="flex gap-3">
                    <div className="h-10 w-32 border-2 border-gray-900 bg-gray-900"></div>
                    <div className="h-10 w-32 border-2 border-gray-400"></div>
                  </div>
                </div>
                <WireframeBox label="IMAGE/CONTENT" height="h-64" variant="filled" />
              </div>

              {/* Cards Grid */}
              <div className="grid grid-cols-3 gap-6 mt-8">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="border-2 border-gray-400 p-6 space-y-3">
                    <WireframeBox label={`CARD ${i}`} height="h-32" variant="filled" />
                    <div className="h-4 border border-gray-700"></div>
                    <div className="h-3 border border-gray-400"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Tablet Frame */}
        <div className="relative">
          <Annotation type="state" text="Tablet layout (768px)" position="right" />
          <div className="mb-6 text-center">
            <div className="inline-block px-6 py-2 border-2 border-gray-900 bg-gray-900 text-white">
              📱 TABLET VIEW (768px)
            </div>
          </div>
          <div className="max-w-3xl mx-auto border-4 border-gray-900 p-6 bg-white">
            {/* Tablet Layout Structure */}
            <div className="space-y-6">
              {/* Navigation */}
              <div className="h-14 border-2 border-gray-400 flex items-center px-4 gap-4">
                <WireframeBox label="LOGO" height="h-8" width="w-20" variant="filled" />
                <div className="flex gap-4 flex-1">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-3 w-12 border border-gray-400"></div>
                  ))}
                </div>
                <div className="h-8 w-8 border border-gray-600">☰</div>
              </div>

              {/* Hero/Content */}
              <div className="space-y-4">
                <div className="h-10 border-2 border-gray-900"></div>
                <div className="space-y-2">
                  <div className="h-3 border border-gray-400"></div>
                  <div className="h-3 border border-gray-400"></div>
                </div>
                <WireframeBox label="IMAGE/CONTENT" height="h-48" variant="filled" />
                <div className="flex gap-2">
                  <div className="h-8 flex-1 border-2 border-gray-900 bg-gray-900"></div>
                  <div className="h-8 flex-1 border-2 border-gray-400"></div>
                </div>
              </div>

              {/* Cards Grid */}
              <div className="grid grid-cols-2 gap-4 mt-6">
                {[1, 2].map((i) => (
                  <div key={i} className="border-2 border-gray-400 p-4 space-y-2">
                    <WireframeBox label={`CARD ${i}`} height="h-24" variant="filled" />
                    <div className="h-3 border border-gray-700"></div>
                    <div className="h-2 border border-gray-400"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Mobile Frame */}
        <div className="relative">
          <Annotation type="state" text="Mobile layout (375px)" position="right" />
          <div className="mb-6 text-center">
            <div className="inline-block px-6 py-2 border-2 border-gray-900 bg-gray-900 text-white">
              📱 MOBILE VIEW (375px)
            </div>
          </div>
          <div className="max-w-sm mx-auto border-4 border-gray-900 p-4 bg-white">
            {/* Mobile Layout Structure */}
            <div className="space-y-4">
              {/* Navigation */}
              <div className="h-12 border-2 border-gray-400 flex items-center px-3 justify-between">
                <div className="h-6 w-6 border border-gray-600">☰</div>
                <WireframeBox label="LOGO" height="h-6" width="w-16" variant="filled" />
                <div className="h-6 w-6 border border-gray-600">🔍</div>
              </div>

              {/* Hero/Content */}
              <div className="space-y-3">
                <div className="h-8 border-2 border-gray-900"></div>
                <div className="space-y-2">
                  <div className="h-3 border border-gray-400"></div>
                  <div className="h-3 border border-gray-400"></div>
                </div>
                <WireframeBox label="IMAGE/CONTENT" height="h-40" variant="filled" />
                <div className="space-y-2">
                  <div className="h-10 border-2 border-gray-900 bg-gray-900"></div>
                  <div className="h-10 border-2 border-gray-400"></div>
                </div>
              </div>

              {/* Cards Stack */}
              <div className="space-y-3 mt-4">
                {[1, 2].map((i) => (
                  <div key={i} className="border-2 border-gray-400 p-3 space-y-2">
                    <WireframeBox label={`CARD ${i}`} height="h-20" variant="filled" />
                    <div className="h-3 border border-gray-700"></div>
                    <div className="h-2 border border-gray-400"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Layout Adaptation Notes */}
        <div className="bg-gray-50 border-4 border-gray-900 p-8 relative">
          <Annotation type="flow" text="Layout adaptation guidelines" position="right" />
          <div className="h-6 w-64 border-b-2 border-gray-900 mb-6 relative">
            <div className="absolute -bottom-6 left-0 text-xs text-gray-500">
              [RESPONSIVE DESIGN PRINCIPLES]
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            <div className="space-y-3">
              <div className="h-5 w-24 border-b border-gray-700"></div>
              <ul className="space-y-2 text-xs">
                <li>• Full-width layout</li>
                <li>• Multi-column grids</li>
                <li>• Expanded navigation</li>
                <li>• Sidebar visible</li>
                <li>• Large touch targets</li>
              </ul>
            </div>
            <div className="space-y-3">
              <div className="h-5 w-24 border-b border-gray-700"></div>
              <ul className="space-y-2 text-xs">
                <li>• Optimized width</li>
                <li>• 2-column grids</li>
                <li>• Compact navigation</li>
                <li>• Collapsible sidebar</li>
                <li>• Medium touch targets</li>
              </ul>
            </div>
            <div className="space-y-3">
              <div className="h-5 w-24 border-b border-gray-700"></div>
              <ul className="space-y-2 text-xs">
                <li>• Single column</li>
                <li>• Stacked layout</li>
                <li>• Hamburger menu</li>
                <li>• Bottom navigation</li>
                <li>• Large touch targets</li>
              </ul>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
