/**
 * Contact API Client
 * Handles contact form submissions
 */

import { apiClient } from './client';

export interface ContactFormData {
	first_name: string;
	last_name?: string;
	email: string;
	phone?: number;
	category: string;
	subject: string;
	comment: string;
}

export interface ContactResponse {
	id: number;
	message: string;
}

/**
 * Submit a contact form inquiry
 * @param data - Contact form data
 * @returns Promise with contact submission response
 */
export async function submitContactForm(data: ContactFormData): Promise<ContactResponse> {
	// Use the static post method with skipAuth=true for public endpoint
	return apiClient.post<ContactResponse>('/contact/submit/', data, true);
}
