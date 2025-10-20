import type { PageServerLoad } from './$types';
import { getApiBaseUrl } from '$lib/config/env';

interface Category {
  id: number;
  name: string;
  slug: string;
}

interface Location {
  id: number;
  name: string;
  slug: string;
  jobs_count?: number;
}

interface Job {
  id: number;
  title: string;
  slug: string;
  company_name: string;
  company_logo: string;
  job_type: string;
  locations: Array<{ id: number; name: string; slug: string; state: string }>;
  skills: Array<{ id: number; name: string; slug: string }>;
  min_salary: number;
  max_salary: number;
  salary_display: string;
  experience_display: string;
  location_display: string;
  time_ago: string;
}

// Curated categories - relevant industries
const curatedCategorySlugs = [
  'it-software',
  'bpo',
  'banking',
  'education',
  'sales',
  'accounting',
  'medical',
  'advertising',
  'construction',
  'automobile',
  'travel',
  'freshers'
];

export const load: PageServerLoad = async ({ fetch }) => {
  try {
    const apiBaseUrl = getApiBaseUrl();

    // Fetch filter options (categories and locations)
    const filterOptionsResponse = await fetch(`${apiBaseUrl}/jobs/filter-options/`);
    if (!filterOptionsResponse.ok) {
      throw new Error('Failed to fetch filter options');
    }
    const filterOptions = await filterOptionsResponse.json();

    // Filter for curated categories only, maintaining order
    const allCategories = filterOptions.industries || [];
    const topCategories = curatedCategorySlugs
      .map(slug => allCategories.find((c: any) => c.slug === slug))
      .filter(Boolean) // Remove undefined entries
      .map((category: any) => ({
        id: category.id,
        name: category.name.trim(), // Clean up whitespace
        slug: category.slug
      })) as Category[];

    // Get top 12 locations sorted by job count
    const topLocations = (filterOptions.locations || [])
      .sort((a: any, b: any) => (b.count || 0) - (a.count || 0))
      .slice(0, 12)
      .map((location: any) => ({
        id: location.id,
        name: location.name,
        slug: location.slug,
        jobs_count: location.count
      })) as Location[];

    // Fetch latest jobs for featured section
    const jobsResponse = await fetch(`${apiBaseUrl}/jobs/?page=1&page_size=8`);
    if (!jobsResponse.ok) {
      throw new Error('Failed to fetch jobs');
    }
    const jobsData = await jobsResponse.json();
    const featuredJobs = (jobsData.results || []) as Job[];

    return {
      topCategories,
      topLocations,
      featuredJobs
    };
  } catch (error) {
    console.error('Error loading home page data:', error);
    // Return empty data on error to allow page to render
    return {
      topCategories: [] as Category[],
      topLocations: [] as Location[],
      featuredJobs: [] as Job[]
    };
  }
};
