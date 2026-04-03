import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 1420,
    strictPort: true,
    proxy: {
      '/media': {
        target: 'http://127.0.0.1:8765',
        changeOrigin: true,
      },
    },
  },
  clearScreen: false,
});
