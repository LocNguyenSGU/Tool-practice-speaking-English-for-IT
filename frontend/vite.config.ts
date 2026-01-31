import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
// force rebuild: 2026-01-31
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    // Enable SPA fallback for client-side routing
    // This makes all routes serve index.html in development
    // This makes all routes serve index.html in development
    proxy: {
      '/api': {
        target: 'http://139.99.103.223:9999',
        changeOrigin: true,
      },
    },
  },
})
