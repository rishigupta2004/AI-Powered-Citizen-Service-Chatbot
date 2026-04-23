import React, { useState, useEffect } from "react";

export function ResponsiveIndicator() {
  const [windowSize, setWindowSize] = useState({
    width: 0,
    height: 0,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () =>
      window.removeEventListener("resize", handleResize);
  }, []);

  const getDeviceType = () => {
    if (windowSize.width < 768) return "MOBILE";
    if (windowSize.width < 1024) return "TABLET";
    return "DESKTOP";
  };

  return (
    <div className="fixed bottom-6 left-6 z-50 bg-gray-900 text-white px-4 py-2 border-2 border-white shadow-lg text-xs">
      <div className="flex items-center gap-3">
        <span className="uppercase tracking-wider">
          {getDeviceType()}
        </span>
        <span className="opacity-70">|</span>
        <span>
          {windowSize.width} × {windowSize.height}
        </span>
      </div>
    </div>
  );
}