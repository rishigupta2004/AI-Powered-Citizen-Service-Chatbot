import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    extensions: ['.js', '.jsx', '.ts', '.tsx', '.json'],
    alias: {
      '@': path.resolve(__dirname, './src'),
      // Remove version-specific aliases as they can cause issues
    },
  },
  build: {
    target: 'esnext',
    outDir: 'build',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'statsig-vendor': [
            '@statsig/react-bindings', 
            '@statsig/web-analytics', 
            '@statsig/session-replay'
          ],
          'ui-vendor': [
            '@radix-ui/react-tooltip',
            '@radix-ui/react-toggle',
            '@radix-ui/react-toggle-group',
            '@radix-ui/react-tabs',
            '@radix-ui/react-switch',
            '@radix-ui/react-slot',
            '@radix-ui/react-slider',
            '@radix-ui/react-separator',
            '@radix-ui/react-select',
            '@radix-ui/react-scroll-area',
            '@radix-ui/react-radio-group',
            '@radix-ui/react-progress',
            '@radix-ui/react-popover',
            '@radix-ui/react-navigation-menu',
            '@radix-ui/react-menubar',
            '@radix-ui/react-label',
            '@radix-ui/react-hover-card',
            '@radix-ui/react-dropdown-menu',
            '@radix-ui/react-dialog',
            '@radix-ui/react-context-menu',
            '@radix-ui/react-collapsible',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-avatar',
            '@radix-ui/react-aspect-ratio',
            '@radix-ui/react-alert-dialog',
            '@radix-ui/react-accordion'
          ],
          'utils-vendor': [
            'recharts',
            'react-resizable-panels', 
            'react-hook-form',
            'react-day-picker',
            'lucide-react',
            'input-otp',
            'embla-carousel-react',
            'cmdk',
            'class-variance-authority',
            'vaul',
            'sonner',
            'next-themes'
          ]
        }
      }
    },
    chunkSizeWarningLimit: 600, // Increase warning limit slightly
  },
  server: {
    port: 3000,
    open: true,
  },
});