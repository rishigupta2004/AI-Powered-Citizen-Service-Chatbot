import React, { useState } from "react";
import { WireframeButton } from "./wireframe/WireframeButton";
import { Annotation } from "./wireframe/Annotation";

interface ResponsiveFramesProps {
  children: React.ReactNode;
  pageName: string;
}

export function ResponsiveFrames({
  children,
  pageName,
}: ResponsiveFramesProps) {
  const [viewMode, setViewMode] = useState<
    "desktop" | "tablet" | "mobile"
  >("desktop");

  const frameStyles = {
    desktop: "w-full",
    tablet: "w-[768px] mx-auto border-4 border-gray-900",
    mobile: "w-[375px] mx-auto border-4 border-gray-900",
  };

  return (
    <div className="space-y-6">
      {/* Device Selector */}
      <div className="bg-gray-900 text-white p-4 sticky top-0 z-50 relative">
        <Annotation
          type="interaction"
          text="Responsive layout switcher"
          position="bottom"
        />
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="text-sm uppercase tracking-wider">
              {pageName} - Responsive Layouts
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode("desktop")}
              className={`px-4 py-2 border-2 ${
                viewMode === "desktop"
                  ? "border-white bg-white text-gray-900"
                  : "border-white text-white hover:bg-white hover:text-gray-900"
              }`}
            >
              🖥️ DESKTOP
            </button>
            <button
              onClick={() => setViewMode("tablet")}
              className={`px-4 py-2 border-2 ${
                viewMode === "tablet"
                  ? "border-white bg-white text-gray-900"
                  : "border-white text-white hover:bg-white hover:text-gray-900"
              }`}
            >
              📱 TABLET
            </button>
            <button
              onClick={() => setViewMode("mobile")}
              className={`px-4 py-2 border-2 ${
                viewMode === "mobile"
                  ? "border-white bg-white text-gray-900"
                  : "border-white text-white hover:bg-white hover:text-gray-900"
              }`}
            >
              📱 MOBILE
            </button>
          </div>
        </div>
      </div>

      {/* Responsive Frame */}
      <div className="bg-gray-100 p-8 min-h-screen">
        <div
          className={`${frameStyles[viewMode]} bg-white overflow-hidden shadow-2xl`}
        >
          {children}
        </div>

        {/* Device Info */}
        <div className="text-center mt-4 text-sm text-gray-600">
          Current View:{" "}
          <span className="uppercase tracking-wider">
            {viewMode}
          </span>
          {viewMode === "desktop" && " (Full Width)"}
          {viewMode === "tablet" && " (768px)"}
          {viewMode === "mobile" && " (375px)"}
        </div>
      </div>
    </div>
  );
}