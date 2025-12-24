/**
 * Companies API Client
 */
import { apiClient } from './client';
import type { PaginatedResponse } from '../types';

export interface Company {
  id: number;
  name: string;
  slug: string;
  logo: string;
  company_type: string;
  size: string;
  industry_name: string;
  location: string;
  job_count: number;
  nature_of_business: string[];
}

export interface CompanyFilterOptions {
  company_types: FilterOption[];
  sizes: FilterOption[];
  locations: FilterOption[];
  industries: FilterOption[];
}

export interface FilterOption {
  label: string;
  value: string;
  count: number;
}

export interface CompanySearchParams {
  page?: number;
  page_size?: number;
  company_type?: string;
  size?: string;
  location?: string;
  industry?: string;
  search?: string;
}

export const companiesApi = {
  /**
   * List companies with optional filtering
   */
  async list(params: CompanySearchParams = {}): Promise<PaginatedResponse<Company>> {
    return await apiClient.get<PaginatedResponse<Company>>('/companies/', params, true);
  },

  /**
   * Get company details by slug
   */
  async get(slug: string): Promise<Company> {
    return await apiClient.get<Company>(`/companies/${slug}/`, true);
  },

  /**
   * Get filter options for companies page
   */
  async getFilterOptions(): Promise<CompanyFilterOptions> {
    return await apiClient.get<CompanyFilterOptions>('/companies/filter-options/', true);
  },
};
