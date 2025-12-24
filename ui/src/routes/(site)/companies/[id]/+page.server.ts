import type { PageServerLoad } from './$types';
import { getApiBaseUrl } from '$lib/config/env';
import { error } from '@sveltejs/kit';

export interface CompanyDetail {
  id: number;
  name: string;
  slug: string;
  logo: string;
  company_type: string;
  size: string;
  industry: {
    id: number;
    name: string;
    slug: string;
  };
  address: string;
  profile: string;
  website: string;
  email: string;
  phone: string;
  level: string;
  is_active: boolean;
  created_at: string;
  job_count: number;
  nature_of_business: string[];
}

export interface CompanyJob {
  id: number;
  title: string;
  slug: string;
  location_display: string;
  salary_display: string;
  experience_display: string;
  job_type: string;
  time_ago: string;
  company_logo: string;
  company_name: string;
}

export const load: PageServerLoad = async ({ params, fetch }) => {
  const { id } = params;
  const apiBaseUrl = getApiBaseUrl();

  try {
    // Fetch company details
    const companyResponse = await fetch(`${apiBaseUrl}/companies/${id}/`);

    if (!companyResponse.ok) {
      if (companyResponse.status === 404) {
        error(404, 'Company not found');
      }
      throw new Error('Failed to fetch company');
    }

    const company: CompanyDetail = await companyResponse.json();

    // Fetch company's jobs
    let jobs: CompanyJob[] = [];
    try {
      const jobsResponse = await fetch(`${apiBaseUrl}/jobs/?company=${company.id}&page_size=10`);
      if (jobsResponse.ok) {
        const jobsData = await jobsResponse.json();
        jobs = jobsData.results || [];
      }
    } catch (err) {
      console.error('Error fetching company jobs:', err);
    }

    return {
      company,
      jobs,
    };
  } catch (err) {
    console.error('Error loading company:', err);
    error(500, 'Failed to load company');
  }
};
