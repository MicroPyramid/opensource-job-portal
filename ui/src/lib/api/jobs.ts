/**
 * Jobs API Client
 * Functions for interacting with the jobs API endpoints
 */

import { apiClient } from './client';
import type {
  Job,
  JobDetail,
  JobListResponse,
  JobFilterOptions,
  JobSearchParams,
} from '$lib/types/jobs';

/**
 * Jobs API namespace
 */
export const jobsApi = {
  /**
   * Fetch paginated job listings with filters
   * @param params - Search and filter parameters
   * @returns Paginated job list response
   */
  async list(params: JobSearchParams = {}): Promise<JobListResponse> {
    const queryParams = new URLSearchParams();

    // Add pagination params
    if (params.page) queryParams.set('page', params.page.toString());
    if (params.page_size) queryParams.set('page_size', params.page_size.toString());

    // Add search param
    if (params.search) queryParams.set('search', params.search);

    // Add filter params (arrays)
    if (params.location?.length) {
      params.location.forEach((loc) => queryParams.append('location', loc));
    }
    if (params.skills?.length) {
      params.skills.forEach((skill) => queryParams.append('skills', skill));
    }
    if (params.industry?.length) {
      params.industry.forEach((ind) => queryParams.append('industry', ind));
    }
    if (params.education?.length) {
      params.education.forEach((edu) => queryParams.append('education', edu));
    }
    if (params.job_type?.length) {
      params.job_type.forEach((type) => queryParams.append('job_type', type));
    }

    // Add numeric filters
    if (params.min_salary !== undefined && params.min_salary !== null) {
      queryParams.set('min_salary', params.min_salary.toString());
    }
    if (params.max_salary !== undefined && params.max_salary !== null) {
      queryParams.set('max_salary', params.max_salary.toString());
    }
    if (params.min_experience !== undefined && params.min_experience !== null) {
      queryParams.set('min_experience', params.min_experience.toString());
    }
    if (params.max_experience !== undefined && params.max_experience !== null) {
      queryParams.set('max_experience', params.max_experience.toString());
    }

    // Add boolean filters
    if (params.fresher !== undefined) {
      queryParams.set('fresher', params.fresher.toString());
    }
    if (params.is_remote !== undefined) {
      queryParams.set('is_remote', params.is_remote.toString());
    }

    // Add date filters
    if (params.posted_after) {
      queryParams.set('posted_after', params.posted_after);
    }
    if (params.posted_before) {
      queryParams.set('posted_before', params.posted_before);
    }

    // Add ordering
    if (params.ordering) {
      queryParams.set('ordering', params.ordering);
    }

    const queryString = queryParams.toString();
    const url = queryString ? `/jobs/?${queryString}` : '/jobs/';

    const response = await apiClient.get(url, true);
    return response;
  },

  /**
   * Fetch single job details by ID or slug
   * @param idOrSlug - Job ID (number) or slug (string)
   * @returns Detailed job information
   */
  async get(idOrSlug: string | number): Promise<JobDetail> {
    const response = await apiClient.get(`/jobs/${idOrSlug}/`, true);
    return response;
  },

  /**
   * Fetch all available filter options with job counts
   * @returns Filter options with counts
   */
  async getFilterOptions(): Promise<JobFilterOptions> {
    const response = await apiClient.get('/jobs/filter-options/', true);
    return response;
  },

  /**
   * Save/bookmark a job (requires authentication)
   * @param jobId - Job ID to save
   */
  async save(jobId: number): Promise<void> {
    await apiClient.post('/jobs/saved/', { job_id: jobId });
  },

  /**
   * Unsave/unbookmark a job (requires authentication)
   * @param jobId - Job ID to unsave
   */
  async unsave(jobId: number): Promise<void> {
    await apiClient.delete(`/jobs/saved/${jobId}/`);
  },

  /**
   * Get user's saved jobs (requires authentication)
   * @returns List of saved jobs
   */
  async getSaved(): Promise<Job[]> {
    const response = await apiClient.get('/jobs/saved/');
    return response;
  },
};
