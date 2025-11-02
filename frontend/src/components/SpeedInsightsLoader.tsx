import React, { useEffect } from 'react';

/**
 * SpeedInsightsLoader
 *
 * Attempts to dynamically load `@vercel/speed-insights` at runtime and
 * mount the `SpeedInsights` React component if available. Guarded by
 * the env var `VITE_ENABLE_SPEED_INSIGHTS` so the loader is inert unless
 * explicitly enabled in production.
 *
 * This keeps the integration safe for non-Next/Vite environments.
 */
const SpeedInsightsLoader: React.FC = () => {
  const enabled = (import.meta.env.VITE_ENABLE_SPEED_INSIGHTS as string) === 'true';

  useEffect(() => {
    if (!enabled) return;

    let mounted = true;

    (async () => {
      try {
        // Try to import the official package. Many projects (non-Next) won't
        // have this dependency, so we catch failures and skip gracefully.
        const mod = await import('@vercel/speed-insights');
        const SpeedInsights = mod?.SpeedInsights || mod?.default;

        if (!SpeedInsights) {
          console.warn('SpeedInsights package found but component not exported. Skipping.');
          return;
        }

        if (!mounted) return;

        // Create a container to render the component into (isolated from app DOM)
        const rootId = 'vercel-speed-insights-root';
        let container = document.getElementById(rootId);
        if (!container) {
          container = document.createElement('div');
          container.id = rootId;
          // place it at end of body to avoid layout changes
          document.body.appendChild(container);
        }

        // React 18 rendering API
        const { createRoot } = await import('react-dom/client');
        const root = createRoot(container);
        root.render(React.createElement(SpeedInsights));
      } catch (err) {
        // Not a failure for the app — just skip speed insights if not present
        // or import fails (e.g. package not installed).
        // eslint-disable-next-line no-console
        console.warn('SpeedInsights not mounted (package missing or error):', err);
      }
    })();

    return () => {
      mounted = false;
    };
  }, [enabled]);

  return null;
};

export default SpeedInsightsLoader;
