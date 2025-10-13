import React from 'react';
import { WireframeBox } from './WireframeBox';
import { WireframeIcon } from './WireframeIcon';
import { Annotation } from './Annotation';

export function GlobalFooter() {
  return (
    <footer className="border-t-2 border-gray-400 bg-gray-50 mt-16">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
          {/* Emblem & Brand */}
          <div className="relative">
            <WireframeBox label="GOVT EMBLEM" height="h-24" width="w-24" variant="filled" className="mb-4" />
            <Annotation type="interaction" text="Official govt seal" position="right" />
            <div className="space-y-2">
              <div className="h-4 w-32 border border-gray-400"></div>
              <div className="h-4 w-24 border border-gray-400"></div>
            </div>
          </div>

          {/* Sitemap Column 1 */}
          <div className="relative">
            <div className="h-5 w-24 border-b-2 border-gray-900 mb-4"></div>
            <Annotation type="flow" text="Quick links" position="top" />
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-4 w-32 border border-gray-400 hover:bg-gray-100 cursor-pointer"></div>
              ))}
            </div>
          </div>

          {/* Sitemap Column 2 */}
          <div>
            <div className="h-5 w-24 border-b-2 border-gray-900 mb-4"></div>
            <div className="space-y-2">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-4 w-32 border border-gray-400 hover:bg-gray-100 cursor-pointer"></div>
              ))}
            </div>
          </div>

          {/* Contact & Social */}
          <div className="relative">
            <div className="h-5 w-24 border-b-2 border-gray-900 mb-4"></div>
            <Annotation type="interaction" text="Social media links" position="left" />
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="h-4 w-full border border-gray-400"></div>
                <div className="h-4 w-full border border-gray-400"></div>
              </div>
              <div className="flex gap-3">
                {['FB', 'TW', 'IG', 'YT'].map((social) => (
                  <WireframeIcon key={social} size="md" label={social} />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t-2 border-gray-300 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex gap-4 flex-wrap justify-center">
              {['Privacy Policy', 'Terms of Service', 'Cookie Policy', 'Accessibility'].map((link) => (
                <div key={link} className="h-4 w-24 border border-gray-400 hover:bg-gray-100 cursor-pointer"></div>
              ))}
            </div>
            <div className="relative">
              <div className="h-4 w-64 border border-gray-400 text-xs text-center">
                © {new Date().getFullYear()} Government Portal
              </div>
              <Annotation type="state" text="Dynamic copyright year" position="top" />
            </div>
          </div>
        </div>

        {/* Contact Details */}
        <div className="border-t-2 border-gray-300 mt-6 pt-6 relative">
          <Annotation type="flow" text="Contact details section" position="right" />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
            <div className="space-y-2">
              <div className="h-4 w-24 border border-gray-600"></div>
              <div className="h-3 w-32 border border-gray-400"></div>
              <div className="h-3 w-40 border border-gray-400"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 w-24 border border-gray-600"></div>
              <div className="h-3 w-48 border border-gray-400"></div>
            </div>
            <div className="space-y-2">
              <div className="h-4 w-24 border border-gray-600"></div>
              <div className="h-3 w-36 border border-gray-400"></div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
