import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
    plugins: [react()],
    base: '/',
    server: {
        port: 3000,
        proxy: {
            '/api': 'http://localhost:5001',
            '/socket.io': {
                target: 'ws://localhost:5001',
                ws: true,
            },
        },
    },
    build: {
        outDir: 'build',
        emptyOutDir: true,
    },
});
