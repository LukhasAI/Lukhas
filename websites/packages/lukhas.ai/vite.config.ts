import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@lukhas/ui': path.resolve(__dirname, '../ui/src'),
    },
  },
  server: {
    port: 3004,
    open: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
})
