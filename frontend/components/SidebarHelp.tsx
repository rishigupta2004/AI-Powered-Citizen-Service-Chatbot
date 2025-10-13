import React, { useState } from "react";
import { WireframeBox } from "./wireframe/WireframeBox";
import { WireframeButton } from "./wireframe/WireframeButton";
import { WireframeIcon } from "./wireframe/WireframeIcon";
import { Annotation } from "./wireframe/Annotation";

export function SidebarHelp() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-1/2 right-0 -translate-y-1/2 bg-gray-900 text-white px-3 py-8 border-2 border-gray-900 border-r-0 z-40 hover:bg-gray-700 transition-colors"
      >
        <div className="rotate-90 whitespace-nowrap text-xs uppercase tracking-wider">
          {isOpen ? "CLOSE HELP" : "HELP"}
        </div>
      </button>

      {/* Sidebar Panel */}
      <div
        className={`fixed top-0 right-0 h-full w-80 bg-white border-l-4 border-gray-900 z-30 transition-transform duration-300 overflow-y-auto ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="p-6 space-y-6 relative">
          <Annotation
            type="flow"
            text="Contextual help sidebar"
            position="left"
          />

          {/* Header */}
          <div className="border-b-2 border-gray-400 pb-4">
            <div className="flex items-center gap-3 mb-3">
              <WireframeIcon size="lg" label="?" />
              <div className="h-6 w-32 border-b-2 border-gray-900"></div>
            </div>
            <div className="h-3 w-full border border-gray-400"></div>
          </div>

          {/* Quick Help Topics */}
          <div className="space-y-3">
            <div className="h-5 w-32 border-b border-gray-700"></div>
            {[
              "Getting Started",
              "Common Tasks",
              "Troubleshooting",
              "FAQs",
            ].map((topic) => (
              <div
                key={topic}
                className="border border-gray-400 p-3 hover:bg-gray-50 cursor-pointer flex items-center justify-between"
              >
                <div className="h-4 w-32 border border-gray-600"></div>
                <span className="text-gray-400">→</span>
              </div>
            ))}
          </div>

          {/* Search Help */}
          <div className="space-y-3">
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <WireframeBox
              label="SEARCH HELP..."
              height="h-10"
              variant="outline"
            />
          </div>

          {/* Contact Options */}
          <div className="space-y-3">
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <div className="space-y-2">
              <WireframeButton
                label="LIVE CHAT"
                variant="primary"
                size="sm"
              />
              <WireframeButton
                label="EMAIL SUPPORT"
                variant="secondary"
                size="sm"
              />
              <WireframeButton
                label="PHONE SUPPORT"
                variant="ghost"
                size="sm"
              />
            </div>
          </div>

          {/* Resources */}
          <div className="space-y-3">
            <div className="h-5 w-32 border-b border-gray-700"></div>
            {[
              "User Guide",
              "Video Tutorials",
              "Documentation",
            ].map((resource) => (
              <div
                key={resource}
                className="flex items-center gap-2 p-2 border border-gray-400 hover:bg-gray-50 cursor-pointer"
              >
                <WireframeIcon size="sm" label="📄" />
                <div className="h-3 w-32 border border-gray-600"></div>
              </div>
            ))}
          </div>

          {/* System Status */}
          <div className="border-t-2 border-gray-400 pt-4 space-y-3">
            <div className="h-5 w-32 border-b border-gray-700"></div>
            <div className="flex items-center gap-3 p-3 bg-gray-50 border border-gray-400">
              <div className="w-3 h-3 rounded-full bg-green-500 border border-gray-600"></div>
              <div className="h-3 w-32 border border-gray-600"></div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}