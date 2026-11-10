// Vite and Vitest settings: React plugin, the dev proxy to the API, and the browser-like test environment.
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [react()],
  // During "npm run dev", /api and /health are forwarded to the backend so the browser only talks to one origin.
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8004',
      '/health': 'http://localhost:8004',
    },
  },
  // Tests run in a simulated browser (jsdom); the setup file adds matchers and cleans up after every test.
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})






