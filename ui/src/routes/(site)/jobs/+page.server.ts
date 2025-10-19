/**
 * Server-side data loader for jobs page
 * Handles SSR for initial page load
 */

import type { PageServerLoad } from './$types';
import type { JobSearchParams } from '$lib/types/jobs';
import { getApiBaseUrl } from '$lib/config/env';

const API_BASE_URL = getApiBaseUrl().replace('/api/v1', ''); // Get base domain without /api/v1

/**
 * Parse URL search params into API parameters
 */
function parseSearchParams(searchParams: URLSearchParams): JobSearchParams {
  const params: JobSearchParams = {};

  // Pagination
  const page = searchParams.get('page');
  if (page) params.page = parseInt(page, 10);

  // Search
  const search = searchParams.get('search');
  if (search) params.search = search;

  // Multi-select filters
  const locations = searchParams.getAll('location');
  if (locations.length) params.location = locations;

  const skills = searchParams.getAll('skills');
  if (skills.length) params.skills = skills;

  const industries = searchParams.getAll('industry');
  if (industries.length) params.industry = industries;

  const education = searchParams.getAll('education');
  if (education.length) params.education = education;

  const jobTypes = searchParams.getAll('job_type');
  if (jobTypes.length) params.job_type = jobTypes;

  // Numeric filters
  const minSalary = searchParams.get('min_salary');
  if (minSalary) params.min_salary = parseFloat(minSalary);

  const maxSalary = searchParams.get('max_salary');
  if (maxSalary) params.max_salary = parseFloat(maxSalary);

  const minExperience = searchParams.get('min_experience');
  if (minExperience) params.min_experience = parseInt(minExperience, 10);

  const maxExperience = searchParams.get('max_experience');
  if (maxExperience) params.max_experience = parseInt(maxExperience, 10);

  // Boolean filters
  const fresher = searchParams.get('fresher');
  if (fresher) params.fresher = fresher === 'true';

  const isRemote = searchParams.get('is_remote');
  if (isRemote) params.is_remote = isRemote === 'true';

  // Ordering
  const ordering = searchParams.get('ordering');
  if (ordering) params.ordering = ordering;

  return params;
}

/**
 * Build query string from params
 */
function buildQueryString(params: JobSearchParams): string {
  const queryParams = new URLSearchParams();

  if (params.page) queryParams.set('page', params.page.toString());
  if (params.page_size) queryParams.set('page_size', params.page_size.toString());
  if (params.search) queryParams.set('search', params.search);

  // Arrays
  params.location?.forEach((loc) => queryParams.append('location', loc));
  params.skills?.forEach((skill) => queryParams.append('skills', skill));
  params.industry?.forEach((ind) => queryParams.append('industry', ind));
  params.education?.forEach((edu) => queryParams.append('education', edu));
  params.job_type?.forEach((type) => queryParams.append('job_type', type));

  // Numbers
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

  // Booleans
  if (params.fresher !== undefined) {
    queryParams.set('fresher', params.fresher.toString());
  }
  if (params.is_remote !== undefined) {
    queryParams.set('is_remote', params.is_remote.toString());
  }

  if (params.ordering) queryParams.set('ordering', params.ordering);

  return queryParams.toString();
}

/**
 * Server-side load function
 * Fetches initial job data and filter options
 */
export const load: PageServerLoad = async ({ url, fetch, cookies }) => {
  const searchParams = url.searchParams;
  const params = parseSearchParams(searchParams);

  // Set default page size
  params.page_size = 20;

  try {
    // Get auth token from cookies if available
    const accessToken = cookies.get('access_token');
    const headers: HeadersInit = {};
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }

    // Build API URLs
    const jobsQueryString = buildQueryString(params);
    const jobsUrl = jobsQueryString
      ? `${API_BASE_URL}/api/v1/jobs/?${jobsQueryString}`
      : `${API_BASE_URL}/api/v1/jobs/`;
    const filterOptionsUrl = `${API_BASE_URL}/api/v1/jobs/filter-options/`;

    // Fetch data in parallel
    const [jobsResponse, filterOptionsResponse] = await Promise.all([
      fetch(jobsUrl, { headers }),
      fetch(filterOptionsUrl),
    ]);

    // Check for errors
    if (!jobsResponse.ok) {
      console.error('Failed to fetch jobs:', jobsResponse.statusText);
      return {
        jobs: [],
        totalJobs: 0,
        totalPages: 0,
        currentPage: params.page || 1,
        filterOptions: null,
        initialParams: params,
        error: 'Failed to load jobs. Please try again later.',
      };
    }

    if (!filterOptionsResponse.ok) {
      console.error('Failed to fetch filter options:', filterOptionsResponse.statusText);
    }

    // Parse responses
    const jobsData = await jobsResponse.json();
    const filterOptionsData = filterOptionsResponse.ok
      ? await filterOptionsResponse.json()
      : null;

    // Calculate pagination
    const totalJobs = jobsData.count || 0;
    const pageSize = params.page_size || 20;
    const totalPages = Math.ceil(totalJobs / pageSize);
    const currentPage = params.page || 1;

    return {
      jobs: jobsData.results || [],
      totalJobs,
      totalPages,
      currentPage,
      filterOptions: filterOptionsData,
      initialParams: params,
      error: null,
    };
  } catch (error) {
    console.error('Error loading jobs page:', error);
    return {
      jobs: [],
      totalJobs: 0,
      totalPages: 0,
      currentPage: params.page || 1,
      filterOptions: null,
      initialParams: params,
      error: 'An unexpected error occurred. Please try again later.',
    };
  }
};
