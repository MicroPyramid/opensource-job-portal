import type { PageServerLoad } from './$types';
import { getApiBaseUrl } from '$lib/config/env';
import type { CompanySearchParams, CompanyFilterOptions, Company } from '$lib/api/companies';
import type { PaginatedResponse } from '$lib/types';

export const load: PageServerLoad = async ({ url, fetch }) => {
  // Parse query parameters
  const page = parseInt(url.searchParams.get('page') || '1', 10);
  const company_type = url.searchParams.get('company_type') || undefined;
  const size = url.searchParams.get('size') || undefined;
  const location = url.searchParams.get('location') || undefined;
  const industry = url.searchParams.get('industry') || undefined;
  const search = url.searchParams.get('search') || undefined;

  // Build API params
  const params: CompanySearchParams = {
    page,
    page_size: 20,
    company_type,
    size,
    location,
    industry,
    search,
  };

  // Build query string
  const queryString = new URLSearchParams(
    Object.entries(params)
      .filter(([_, value]) => value !== undefined && value !== null)
      .map(([key, value]) => [key, String(value)])
  ).toString();

  const apiBaseUrl = getApiBaseUrl();

  try {
    // Fetch companies and filter options in parallel using SvelteKit fetch
    const [companiesResponse, filterOptionsResponse] = await Promise.all([
      fetch(`${apiBaseUrl}/companies/?${queryString}`),
      fetch(`${apiBaseUrl}/companies/filter-options/`),
    ]);

    if (!companiesResponse.ok || !filterOptionsResponse.ok) {
      throw new Error('Failed to fetch data');
    }

    const companiesData: PaginatedResponse<Company> = await companiesResponse.json();
    const filterOptions: CompanyFilterOptions = await filterOptionsResponse.json();

    return {
      companies: companiesData.results || [],
      totalCompanies: companiesData.count || 0,
      totalPages: Math.ceil((companiesData.count || 0) / (params.page_size || 20)),
      currentPage: page,
      filterOptions,
      initialParams: {
        company_type,
        size,
        location,
        industry,
        search,
      },
    };
  } catch (error) {
    console.error('Error loading companies:', error);

    return {
      companies: [],
      totalCompanies: 0,
      totalPages: 0,
      currentPage: 1,
      filterOptions: {
        company_types: [],
        sizes: [],
        locations: [],
        industries: [],
      },
      initialParams: {},
      error: 'Failed to load companies. Please try again later.',
    };
  }
};
