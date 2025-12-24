/**
 * Search API Client
 * Handles autocomplete requests for skills, locations, etc.
 */

import { ApiClient } from './client';
import type {
  SkillAutocompleteResponse,
  LocationAutocompleteResponse,
} from '$lib/types/search';

// Cache for filter options to avoid repeated API calls
let filterOptionsCache: { locations?: any[]; skills?: any[]; timestamp?: number } | null = null;
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

/**
 * Get filter options from jobs API (cached)
 */
async function getFilterOptions() {
  const now = Date.now();

  // Return cached data if still valid
  if (filterOptionsCache && filterOptionsCache.timestamp && (now - filterOptionsCache.timestamp) < CACHE_DURATION) {
    return filterOptionsCache;
  }

  // Fetch fresh data
  const data = await ApiClient.get<any>('/jobs/filter-options/', true);

  filterOptionsCache = {
    locations: data.locations || [],
    skills: data.skills || [],
    timestamp: now
  };

  return filterOptionsCache;
}

/**
 * Search for skills with autocomplete using job filter options
 * This provides clean, curated skills that have active jobs
 * @param query - Search query string
 * @returns Promise with skill suggestions
 */
export async function searchSkills(
  query: string
): Promise<SkillAutocompleteResponse> {
  const filterOptions = await getFilterOptions();
  const skills = filterOptions.skills || [];

  // Filter skills by query (case-insensitive)
  const queryLower = query.toLowerCase().trim();
  const filtered = skills.filter((skill: any) =>
    skill.name.toLowerCase().includes(queryLower)
  );

  // Sort by name length (shorter names first, better matches)
  const sorted = filtered.sort((a: any, b: any) => a.name.length - b.name.length);

  // Return top 10 results
  return {
    results: sorted.slice(0, 10).map((skill: any) => ({
      id: skill.id,
      name: skill.name,
      slug: skill.slug,
      jobs_count: skill.count
    }))
  };
}

/**
 * Search for locations (cities) with autocomplete using job filter options
 * This provides clean, curated locations that have active jobs
 * @param query - Search query string
 * @returns Promise with location suggestions
 */
export async function searchLocations(
  query: string
): Promise<LocationAutocompleteResponse> {
  const filterOptions = await getFilterOptions();
  const locations = filterOptions.locations || [];

  // Filter locations by query (case-insensitive)
  const queryLower = query.toLowerCase().trim();
  const filtered = locations.filter((location: any) =>
    location.name.toLowerCase().includes(queryLower)
  );

  // Sort by name length (shorter names first, better matches)
  const sorted = filtered.sort((a: any, b: any) => a.name.length - b.name.length);

  // Return top 10 results
  return {
    results: sorted.slice(0, 10).map((location: any) => ({
      id: location.id,
      name: location.name,
      slug: location.slug,
      jobs_count: location.count
    }))
  };
}
