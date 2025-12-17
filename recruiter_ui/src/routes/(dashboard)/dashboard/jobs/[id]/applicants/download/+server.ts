/**
 * CSV Download Handler for Job Applicants
 * Generates CSV file with applicant data based on filters
 */

import { error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { API_BASE_URL } from '$lib/config/env';

export const GET: RequestHandler = async ({ params, url, cookies, fetch }) => {
	const jobId = params.id;
	const accessToken = cookies.get('access_token');

	if (!accessToken) {
		throw error(401, 'Unauthorized');
	}

	// Get filter parameters
	const statusFilter = url.searchParams.get('status') || '';
	const searchQuery = url.searchParams.get('search') || '';

	try {
		// Build query parameters for API request
		const queryParams = new URLSearchParams();
		if (statusFilter) {
			queryParams.set('status', statusFilter);
		}
		if (searchQuery) {
			queryParams.set('search', searchQuery);
		}
		// Request all applicants (no pagination for CSV export)
		queryParams.set('page_size', '10000');

		// Fetch applicants data from API
		const response = await fetch(
			`${API_BASE_URL}/recruiter/jobs/${jobId}/applicants/?${queryParams.toString()}`,
			{
				headers: {
					Authorization: `Bearer ${accessToken}`
				}
			}
		);

		if (!response.ok) {
			throw error(response.status, 'Failed to fetch applicants data');
		}

		const data = await response.json();
		const applications = data.applications || [];

		// Generate CSV content
		const csvRows: string[] = [];

		// CSV Headers
		const headers = [
			'Name',
			'Email',
			'Phone',
			'Current Location',
			'Experience',
			'Skills',
			'Education',
			'Status',
			'Applied On',
			'Remarks',
			'Resume URL'
		];
		csvRows.push(headers.map((header) => escapeCSVField(header)).join(','));

		// CSV Data Rows
		for (const application of applications) {
			const applicant = application.applicant;

			const row = [
				applicant.name || '',
				applicant.email || '',
				applicant.mobile || '',
				applicant.current_location || '',
				applicant.experience || '',
				applicant.skills?.join('; ') || '',
				applicant.education || '',
				application.status || '',
				application.applied_on || '',
				application.remarks || '',
				applicant.resume_url || ''
			];

			csvRows.push(row.map((field) => escapeCSVField(field)).join(','));
		}

		const csvContent = csvRows.join('\n');

		// Generate filename with status filter and timestamp
		const timestamp = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
		const statusSuffix = statusFilter ? `_${statusFilter.toLowerCase()}` : '_all';
		const filename = `applicants_job${jobId}${statusSuffix}_${timestamp}.csv`;

		// Return CSV file
		return new Response(csvContent, {
			headers: {
				'Content-Type': 'text/csv; charset=utf-8',
				'Content-Disposition': `attachment; filename="${filename}"`,
				'Cache-Control': 'no-cache'
			}
		});
	} catch (err: any) {
		console.error('Error generating CSV:', err);
		throw error(500, err.message || 'Failed to generate CSV file');
	}
};

/**
 * Escape CSV field to handle special characters
 */
function escapeCSVField(field: string): string {
	if (field == null) {
		return '';
	}

	const stringField = String(field);

	// Check if field needs to be quoted (contains comma, quote, or newline)
	if (
		stringField.includes(',') ||
		stringField.includes('"') ||
		stringField.includes('\n') ||
		stringField.includes('\r')
	) {
		// Escape quotes by doubling them and wrap in quotes
		return `"${stringField.replace(/"/g, '""')}"`;
	}

	return stringField;
}
