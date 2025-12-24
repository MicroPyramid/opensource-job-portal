/**
 * Common types used across the application
 */

/**
 * Django REST Framework paginated response
 */
export interface PaginatedResponse<T> {
	count: number;
	next: string | null;
	previous: string | null;
	results: T[];
}

// Re-export all types from individual files
export * from './jobs';
export * from './search';
