import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  root: '.',
  server: {
    host: '0.0.0.0',
    port: 5173,
    strictPort: true,
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      clientPort: 80
    },
    proxy: {
      '/api': {
        target: 'http://render-routing-service:3000',
        changeOrigin: true,
        secure: false
      },
      '/storage': {
        target: 'http://storage-service:3000',
        changeOrigin: true,
        secure: false
      },
      '/pdf': {
        target: 'http://pdf-renderer:3000',
        changeOrigin: true,
        secure: false
      },
      '/png': {
        target: 'http://png-renderer:3000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'build',
    assetsDir: 'assets',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'index.html')
      }
    }
  }
})