import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: vitePreprocess(),

	kit: {
		adapter: adapter({
			out: 'build',
			precompress: false,
			envPrefix: ''
		})
		// Note: trailingSlash option removed - not supported in current SvelteKit version
		// Django backend handles URL normalization (adds trailing slashes)
	}
};

export default config;
