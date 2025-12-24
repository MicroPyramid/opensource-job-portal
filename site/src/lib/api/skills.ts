import { ApiClient } from './client';

export interface Skill {
	id: number;
	name: string;
	slug: string;
	skill_type: string;
	status: string;
}

export interface TechnicalSkill {
	id: number;
	skill: Skill;
	year?: number;
	month?: number;
	last_used?: string;
	version?: string;
	proficiency?: 'Poor' | 'Average' | 'Good' | 'Expert';
	is_major: boolean;
}

export interface TechnicalSkillCreateUpdate {
	skill: number; // skill_id
	year?: number;
	month?: number;
	last_used?: string;
	version?: string;
	proficiency?: 'Poor' | 'Average' | 'Good' | 'Expert';
	is_major?: boolean;
}

/**
 * Search for skills in master skill list
 */
export async function searchSkills(params?: {
	search?: string;
	skill_type?: string;
}): Promise<Skill[]> {
	const queryParams = new URLSearchParams();

	if (params?.search) {
		queryParams.append('search', params.search);
	}
	if (params?.skill_type) {
		queryParams.append('skill_type', params.skill_type);
	}

	const query = queryParams.toString();
	return ApiClient.get<Skill[]>(`/skills/${query ? `?${query}` : ''}`, true); // Public endpoint
}

/**
 * Get user's technical skills
 */
export async function getMySkills(): Promise<TechnicalSkill[]> {
	return ApiClient.get<TechnicalSkill[]>('/skills/my-skills/');
}

/**
 * Add a new technical skill to user profile
 */
export async function addTechnicalSkill(
	data: TechnicalSkillCreateUpdate
): Promise<TechnicalSkill> {
	return ApiClient.post<TechnicalSkill>('/skills/my-skills/add/', data);
}

/**
 * Update an existing technical skill
 */
export async function updateTechnicalSkill(
	skillId: number,
	data: Partial<TechnicalSkillCreateUpdate>
): Promise<TechnicalSkill> {
	return ApiClient.patch<TechnicalSkill>(`/skills/my-skills/${skillId}/`, data);
}

/**
 * Delete a technical skill from user profile
 */
export async function deleteTechnicalSkill(skillId: number): Promise<void> {
	return ApiClient.delete(`/skills/my-skills/${skillId}/`);
}
