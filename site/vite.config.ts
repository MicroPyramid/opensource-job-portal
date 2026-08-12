import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

/**
 * No `/api` dev proxy.
 *
 * The browser now calls this app's own `/api/*` routes (src/routes/api), which
 * read the JWT from the HttpOnly cookie and forward to Django with a Bearer
 * header. A Vite proxy on `/api` would shadow those routes in dev and send the
 * request to Django unauthenticated.
 */
export default defineConfig({
	plugins: [tailwindcss(), sveltekit()],
	server: {
		port: 5173
	}
});
