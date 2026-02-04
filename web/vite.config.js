import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// base: './' makes the build work when hosted from a subfolder (e.g., GitHub Pages)
export default defineConfig({
  plugins: [react()],
  base: './',
})
