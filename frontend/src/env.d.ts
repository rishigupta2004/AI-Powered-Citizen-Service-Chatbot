interface ImportMetaEnv {
  readonly VITE_VERCEL_ANALYTICS_ID?: string;
  readonly VITE_ANALYTICS_SRC?: string;
  readonly VITE_ENABLE_SPEED_INSIGHTS?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
