import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    // Removed proxy since frontend makes direct calls to localhost:8000
    // The proxy was for /api routes but our frontend uses full URLs
  }
})
