import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
	// Load env file based on `mode` in the current working directory.
	const env = loadEnv(mode, process.cwd(), '');

	// Extract the base URL without /api/v1 suffix for proxy target
	const apiBaseUrl = env.PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';
	const proxyTarget = apiBaseUrl.replace(/\/api\/v1$/, '');

	return {
		plugins: [tailwindcss(), sveltekit()],

		server: {
			port: 5173,
			proxy: {
				// Proxy API requests to Django during development
				'/api': {
					target: proxyTarget,
					changeOrigin: true
				}
			}
		}
	};
});
