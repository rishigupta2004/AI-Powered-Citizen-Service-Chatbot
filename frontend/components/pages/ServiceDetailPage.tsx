import React, { useState } from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { WireframeButton } from '../wireframe/WireframeButton';
import { WireframeIcon } from '../wireframe/WireframeIcon';
import { Annotation } from '../wireframe/Annotation';

export function ServiceDetailPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [showModal, setShowModal] = useState(false);

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <div className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="flow" text="Breadcrumb navigation" position="left" />
        <div className="flex items-center gap-2">
          {['Home', 'Services', 'Service Name'].map((crumb, i, arr) => (
            <React.Fragment key={i}>
              <div className="h-4 w-20 border border-gray-400 hover:bg-gray-100 cursor-pointer"></div>
              {i < arr.length - 1 && <span className="text-gray-400">/</span>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Hero Header */}
      <section className="max-w-7xl mx-auto px-4">
        <div className="flex flex-col lg:flex-row gap-8">
          <div className="flex-1 space-y-6 relative">
            <Annotation type="state" text="Service title & icon" position="right" />
            <div className="flex items-start gap-4">
              <div className="relative">
                <WireframeIcon size="xl" label="S1" />
                <Annotation type="state" text="Service icon" position="top" />
              </div>
              <div className="flex-1 space-y-3">
                <div className="h-10 w-3/4 border-2 border-gray-900 relative">
                  <Annotation type="state" text="Service title" position="top" />
                </div>
                <div className="space-y-2">
                  <div className="h-4 w-full border border-gray-400"></div>
                  <div className="h-4 w-full border border-gray-400"></div>
                  <div className="h-4 w-2/3 border border-gray-400"></div>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <div className="px-3 py-1 border border-gray-500 text-xs">CATEGORY</div>
              <div className="px-3 py-1 border border-gray-500 text-xs">EST. TIME: 5 DAYS</div>
              <div className="px-3 py-1 border border-gray-500 text-xs">ONLINE</div>
            </div>

            <div className="flex gap-3 relative">
              <Annotation type="action" text="Primary service actions" position="bottom" />
              <WireframeButton label="APPLY NOW" variant="primary" size="lg" onClick={() => setShowModal(true)} />
              <WireframeButton label="SAVE" variant="secondary" />
              <WireframeButton label="SHARE" variant="ghost" />
            </div>
          </div>

          <div className="lg:w-96 space-y-6">
            {/* Contact/Help Sidebar */}
            <div className="border-2 border-gray-400 p-6 space-y-4 relative">
              <Annotation type="flow" text="Sidebar: contact/help" position="left" />
              <div className="h-5 w-32 border-b border-gray-700 mb-4"></div>
              {['Requirements', 'Fees', 'Processing Time', 'Validity'].map((item) => (
                <div key={item} className="space-y-2">
                  <div className="h-4 w-24 border border-gray-600"></div>
                  <div className="h-6 w-full border border-gray-400 bg-gray-50"></div>
                </div>
              ))}
            </div>

            {/* Chat Widget Icon */}
            <div className="border-2 border-gray-400 p-6 text-center space-y-4 relative">
              <Annotation type="action" text="Chat widget icon" position="left" />
              <WireframeIcon size="xl" label="💬" />
              <div className="h-4 w-32 mx-auto border border-gray-600"></div>
              <WireframeButton label="START CHAT" variant="primary" size="sm" />
            </div>
          </div>
        </div>
      </section>

      {/* Tabs Navigation */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="interaction" text="Tab navigation" position="right" />
        <div className="border-b-2 border-gray-400 flex gap-1">
          {['overview', 'requirements', 'process', 'forms', 'faqs'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`px-6 py-3 uppercase text-sm border-2 border-b-0 ${
                activeTab === tab ? 'border-gray-900 bg-white -mb-0.5' : 'border-gray-400 bg-gray-100'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>
      </section>

      {/* Tab Content */}
      <section className="max-w-7xl mx-auto px-4">
        {activeTab === 'overview' && (
          <div className="space-y-8 relative">
            <Annotation type="state" text="Tab content area" position="right" />
            
            {/* Description */}
            <div className="space-y-4">
              <div className="h-6 w-48 border-b-2 border-gray-900"></div>
              <div className="space-y-2">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="h-4 w-full border border-gray-400"></div>
                ))}
              </div>
            </div>

            {/* Benefits Grid */}
            <div>
              <div className="h-6 w-32 border-b-2 border-gray-900 mb-4"></div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="border border-gray-400 p-4 space-y-3">
                    <WireframeIcon size="lg" label={`B${i}`} />
                    <div className="h-4 w-32 border border-gray-600"></div>
                    <div className="space-y-1">
                      <div className="h-3 w-full border border-gray-400"></div>
                      <div className="h-3 w-3/4 border border-gray-400"></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'requirements' && (
          <div className="space-y-6">
            <div className="h-6 w-48 border-b-2 border-gray-900"></div>
            <div className="space-y-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="flex gap-3 border border-gray-400 p-4 relative">
                  {i === 1 && <Annotation type="state" text="Checklist items" position="right" />}
                  <div className="w-5 h-5 border-2 border-gray-600"></div>
                  <div className="flex-1 space-y-2">
                    <div className="h-4 w-64 border border-gray-700"></div>
                    <div className="h-3 w-full border border-gray-400"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'process' && (
          <div className="space-y-8 relative">
            <Annotation type="flow" text="Step-by-step process section (stepper/diagram)" position="left" />
            <div className="h-6 w-64 border-b-2 border-gray-900"></div>
            
            {/* Visual Stepper */}
            <div className="border-2 border-gray-400 p-8 bg-gray-50">
              <div className="flex justify-between items-center relative">
                <Annotation type="interaction" text="Stepper diagram" position="top" />
                {[1, 2, 3, 4, 5].map((step, idx) => (
                  <React.Fragment key={step}>
                    <div className="flex flex-col items-center flex-1">
                      <div className={`w-12 h-12 rounded-full border-4 ${idx === 0 ? 'border-gray-900 bg-gray-900' : 'border-gray-400 bg-white'} text-white flex items-center justify-center text-xl`}>
                        {step}
                      </div>
                      <div className="mt-3 h-4 w-20 border border-gray-600 text-center text-xs">
                        STEP {step}
                      </div>
                    </div>
                    {idx < 4 && (
                      <div className="flex-1 h-1 bg-gray-400 -mx-4 mt-[-2rem]"></div>
                    )}
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Detailed Steps */}
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-10 h-10 rounded-full border-2 border-gray-900 bg-gray-900 text-white flex items-center justify-center">
                    {i}
                  </div>
                  {i < 5 && <div className="w-0.5 h-24 bg-gray-400"></div>}
                </div>
                <div className="flex-1 pb-8 space-y-3">
                  <div className="h-5 w-48 border-b border-gray-700"></div>
                  <div className="space-y-2">
                    <div className="h-3 w-full border border-gray-400"></div>
                    <div className="h-3 w-3/4 border border-gray-400"></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'forms' && (
          <div className="space-y-6 relative">
            <Annotation type="action" text="Downloadable resources/forms area" position="right" />
            <div className="h-6 w-64 border-b-2 border-gray-900"></div>
            
            <div className="border-2 border-gray-400 p-6 bg-gray-50">
              <div className="h-5 w-40 border-b border-gray-700 mb-4"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="border-2 border-gray-400 p-6 bg-white hover:border-gray-900 cursor-pointer">
                    <div className="flex items-start gap-4">
                      <WireframeIcon size="lg" label="📄" />
                      <div className="flex-1 space-y-3">
                        <div className="h-5 w-48 border border-gray-700"></div>
                        <div className="h-3 w-32 border border-gray-400"></div>
                        <div className="flex gap-2">
                          <WireframeButton label="DOWNLOAD" variant="secondary" size="sm" />
                          <WireframeButton label="VIEW" variant="ghost" size="sm" />
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'faqs' && (
          <div className="space-y-4 relative">
            <Annotation type="interaction" text="FAQ (collapsible list, clearly marked Q/A)" position="right" />
            <div className="h-6 w-48 border-b-2 border-gray-900 mb-4"></div>
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="border-2 border-gray-400 hover:border-gray-600 cursor-pointer">
                <div className="p-4 flex items-center justify-between bg-gray-50">
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-sm">Q{i}:</span>
                    <div className="h-4 w-full max-w-lg border border-gray-700"></div>
                  </div>
                  <span className="text-gray-500">▼</span>
                </div>
                {i === 1 && (
                  <div className="p-4 border-t-2 border-gray-400 bg-white space-y-2">
                    <div className="flex items-start gap-3">
                      <span className="text-sm">A:</span>
                      <div className="flex-1 space-y-2">
                        <div className="h-3 w-full border border-gray-400"></div>
                        <div className="h-3 w-full border border-gray-400"></div>
                        <div className="h-3 w-2/3 border border-gray-400"></div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Related Services Section */}
      <section className="max-w-7xl mx-auto px-4 bg-gray-50 border-2 border-gray-400 p-8 relative">
        <Annotation type="flow" text="Related services section" position="left" />
        <div className="h-6 w-48 border-b-2 border-gray-900 mb-6 relative">
          <div className="absolute -bottom-6 left-0 text-xs text-gray-500">
            [RELATED SERVICES]
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="border border-gray-400 p-4 bg-white hover:border-gray-900 cursor-pointer">
              <div className="space-y-3">
                <WireframeIcon size="md" label={`R${i}`} />
                <div className="h-4 w-32 border border-gray-700"></div>
                <div className="space-y-1">
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-2/3 border border-gray-400"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Application Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white border-4 border-gray-900 max-w-2xl w-full max-h-[90vh] overflow-y-auto relative">
            <Annotation type="state" text="Modal overlay - application form" position="right" />
            <div className="p-8">
              <div className="flex justify-between items-center mb-6">
                <div className="h-6 w-48 border-b-2 border-gray-900"></div>
                <button onClick={() => setShowModal(false)} className="text-2xl">×</button>
              </div>

              <div className="space-y-6">
                {/* Form Fields */}
                {['Full Name', 'Email', 'Phone', 'Address', 'Document Upload'].map((field) => (
                  <div key={field} className="space-y-2">
                    <div className="h-4 w-32 border border-gray-600"></div>
                    <WireframeBox label={field.toUpperCase()} height="h-12" variant="outline" />
                  </div>
                ))}

                <div className="border-t-2 border-gray-400 pt-6 flex gap-3 justify-end">
                  <WireframeButton label="CANCEL" variant="ghost" onClick={() => setShowModal(false)} />
                  <WireframeButton label="SUBMIT APPLICATION" variant="primary" />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
