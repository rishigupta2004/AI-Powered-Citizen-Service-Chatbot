import React from 'react';
import { WireframeBox } from '../wireframe/WireframeBox';
import { WireframeButton } from '../wireframe/WireframeButton';
import { WireframeIcon } from '../wireframe/WireframeIcon';
import { Annotation } from '../wireframe/Annotation';

interface HomePageProps {
  onNavigate: (page: string) => void;
}

export function HomePage({ onNavigate }: HomePageProps) {
  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="relative bg-gray-50 border-2 border-gray-400 p-8 md:p-16">
        <Annotation type="flow" text="Hero banner - first impression" position="right" />
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-6 text-center lg:text-left">
              <div className="h-14 w-full lg:w-3/4 border-4 border-gray-900 bg-white relative">
                <Annotation type="interaction" text="Large header/title" position="top" />
              </div>
              <div className="h-6 w-full lg:w-2/3 border-2 border-gray-600 relative">
                <Annotation type="state" text="Subtitle/tagline" position="bottom" />
              </div>
              <div className="flex gap-4 justify-center lg:justify-start flex-wrap relative">
                <Annotation type="action" text="Two primary CTA buttons" position="bottom" />
                <WireframeButton label="GET STARTED" variant="primary" size="lg" onClick={() => onNavigate('services')} />
                <WireframeButton label="EXPLORE SERVICES" variant="secondary" size="lg" />
              </div>
            </div>
            <div className="relative">
              <WireframeBox label="HERO ILLUSTRATION" height="h-96" variant="filled" />
              <Annotation type="state" text="Hero illustration placeholder" position="left" />
            </div>
          </div>
        </div>
      </section>

      {/* Search Bar */}
      <section className="max-w-4xl mx-auto px-4 relative">
        <Annotation type="action" text="Main service search" position="left" />
        <div className="flex gap-3">
          <WireframeBox label="SEARCH FOR SERVICES..." height="h-14" variant="outline" className="flex-1" />
          <WireframeButton label="SEARCH" variant="primary" size="lg" />
        </div>
        <div className="mt-4 flex gap-2 flex-wrap">
          <span className="text-xs text-gray-500 uppercase">Popular:</span>
          {['License', 'Certificate', 'Permit', 'Registration'].map((tag) => (
            <div key={tag} className="px-3 py-1 border border-gray-400 text-xs cursor-pointer hover:bg-gray-100">
              {tag}
            </div>
          ))}
        </div>
      </section>

      {/* Feature Cards - Three Specific Features */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="flow" text="Three feature cards with specific content" position="left" />
        <div className="mb-8 text-center">
          <div className="h-8 w-64 mx-auto border-b-2 border-gray-900 mb-2"></div>
          <div className="h-4 w-96 mx-auto border border-gray-400"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {[
            { title: 'COMPLIANT BY DESIGN', icon: '✓', note: 'Meets govt standards' },
            { title: 'ACCESSIBLE & INCLUSIVE', icon: '♿', note: 'WCAG 2.1 AA compliant' },
            { title: 'READY FOR MULTILINGUAL', icon: '🌐', note: 'Multi-language support' }
          ].map((feature, i) => (
            <div 
              key={i} 
              className="border-2 border-gray-400 p-8 hover:border-gray-900 cursor-pointer transition-all hover:shadow-lg relative text-center"
            >
              {i === 0 && (
                <Annotation type="interaction" text="Feature card with icon, headline, description, note" position="right" />
              )}
              <div className="space-y-4">
                <div className="relative">
                  <WireframeIcon size="xl" label={feature.icon} />
                  <Annotation type="state" text="Placeholder icon" position="top" />
                </div>
                <div className="h-6 w-full border-b-2 border-gray-900 relative">
                  <div className="absolute -bottom-6 left-0 right-0 text-xs text-gray-500">
                    [{feature.title}]
                  </div>
                </div>
                <div className="space-y-2 pt-4">
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-3/4 mx-auto border border-gray-400"></div>
                </div>
                <div className="pt-3 border-t border-gray-300">
                  <div className="h-3 w-40 mx-auto border border-gray-500 italic text-[10px] flex items-center justify-center">
                    NOTE: {feature.note}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Service Dashboard Grid - Five Specific Services */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="flow" text="Service dashboard with specific services" position="left" />
        <div className="mb-8">
          <div className="h-8 w-64 border-b-2 border-gray-900 mb-2"></div>
          <div className="h-4 w-96 border border-gray-400"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {[
            { name: 'PASSPORT', icon: '📘', status: 'AVAILABLE' },
            { name: 'AADHAAR', icon: '🆔', status: 'AVAILABLE' },
            { name: 'EPFO', icon: '💼', status: 'AVAILABLE' },
            { name: 'SCHOLARSHIP', icon: '🎓', status: 'NEW' },
            { name: 'DRIVING LICENSE', icon: '🚗', status: 'AVAILABLE' }
          ].map((service, i) => (
            <div 
              key={i} 
              className="border-2 border-gray-400 p-6 hover:border-gray-900 cursor-pointer transition-all hover:shadow-lg relative group"
              onClick={() => onNavigate('service-detail')}
            >
              {i === 0 && (
                <Annotation type="interaction" text="Service card: icon, heading, description, status, action button" position="right" />
              )}
              <div className="space-y-4">
                <div className="relative">
                  <WireframeIcon size="xl" label={service.icon} />
                  <Annotation type="state" text="Icon placeholder" position="top" />
                </div>
                <div className="h-5 border-b-2 border-gray-900 relative text-xs">
                  [{service.name}]
                </div>
                <div className="space-y-2">
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-2/3 border border-gray-400"></div>
                </div>
                <div className="flex items-center justify-between pt-2">
                  <div className="px-2 py-1 border border-gray-600 text-[10px] relative">
                    STATUS: {service.status}
                    <Annotation type="state" text="Status badge" position="bottom" />
                  </div>
                </div>
                <WireframeButton label="APPLY NOW" variant="primary" size="sm" className="w-full" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Statistics Banner */}
      <section className="bg-gray-100 border-y-2 border-gray-400 py-12 relative">
        <Annotation type="state" text="Live statistics display" position="left" />
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {['Citizens Served', 'Services Available', 'Avg Response Time', 'Satisfaction Rate'].map((stat, i) => (
              <div key={i} className="text-center space-y-3">
                <div className="h-10 w-32 mx-auto border-2 border-gray-900 bg-white"></div>
                <div className="h-4 w-24 mx-auto border border-gray-500"></div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Access Dashboard */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="flow" text="Personalized dashboard section" position="right" />
        <div className="mb-8">
          <div className="h-8 w-64 border-b-2 border-gray-900 mb-2"></div>
          <div className="h-4 w-96 border border-gray-400"></div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Applications */}
          <div className="border-2 border-gray-400 p-6 relative">
            <Annotation type="state" text="Dynamic content - user specific" position="top" />
            <div className="h-5 w-40 border-b border-gray-600 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="border border-gray-400 p-3 hover:bg-gray-50 cursor-pointer">
                  <div className="h-4 w-32 border border-gray-600 mb-2"></div>
                  <div className="h-3 w-24 border border-gray-400"></div>
                </div>
              ))}
            </div>
          </div>

          {/* Notifications */}
          <div className="border-2 border-gray-400 p-6 relative">
            <Annotation type="action" text="Click to view all notifications" position="top" />
            <div className="h-5 w-40 border-b border-gray-600 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex gap-3 border border-gray-400 p-3">
                  <WireframeIcon size="sm" label="!" />
                  <div className="flex-1 space-y-2">
                    <div className="h-3 w-full border border-gray-600"></div>
                    <div className="h-2 w-16 border border-gray-400"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bookmarks/Saved */}
          <div className="border-2 border-gray-400 p-6">
            <div className="h-5 w-40 border-b border-gray-600 mb-4"></div>
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="flex items-center gap-3 border border-gray-400 p-3 hover:bg-gray-50 cursor-pointer">
                  <WireframeIcon size="sm" label="★" />
                  <div className="h-4 w-32 border border-gray-600"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Announcements/News Carousel */}
      <section className="max-w-7xl mx-auto px-4 relative">
        <Annotation type="interaction" text="Swipeable carousel" position="left" />
        <div className="mb-8">
          <div className="h-8 w-48 border-b-2 border-gray-900"></div>
        </div>
        <div className="relative border-2 border-gray-400 p-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="space-y-4">
                <WireframeBox label="NEWS IMAGE" height="h-40" variant="filled" />
                <div className="h-5 w-full border-b border-gray-700"></div>
                <div className="space-y-2">
                  <div className="h-3 w-full border border-gray-400"></div>
                  <div className="h-3 w-full border border-gray-400"></div>
                </div>
              </div>
            ))}
          </div>
          <div className="flex justify-center gap-2 mt-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className={`w-2 h-2 border border-gray-600 ${i === 1 ? 'bg-gray-900' : ''}`}></div>
            ))}
          </div>
        </div>
      </section>

      {/* Help Section */}
      <section className="max-w-4xl mx-auto px-4 bg-gray-50 border-2 border-gray-400 p-8 relative">
        <Annotation type="flow" text="Help CTA section" position="right" />
        <div className="text-center space-y-4">
          <div className="h-8 w-64 mx-auto border-b-2 border-gray-900"></div>
          <div className="h-4 w-96 mx-auto border border-gray-400"></div>
          <div className="flex gap-4 justify-center">
            <WireframeButton label="VIEW FAQ" variant="secondary" onClick={() => onNavigate('faq')} />
            <WireframeButton label="CONTACT SUPPORT" variant="ghost" />
          </div>
        </div>
      </section>
    </div>
  );
}
