import type { UserConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';

declare const process: any;

export default {
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/api': process.env.STYLR_API_URL ?? 'http://localhost:3031'
    }
  }
} satisfies UserConfig;
