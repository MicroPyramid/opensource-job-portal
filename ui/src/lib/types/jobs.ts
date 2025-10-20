/**
 * TypeScript types for Jobs API
 * Matches the Django REST API response structure
 */

export interface Location {
  id: number;
  name: string;
  slug: string;
  state: string;
  state_slug: string;
}

export interface Skill {
  id: number;
  name: string;
  slug: string;
}

export interface Industry {
  id: number;
  name: string;
  slug: string;
}

export interface Qualification {
  id: number;
  name: string;
  slug: string;
}

export interface FunctionalArea {
  id: number;
  name: string;
}

export interface Company {
  id: number;
  name: string;
  slug: string;
  logo: string | null;
  profile_pic: string | null;
  company_type: string;
}

export type JobType = 'full-time' | 'internship' | 'walk-in' | 'government' | 'Fresher';

export type SalaryType = 'Month' | 'Year';

/**
 * Job listing model (lightweight for list views)
 */
export interface Job {
  id: number;
  title: string;
  slug: string;
  company_name: string;
  company_logo: string | null;
  job_type: JobType;
  locations: Location[];
  skills: Skill[];
  industries: Industry[];
  min_salary: number;
  max_salary: number;
  salary_type: SalaryType;
  min_year: number;
  max_year: number;
  min_month: number;
  max_month: number;
  fresher: boolean;
  published_on: string;
  last_date: string | null;
  vacancies: number;
  experience_display: string;
  salary_display: string;
  location_display: string;
  time_ago: string;
  applicants_count: number;
  is_saved: boolean;
  is_applied: boolean;
}

/**
 * Detailed job model (for detail views)
 */
export interface JobDetail extends Job {
  description: string;
  job_role: string;
  company: Company;
  company_description: string;
  company_address: string;
  company_links: string;
  company_emails: string | null;
  edu_qualification: Qualification[];
  functional_area: FunctionalArea[];
  // Walk-in specific fields
  walkin_contactinfo: string;
  walkin_show_contact_info: boolean;
  walkin_from_date: string | null;
  walkin_to_date: string | null;
  walkin_time: string | null;
  // Government job specific fields
  govt_job_type: string;
  application_fee: number;
  selection_process: string;
  how_to_apply: string;
  important_dates: string;
  govt_from_date: string | null;
  govt_to_date: string | null;
  govt_exam_date: string | null;
  age_relaxation: string;
}

/**
 * Filter option with count
 */
export interface FilterOption {
  id: number;
  name: string;
  slug: string;
  count: number;
}

/**
 * Job type filter option
 */
export interface JobTypeOption {
  value: JobType;
  label: string;
  count: number;
}

/**
 * All available filter options with counts
 */
export interface JobFilterOptions {
  locations: FilterOption[];
  skills: FilterOption[];
  industries: FilterOption[];
  education: FilterOption[];
  job_types: JobTypeOption[];
}

/**
 * Paginated response from jobs list API
 */
export interface JobListResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Job[];
}

/**
 * Job search parameters for API requests
 */
export interface JobSearchParams {
  page?: number;
  page_size?: number;
  search?: string;
  location?: string[];  // Location slugs
  skills?: string[];    // Skill slugs
  industry?: string[];  // Industry slugs
  education?: string[]; // Qualification slugs
  job_type?: string[];  // Job type values
  min_salary?: number;  // In LPA
  max_salary?: number;  // In LPA
  min_experience?: number;  // In years
  max_experience?: number;  // In years
  fresher?: boolean;
  is_remote?: boolean;
  posted_after?: string;  // ISO date string
  posted_before?: string; // ISO date string
  ordering?: string;  // e.g., '-published_on', 'min_salary'
}

/**
 * Client-side filter state
 * Used for UI state management
 */
export interface JobFilters {
  searchTerm: string;
  locationSearchTerm: string;
  selectedLocations: string[];
  selectedSkills: string[];
  selectedIndustries: string[];
  selectedEducation: string[];
  selectedJobTypes: string[];
  minSalary: number | null;
  maxSalary: number | null;
  minExperience: number;
  maxExperience: number;
  isRemote: boolean;
  fresher: boolean;
}
