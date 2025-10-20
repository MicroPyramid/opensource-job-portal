/**
 * Search and Autocomplete Types
 */

export interface SkillSuggestion {
  id: number;
  name: string;
  slug: string;
  jobs_count?: number;
}

export interface LocationSuggestion {
  id: number;
  name: string;
  slug?: string;
  jobs_count?: number;
}

export interface AutocompleteResponse<T> {
  results: T[];
}

export interface SkillAutocompleteResponse extends AutocompleteResponse<SkillSuggestion> {}

export interface LocationAutocompleteResponse extends AutocompleteResponse<LocationSuggestion> {}
