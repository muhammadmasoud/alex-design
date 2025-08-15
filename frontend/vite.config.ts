import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";


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
      },
      '/media': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  plugins: [
    react(),
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
           vendor: ['react', 'react-dom', 'react-router-dom'],
           ui: ['@radix-ui/react-dialog', '@radix-ui/react-dropdown-menu', '@radix-ui/react-select', '@radix-ui/react-tabs'],
           motion: ['framer-motion'],
           utils: ['clsx', 'tailwind-merge', 'class-variance-authority'],
           query: ['@tanstack/react-query', 'axios'],
           icons: ['lucide-react'],
         },
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
