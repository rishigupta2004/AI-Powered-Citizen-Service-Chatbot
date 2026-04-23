import React, { useState } from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { WireframeButton } from '../wireframe/WireframeButton';
import { WireframeIcon } from '../wireframe/WireframeIcon';
import { Annotation } from '../wireframe/Annotation';

export function UIStatesPage() {
  const [activeState, setActiveState] = useState<'loading' | 'error' | 'success' | 'empty' | 'offline'>('loading');

  return (
    <div className="space-y-8">
      {/* Header */}
      <section className="max-w-7xl mx-auto px-4 py-8">
        <div className="h-12 w-96 border-2 border-gray-900 mb-4"></div>
        <div className="h-4 w-[600px] border border-gray-400"></div>
      </section>

      {/* State Selector */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="interaction" text="Toggle between states" position="top" />
        <div className="flex gap-3 flex-wrap justify-center p-6 bg-gray-50 border-2 border-gray-400">
          {[
            { id: 'loading', label: 'Loading State' },
            { id: 'error', label: 'Error State' },
            { id: 'success', label: 'Success State' },
            { id: 'empty', label: 'Empty State' },
            { id: 'offline', label: 'Offline State' }
          ].map((state) => (
            <button
              key={state.id}
              onClick={() => setActiveState(state.id as any)}
              className={`px-6 py-3 border-2 ${
                activeState === state.id
                  ? 'border-gray-900 bg-gray-900 text-white'
                  : 'border-gray-400 hover:border-gray-600'
              }`}
            >
              {state.label.toUpperCase()}
            </button>
          ))}
        </div>
      </section>

      {/* State Demonstrations */}
      <section className="max-w-7xl mx-auto px-4">
        {/* Loading State */}
        {activeState === 'loading' && (
          <div className="space-y-8">
            <div className="text-center mb-8 relative">
              <Annotation type="state" text="Loading indicators" position="right" />
              <div className="h-8 w-48 mx-auto border-b-2 border-gray-900"></div>
            </div>

            {/* Spinner Loading */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="border-2 border-gray-400 p-8 text-center space-y-4">
                <div className="h-5 w-32 mx-auto border-b border-gray-700 mb-4"></div>
                <div className="w-16 h-16 border-4 border-gray-400 border-t-gray-900 rounded-full mx-auto animate-spin"></div>
                <div className="h-3 w-24 mx-auto border border-gray-500"></div>
              </div>

              <div className="border-2 border-gray-400 p-8 text-center space-y-4">
                <div className="h-5 w-32 mx-auto border-b border-gray-700 mb-4"></div>
                <div className="flex gap-2 justify-center">
                  <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce"></div>
                  <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-3 h-3 bg-gray-900 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <div className="h-3 w-24 mx-auto border border-gray-500"></div>
              </div>

              <div className="border-2 border-gray-400 p-8 text-center space-y-4">
                <div className="h-5 w-32 mx-auto border-b border-gray-700 mb-4"></div>
                <div className="w-full h-2 bg-gray-200 border border-gray-400 rounded overflow-hidden">
                  <div className="h-full w-1/2 bg-gray-900 animate-pulse"></div>
                </div>
                <div className="h-3 w-24 mx-auto border border-gray-500"></div>
              </div>
            </div>

            {/* Skeleton Loading */}
            <div className="border-2 border-gray-400 p-6 space-y-6 relative">
              <Annotation type="state" text="Skeleton loading placeholders" position="right" />
              <div className="h-5 w-48 border-b border-gray-700 mb-4"></div>
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-4 animate-pulse">
                  <div className="w-16 h-16 bg-gray-200 border border-gray-400"></div>
                  <div className="flex-1 space-y-3">
                    <div className="h-4 w-3/4 bg-gray-200 border border-gray-400"></div>
                    <div className="h-3 w-1/2 bg-gray-200 border border-gray-400"></div>
                    <div className="h-3 w-2/3 bg-gray-200 border border-gray-400"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Error State */}
        {activeState === 'error' && (
          <div className="space-y-8">
            <div className="text-center mb-8 relative">
              <Annotation type="state" text="Error handling displays" position="right" />
              <div className="h-8 w-48 mx-auto border-b-2 border-gray-900"></div>
            </div>

            {/* Critical Error */}
            <div className="border-4 border-gray-900 p-12 text-center space-y-6 bg-gray-50 relative">
              <Annotation type="flow" text="Critical error message" position="left" />
              <WireframeIcon size="xl" label="⚠️" />
              <div className="space-y-3">
                <div className="h-8 w-96 mx-auto border-2 border-gray-900"></div>
                <div className="space-y-2">
                  <div className="h-4 w-[500px] mx-auto border border-gray-600"></div>
                  <div className="h-4 w-96 mx-auto border border-gray-600"></div>
                </div>
              </div>
              <div className="flex gap-4 justify-center">
                <WireframeButton label="TRY AGAIN" variant="primary" size="lg" />
                <WireframeButton label="GO HOME" variant="secondary" size="lg" />
              </div>
            </div>

            {/* Inline Error */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="border-2 border-gray-400 p-6 space-y-4">
                <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
                <div className="space-y-3">
                  <div className="space-y-2">
                    <div className="h-4 w-24 border border-gray-600"></div>
                    <WireframeBox label="INPUT FIELD" height="h-12" variant="outline" className="border-red-500" />
                    <div className="flex items-center gap-2 text-xs">
                      <span>⚠</span>
                      <div className="h-3 w-48 border border-red-500"></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="border-2 border-gray-400 p-6 space-y-4">
                <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
                <div className="border-l-4 border-gray-900 bg-gray-50 p-4 space-y-2">
                  <div className="flex items-start gap-3">
                    <WireframeIcon size="sm" label="⚠" />
                    <div className="flex-1 space-y-2">
                      <div className="h-4 w-48 border border-gray-700"></div>
                      <div className="h-3 w-full border border-gray-500"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Error Banner */}
            <div className="border-l-4 border-gray-900 bg-gray-100 p-6 flex items-center justify-between relative">
              <Annotation type="state" text="Dismissible error banner" position="top" />
              <div className="flex items-center gap-4">
                <WireframeIcon size="md" label="⚠" />
                <div className="space-y-2">
                  <div className="h-4 w-64 border border-gray-700"></div>
                  <div className="h-3 w-96 border border-gray-500"></div>
                </div>
              </div>
              <button className="text-xl hover:opacity-70">×</button>
            </div>
          </div>
        )}

        {/* Success State */}
        {activeState === 'success' && (
          <div className="space-y-8">
            <div className="text-center mb-8 relative">
              <Annotation type="state" text="Success confirmations" position="right" />
              <div className="h-8 w-48 mx-auto border-b-2 border-gray-900"></div>
            </div>

            {/* Full Page Success */}
            <div className="border-4 border-gray-900 p-12 text-center space-y-6 bg-gray-50 relative">
              <Annotation type="flow" text="Confirmation page" position="left" />
              <div className="w-24 h-24 border-4 border-gray-900 rounded-full mx-auto flex items-center justify-center">
                <span className="text-4xl">✓</span>
              </div>
              <div className="space-y-3">
                <div className="h-10 w-96 mx-auto border-2 border-gray-900"></div>
                <div className="space-y-2">
                  <div className="h-4 w-[500px] mx-auto border border-gray-600"></div>
                  <div className="h-4 w-96 mx-auto border border-gray-600"></div>
                </div>
              </div>
              <div className="border-2 border-gray-400 p-6 max-w-md mx-auto space-y-3 bg-white">
                <div className="h-4 w-32 border border-gray-600"></div>
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="flex justify-between">
                      <div className="h-3 w-32 border border-gray-500"></div>
                      <div className="h-3 w-24 border border-gray-600"></div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex gap-4 justify-center">
                <WireframeButton label="VIEW DETAILS" variant="primary" size="lg" />
                <WireframeButton label="DONE" variant="secondary" size="lg" />
              </div>
            </div>

            {/* Toast Notifications */}
            <div className="space-y-4 relative">
              <Annotation type="interaction" text="Toast notification examples" position="right" />
              <div className="h-5 w-48 border-b border-gray-700 mb-4"></div>
              {['Success', 'Info', 'Warning'].map((type, i) => (
                <div
                  key={type}
                  className="border-l-4 border-gray-900 bg-white shadow-lg p-4 flex items-center justify-between max-w-md"
                >
                  <div className="flex items-center gap-3">
                    <WireframeIcon size="sm" label={type === 'Success' ? '✓' : type === 'Info' ? 'i' : '⚠'} />
                    <div className="space-y-1">
                      <div className="h-4 w-32 border border-gray-700"></div>
                      <div className="h-3 w-48 border border-gray-500"></div>
                    </div>
                  </div>
                  <button className="text-xl hover:opacity-70">×</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {activeState === 'empty' && (
          <div className="space-y-8">
            <div className="text-center mb-8 relative">
              <Annotation type="state" text="Empty state designs" position="right" />
              <div className="h-8 w-48 mx-auto border-b-2 border-gray-900"></div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {/* No Results */}
              <div className="border-2 border-gray-400 p-12 text-center space-y-6 relative">
                <Annotation type="flow" text="No search results" position="left" />
                <WireframeIcon size="xl" label="🔍" />
                <div className="space-y-3">
                  <div className="h-8 w-64 mx-auto border-2 border-gray-900"></div>
                  <div className="space-y-2">
                    <div className="h-4 w-80 mx-auto border border-gray-600"></div>
                    <div className="h-4 w-64 mx-auto border border-gray-600"></div>
                  </div>
                </div>
                <WireframeButton label="CLEAR SEARCH" variant="secondary" />
              </div>

              {/* No Data */}
              <div className="border-2 border-gray-400 p-12 text-center space-y-6">
                <WireframeIcon size="xl" label="📋" />
                <div className="space-y-3">
                  <div className="h-8 w-64 mx-auto border-2 border-gray-900"></div>
                  <div className="space-y-2">
                    <div className="h-4 w-80 mx-auto border border-gray-600"></div>
                    <div className="h-4 w-64 mx-auto border border-gray-600"></div>
                  </div>
                </div>
                <WireframeButton label="GET STARTED" variant="primary" />
              </div>

              {/* No Notifications */}
              <div className="border-2 border-gray-400 p-12 text-center space-y-6">
                <WireframeIcon size="xl" label="🔔" />
                <div className="space-y-3">
                  <div className="h-8 w-64 mx-auto border-2 border-gray-900"></div>
                  <div className="h-4 w-80 mx-auto border border-gray-600"></div>
                </div>
              </div>

              {/* No Favorites */}
              <div className="border-2 border-gray-400 p-12 text-center space-y-6">
                <WireframeIcon size="xl" label="★" />
                <div className="space-y-3">
                  <div className="h-8 w-64 mx-auto border-2 border-gray-900"></div>
                  <div className="space-y-2">
                    <div className="h-4 w-80 mx-auto border border-gray-600"></div>
                    <div className="h-4 w-64 mx-auto border border-gray-600"></div>
                  </div>
                </div>
                <WireframeButton label="BROWSE SERVICES" variant="secondary" />
              </div>
            </div>
          </div>
        )}

        {/* Offline State */}
        {activeState === 'offline' && (
          <div className="space-y-8">
            <div className="text-center mb-8 relative">
              <Annotation type="state" text="Offline/connectivity issues" position="right" />
              <div className="h-8 w-48 mx-auto border-b-2 border-gray-900"></div>
            </div>

            {/* Full Page Offline */}
            <div className="border-4 border-gray-900 p-12 text-center space-y-6 bg-gray-50 relative">
              <Annotation type="flow" text="No connection page" position="left" />
              <WireframeIcon size="xl" label="📡" />
              <div className="space-y-3">
                <div className="h-10 w-96 mx-auto border-2 border-gray-900"></div>
                <div className="space-y-2">
                  <div className="h-4 w-[500px] mx-auto border border-gray-600"></div>
                  <div className="h-4 w-96 mx-auto border border-gray-600"></div>
                  <div className="h-4 w-[400px] mx-auto border border-gray-600"></div>
                </div>
              </div>
              <div className="flex gap-4 justify-center">
                <WireframeButton label="RETRY CONNECTION" variant="primary" size="lg" />
                <WireframeButton label="VIEW CACHED CONTENT" variant="secondary" size="lg" />
              </div>
            </div>

            {/* Offline Banner */}
            <div className="border-l-4 border-gray-900 bg-gray-100 p-6 flex items-center justify-between sticky top-0 z-40">
              <div className="flex items-center gap-4">
                <WireframeIcon size="md" label="📡" />
                <div className="space-y-2">
                  <div className="h-4 w-64 border border-gray-700"></div>
                  <div className="h-3 w-96 border border-gray-500"></div>
                </div>
              </div>
              <WireframeButton label="RETRY" variant="secondary" size="sm" />
            </div>

            {/* Partial Functionality */}
            <div className="border-2 border-gray-400 p-6 space-y-4">
              <div className="h-5 w-48 border-b border-gray-700 mb-4"></div>
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="border border-gray-400 p-4 opacity-50 relative">
                    <div className="absolute inset-0 bg-gray-100 bg-opacity-50 flex items-center justify-center">
                      <div className="bg-white border-2 border-gray-900 px-4 py-2 text-xs">
                        OFFLINE - NOT AVAILABLE
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="h-4 w-64 border border-gray-600"></div>
                      <div className="h-3 w-full border border-gray-500"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
