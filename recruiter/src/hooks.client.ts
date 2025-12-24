/**
 * SvelteKit Client Hooks
 * Handles client-side initialization and error handling
 */

import type { HandleClientError } from '@sveltejs/kit';

/**
 * Handle errors on the client side
 */
export const handleError: HandleClientError = ({ error, event }) => {
	console.error('Client error:', error, 'Event:', event);

	return {
		message: 'An unexpected error occurred. Please try again.',
		code: 'UNKNOWN'
	};
};
