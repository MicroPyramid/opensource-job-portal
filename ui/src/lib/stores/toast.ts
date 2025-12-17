/**
 * Toast Notification Store
 * Simple, lightweight toast notifications for user feedback
 */

import { writable } from 'svelte/store';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface Toast {
	id: string;
	message: string;
	type: ToastType;
	duration?: number;
}

interface ToastStore {
	toasts: Toast[];
}

function createToastStore() {
	const { subscribe, update } = writable<ToastStore>({ toasts: [] });

	return {
		subscribe,

		/**
		 * Show a toast notification
		 */
		show: (message: string, type: ToastType = 'info', duration: number = 3000) => {
			const id = Math.random().toString(36).substring(2, 9);
			const toast: Toast = { id, message, type, duration };

			update((store) => ({
				toasts: [...store.toasts, toast]
			}));

			// Auto-dismiss after duration
			if (duration > 0) {
				setTimeout(() => {
					update((store) => ({
						toasts: store.toasts.filter((t) => t.id !== id)
					}));
				}, duration);
			}
		},

		/**
		 * Show success toast
		 */
		success: (message: string, duration: number = 3000) => {
			const id = Math.random().toString(36).substring(2, 9);
			const toast: Toast = { id, message, type: 'success', duration };

			update((store) => ({
				toasts: [...store.toasts, toast]
			}));

			if (duration > 0) {
				setTimeout(() => {
					update((store) => ({
						toasts: store.toasts.filter((t) => t.id !== id)
					}));
				}, duration);
			}
		},

		/**
		 * Show error toast
		 */
		error: (message: string, duration: number = 4000) => {
			const id = Math.random().toString(36).substring(2, 9);
			const toast: Toast = { id, message, type: 'error', duration };

			update((store) => ({
				toasts: [...store.toasts, toast]
			}));

			if (duration > 0) {
				setTimeout(() => {
					update((store) => ({
						toasts: store.toasts.filter((t) => t.id !== id)
					}));
				}, duration);
			}
		},

		/**
		 * Show info toast
		 */
		info: (message: string, duration: number = 3000) => {
			const id = Math.random().toString(36).substring(2, 9);
			const toast: Toast = { id, message, type: 'info', duration };

			update((store) => ({
				toasts: [...store.toasts, toast]
			}));

			if (duration > 0) {
				setTimeout(() => {
					update((store) => ({
						toasts: store.toasts.filter((t) => t.id !== id)
					}));
				}, duration);
			}
		},

		/**
		 * Show warning toast
		 */
		warning: (message: string, duration: number = 3000) => {
			const id = Math.random().toString(36).substring(2, 9);
			const toast: Toast = { id, message, type: 'warning', duration };

			update((store) => ({
				toasts: [...store.toasts, toast]
			}));

			if (duration > 0) {
				setTimeout(() => {
					update((store) => ({
						toasts: store.toasts.filter((t) => t.id !== id)
					}));
				}, duration);
			}
		},

		/**
		 * Dismiss a specific toast
		 */
		dismiss: (id: string) => {
			update((store) => ({
				toasts: store.toasts.filter((t) => t.id !== id)
			}));
		},

		/**
		 * Clear all toasts
		 */
		clear: () => {
			update(() => ({ toasts: [] }));
		}
	};
}

export const toast = createToastStore();
