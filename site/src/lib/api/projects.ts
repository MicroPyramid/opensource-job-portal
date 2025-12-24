import { ApiClient } from './client';

export interface Skill {
	id: number;
	name: string;
	slug: string;
	skill_type: string;
}

export interface City {
	id: number;
	name: string;
	slug: string;
	state_name: string;
	country_name: string;
}

export interface Project {
	id: number;
	name: string;
	from_date?: string;
	to_date?: string;
	skills: Skill[];
	skill_ids?: number[];
	description: string;
	location?: City;
	location_id?: number;
	role?: string;
	size?: number;
}

export interface ProjectCreateUpdate {
	name: string;
	from_date?: string;
	to_date?: string;
	skill_ids: number[];
	description: string;
	location_id?: number;
	role?: string;
	size?: number;
}

/**
 * Get all projects for the authenticated user
 * Sorted by most recent first
 */
export async function getMyProjects(): Promise<Project[]> {
	return ApiClient.get<Project[]>('/profile/projects/');
}

/**
 * Get a specific project
 */
export async function getProjectById(projectId: number): Promise<Project> {
	return ApiClient.get<Project>(`/profile/projects/${projectId}/`);
}

/**
 * Add a new project
 */
export async function addProject(data: ProjectCreateUpdate): Promise<Project> {
	return ApiClient.post<Project>('/profile/projects/', data);
}

/**
 * Update an existing project (full update)
 */
export async function updateProject(
	projectId: number,
	data: ProjectCreateUpdate
): Promise<Project> {
	return ApiClient.put<Project>(`/profile/projects/${projectId}/`, data);
}

/**
 * Partially update a project
 */
export async function patchProject(
	projectId: number,
	data: Partial<ProjectCreateUpdate>
): Promise<Project> {
	return ApiClient.patch<Project>(`/profile/projects/${projectId}/`, data);
}

/**
 * Delete a project
 */
export async function deleteProject(projectId: number): Promise<void> {
	return ApiClient.delete(`/profile/projects/${projectId}/`);
}
