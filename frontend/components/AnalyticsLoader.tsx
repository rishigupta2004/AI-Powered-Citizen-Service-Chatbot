import React, { useEffect } from "react";

const AnalyticsLoader: React.FC = () => {
  const websiteId = (import.meta.env.VITE_VERCEL_ANALYTICS_ID as string) || "";
  const scriptSrc = (import.meta.env.VITE_ANALYTICS_SRC as string) || "https://static.vercel-insights.com/v1/script.js";

  useEffect(() => {
    if (!websiteId) return;
    if (document.querySelector(`script[data-website-id=\"${websiteId}\"]`)) return;
    const s = document.createElement("script");
    s.defer = true;
    s.src = scriptSrc;
    s.setAttribute("data-website-id", websiteId);
    document.head.appendChild(s);
  }, [websiteId, scriptSrc]);

  return null;
};

export default AnalyticsLoader;
