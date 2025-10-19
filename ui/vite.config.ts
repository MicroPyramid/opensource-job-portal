import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],

	server: {
		port: 5173,
		proxy: {
			// Proxy API requests to Django during development
			'/api': {
				target: 'http://localhost:8000',
				changeOrigin: true
			}
		}
	}
});
