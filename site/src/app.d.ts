// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
import type { User } from '$lib/types/auth';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			/** JWT from the HttpOnly cookie, refreshed in hooks.server.ts. */
			accessToken: string | null;
			isAuthenticated: boolean;
		}
		interface PageData {
			user?: User | null;
			isAuthenticated?: boolean;
		}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};
