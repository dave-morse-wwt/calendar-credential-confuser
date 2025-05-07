import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { TanStackRouterVite } from '@tanstack/router-plugin/vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    TanStackRouterVite({ target: 'react', autoCodeSplitting: true }),
    // Please make sure that '@tanstack/router-plugin' is passed before '@vitejs/plugin-react'
    react(),
  ],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend API URL
        changeOrigin: true,               // Ensure correct headers for proxying
        secure: false,                    // Only for dev, as we are using HTTP
      },
    },
  },
})