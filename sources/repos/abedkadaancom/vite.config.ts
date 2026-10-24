import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

// Client-only build. No SSR, no server routes. The CGT book is proxied at /cgt
// by vercel.json in production; in development the same path is proxied here.
export default defineConfig({
  plugins: [react()],
  build: {
    // `/assets` is left free for the legacy CGT book paths (see vercel.json).
    assetsDir: '_u',
    target: 'es2022',
    chunkSizeWarningLimit: 1200,
    rollupOptions: {
      output: {
        // Split heavy libraries by package only (never pulling React along), so the
        // entry stays small: 3D, PDF and astronomy load when a page needs them.
        manualChunks(id) {
          if (id.includes('vite/preload-helper') || id.includes('modulepreload-polyfill')) return 'react';
          if (!id.includes('node_modules')) return undefined;
          if (/node_modules\/(react|react-dom|scheduler|react-router|react-router-dom|use-sync-external-store)\//.test(id)) return 'react';
          if (/node_modules\/@supabase\//.test(id)) return 'supabase';
          if (/node_modules\/three\//.test(id)) return 'three';
          if (/node_modules\/(@react-three|three-stdlib|troika-|@monogrid|maath|camera-controls|three-mesh-bvh)/.test(id)) return 'r3f';
          if (/node_modules\/(pdf-lib|@pdf-lib|pako|tiny-inflate|unicode-|brotli|restructure|dfa|clone|fast-deep-equal)/.test(id)) return 'pdf';
          if (/node_modules\/astronomy-engine/.test(id)) return 'astro';
          return undefined;
        },
      },
    },
  },
  server: {
    proxy: {
      '/cgt': {
        target: 'https://computationalgrammartheory-sdk.vercel.app',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/cgt/, ''),
      },
    },
  },
  test: {
    include: ['tests/**/*.test.ts'],
    environment: 'node',
  },
});
