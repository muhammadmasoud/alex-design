import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { visualizer } from 'rollup-plugin-visualizer';


// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api'),
        timeout: 3600000, // 1 hour for large uploads
        proxyTimeout: 3600000, // 1 hour for large uploads
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  plugins: [
    react(),
    // Bundle analyzer - generates stats.html
    mode === 'production' && visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true,
    }),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  build: {
    // Production optimizations
    rollupOptions: {
      output: {
        // Manual chunk splitting for better caching
        manualChunks: {
          // Core dependencies
          vendor: ['react', 'react-dom', 'react-router-dom'],
          // UI components
          ui: [
            '@radix-ui/react-dialog', 
            '@radix-ui/react-dropdown-menu', 
            '@radix-ui/react-select', 
            '@radix-ui/react-tabs',
            '@radix-ui/react-toast',
            '@radix-ui/react-checkbox',
            '@radix-ui/react-label'
          ],
          // Animation library
          motion: ['framer-motion'],
          // Utility libraries
          utils: ['clsx', 'tailwind-merge', 'class-variance-authority'],
          // Data fetching
          query: ['@tanstack/react-query', 'axios'],
          // Icons
          icons: ['lucide-react'],
          // Forms
          forms: ['react-hook-form', '@hookform/resolvers', 'zod']
        },
        // Optimize asset names for better caching
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || [];
          const ext = info[info.length - 1];
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(ext || '')) {
            return `assets/images/[name]-[hash][extname]`;
          }
          if (/woff2?|eot|ttf|otf/i.test(ext || '')) {
            return `assets/fonts/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
      },
    },
    // Increase chunk size warning limit for large libraries
    chunkSizeWarningLimit: 1000,
    // Enable source maps for production debugging (disabled for production)
    sourcemap: mode === 'production' ? false : true,
    // Minify for production (using default esbuild which is faster)
    minify: mode === 'production' ? true : false,
    // Target modern browsers for smaller bundles
    target: 'es2020',
  },
  // Optimize dependencies
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'react-router-dom',
      'framer-motion',
      '@tanstack/react-query',
      'axios',
      'lucide-react',
    ],
  },
}));
