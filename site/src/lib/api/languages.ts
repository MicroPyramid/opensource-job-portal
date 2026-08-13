import { ApiClient } from './client';

/** An entry in the language catalogue a seeker picks from. */
export interface LanguageOption {
	id: number;
	name: string;
}

/**
 * One language a user speaks.
 *
 * `read`/`write`/`speak` are independent rather than a single level — that is
 * how the legacy form collected them and how the existing 6,283 rows are
 * shaped, so flattening to one field would lose data.
 */
export interface UserLanguage {
	id: number;
	language: number;
	language_name: string;
	read: boolean;
	write: boolean;
	speak: boolean;
}

export interface UserLanguageInput {
	language: number;
	read: boolean;
	write: boolean;
	speak: boolean;
}

export async function getLanguageOptions(): Promise<LanguageOption[]> {
	return ApiClient.get<LanguageOption[]>('/profile/language-options/');
}

export async function getMyLanguages(): Promise<UserLanguage[]> {
	return ApiClient.get<UserLanguage[]>('/profile/languages/');
}

export async function addLanguage(data: UserLanguageInput): Promise<UserLanguage> {
	return ApiClient.post<UserLanguage>('/profile/languages/', data);
}

export async function updateLanguage(
	id: number,
	data: Partial<UserLanguageInput>
): Promise<UserLanguage> {
	return ApiClient.patch<UserLanguage>(`/profile/languages/${id}/`, data);
}

export async function deleteLanguage(id: number): Promise<void> {
	return ApiClient.delete<void>(`/profile/languages/${id}/`);
}
