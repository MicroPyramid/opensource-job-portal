/**
 * Server-side data loading for job detail page
 * Handles SSR for SEO optimization and fast initial page load
 */

import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import type { JobDetail, Job, JobListResponse } from '$lib/types/jobs';
import { getApiBaseUrl } from '$lib/config/env';

const API_BASE = getApiBaseUrl();

export const load: PageServerLoad = async ({ params, fetch, cookies }) => {
  const { id } = params;

  try {
    // Get auth token from cookies if available
    const accessToken = cookies.get('access_token');
    const headers: HeadersInit = {};
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    // Fetch job detail using slug or ID
    const jobResponse = await fetch(`${API_BASE}/jobs/${id}/`, { headers });

    if (!jobResponse.ok) {
      throw error(jobResponse.status === 404 ? 404 : 500, {
        message: jobResponse.status === 404 ? 'Job not found' : 'Failed to load job details',
      });
    }

    const jobDetail: JobDetail = await jobResponse.json();

    // Fetch related jobs based on industry, skills, and location
    const relatedJobs = await fetchRelatedJobs(jobDetail, fetch);

    return {
      job: jobDetail,
      relatedJobs,
    };
  } catch (err) {
    // Handle errors
    console.error('Error fetching job detail:', err);

    if (err && typeof err === 'object' && 'status' in err) {
      throw err; // Re-throw SvelteKit errors
    }

    throw error(500, {
      message: 'Failed to load job details',
    });
  }
};

/**
 * Fetch related/similar jobs based on the current job
 * Uses industry, skills, and location for matching
 */
async function fetchRelatedJobs(job: JobDetail, fetch: typeof globalThis.fetch): Promise<Job[]> {
  try {
    // Build filter params for related jobs
    const params = new URLSearchParams();

    // Limit to 6 jobs
    params.set('page_size', '6');

    // Add industry filter (highest priority)
    if (job.industries && job.industries.length > 0) {
      job.industries.slice(0, 2).forEach((industry) => {
        params.append('industry', industry.slug);
      });
    }

    // Add skills filter
    if (job.skills && job.skills.length > 0) {
      job.skills.slice(0, 3).forEach((skill) => {
        params.append('skills', skill.slug);
      });
    }

    // Add location filter
    if (job.locations && job.locations.length > 0) {
      params.append('location', job.locations[0].slug);
    }

    // Sort by most recent
    params.set('ordering', '-published_on');

    const queryString = params.toString();
    const url = `${API_BASE}/jobs/?${queryString}`;

    const response = await fetch(url);

    if (!response.ok) {
      console.error('Failed to fetch related jobs');
      return [];
    }

    const data: JobListResponse = await response.json();

    // Filter out the current job and return up to 6 results
    const filtered = data.results.filter((relatedJob: Job) => relatedJob.id !== job.id).slice(0, 6);

    return filtered;
  } catch (err) {
    console.error('Error fetching related jobs:', err);
    return [];
  }
}
