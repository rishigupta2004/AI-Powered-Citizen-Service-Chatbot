import React, { useEffect } from "react";

/**
 * AnalyticsLoader
 *
 * Safely injects a Vercel/Web Analytics script at runtime when the
 * environment variable VITE_VERCEL_ANALYTICS_ID is present.
 *
 * This keeps the change non-invasive and avoids depending on Next.js
 * specific packages. No script is added when the env var is not set,
 * so local development and builds are unaffected.
 */
const AnalyticsLoader: React.FC = () => {
  // Vite exposes env vars starting with VITE_ via import.meta.env
  const websiteId = (import.meta.env.VITE_VERCEL_ANALYTICS_ID as string) || "";
  const scriptSrc = (import.meta.env.VITE_ANALYTICS_SRC as string) || "https://static.vercel-insights.com/v1/script.js";

  useEffect(() => {
    if (!websiteId) return;

    // Avoid injecting the same script multiple times
    if (document.querySelector(`script[data-website-id=\"${websiteId}\"]`)) return;

    const s = document.createElement("script");
    s.defer = true;
    s.src = scriptSrc;
    s.setAttribute("data-website-id", websiteId);
    // optional: do not collect client IP if you want privacy-by-default
    // s.setAttribute('data-collect-client-ip', 'false');
    document.head.appendChild(s);

    // Keep the script loaded for the lifetime of the page; no cleanup.
    // If you wish to remove it on unmount, implement removal here.
  }, [websiteId, scriptSrc]);

  return null;
};

export default AnalyticsLoader;
