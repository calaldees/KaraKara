import path from 'node:path';
import { defineConfig } from '@rstest/core';

export default defineConfig({
  testEnvironment: 'jsdom',
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
