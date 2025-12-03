import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, 'src/main.jsx'),
      },
      output: {
        entryFileNames: '[name].js',
        chunkFileNames: '[name]-[hash].js',
        assetFileNames: '[name]-[hash][extname]',
      },
    },
  },
  resolve: {
    alias: {
      'rich-markdown-editor': path.resolve(__dirname, '../../../rich-markdown-editor/src'),
      react: path.resolve(__dirname, '../../../rich-markdown-editor/node_modules/react'),
      'react-dom': path.resolve(__dirname, '../../../rich-markdown-editor/node_modules/react-dom'),
    },
  },
});
