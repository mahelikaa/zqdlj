import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// In development, requests to /api are forwarded to the FastAPI server, so the browser
// sees a single origin. In Docker the backend is reachable as http://backend:8000.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': process.env.API_PROXY_TARGET ?? 'http://localhost:8000',
    },
  },
})
