/**
 * Error Message Formatter
 * Converts Django REST Framework error responses into user-friendly messages
 */

/**
 * Format field name to be user-friendly
 * Converts snake_case to Title Case, with special handling for common terms
 */
function formatFieldName(field: string): string {
	// Special cases - common field names that should be formatted differently
	const specialCases: Record<string, string> = {
		email: 'Email',
		password: 'Password',
		old_password: 'Current password',
		new_password: 'New password',
		confirm_password: 'Password confirmation',
		first_name: 'First name',
		last_name: 'Last name',
		phone: 'Phone number',
		mobile: 'Mobile number',
		company_name: 'Company name',
		company_website: 'Company website',
		company_size: 'Company size',
		job_title: 'Job title',
		agree_to_terms: 'Terms of service agreement'
	};

	if (specialCases[field]) {
		return specialCases[field];
	}

	// Convert snake_case to Title Case
	return field
		.split('_')
		.map((word) => word.charAt(0).toUpperCase() + word.slice(1))
		.join(' ');
}

/**
 * Format Django REST Framework error response into user-friendly message
 *
 * Handles:
 * - non_field_errors: Returns just the message (no field name prefix)
 * - Single field errors: Returns formatted field name with message
 * - Multiple field errors: Returns bulleted list of formatted errors
 */
export function formatApiError(errorData: any): string {
	// Handle string errors
	if (typeof errorData === 'string') {
		return errorData;
	}

	// Handle error or detail fields (standard DRF error format)
	if (errorData?.error) {
		return errorData.error;
	}
	if (errorData?.detail) {
		return errorData.detail;
	}

	// Handle DRF validation errors: { field_name: ["error message"] }
	if (errorData && typeof errorData === 'object') {
		const errors: string[] = [];

		for (const [field, messages] of Object.entries(errorData)) {
			// Extract error message(s)
			const errorMessage = Array.isArray(messages) ? messages.join(', ') : String(messages);

			// Special handling for non_field_errors - don't show field name
			if (field === 'non_field_errors') {
				errors.push(errorMessage);
			} else {
				// Format field name and combine with message
				const fieldName = formatFieldName(field);
				errors.push(`${fieldName}: ${errorMessage}`);
			}
		}

		if (errors.length > 0) {
			// Single error - return as-is
			if (errors.length === 1) {
				return errors[0];
			}
			// Multiple errors - return as bulleted list
			return errors.map((error) => `• ${error}`).join('\n');
		}
	}

	// Fallback
	return 'An error occurred. Please try again.';
}
