import { ApiClient } from './client';

export interface Country {
	id: number;
	name: string;
	slug: string;
	status: string;
}

export interface State {
	id: number;
	name: string;
	slug: string;
	status: string;
	country?: Country;
}

export interface City {
	id: number;
	name: string;
	slug: string;
	status: string;
	state?: State;
	state_name?: string;
	country_name?: string;
}

/**
 * Get list of all enabled countries
 */
export async function getCountries(): Promise<Country[]> {
	return ApiClient.get<Country[]>('/locations/countries/', true); // skipAuth = true (public endpoint)
}

/**
 * Get list of states, optionally filtered by country
 */
export async function getStates(countryId?: number): Promise<State[]> {
	const params = countryId ? `?country_id=${countryId}` : '';
	return ApiClient.get<State[]>(`/locations/states/${params}`, true);
}

/**
 * Get list of cities, optionally filtered by state or country
 */
export async function getCities(params?: {
	stateId?: number;
	countryId?: number;
	search?: string;
}): Promise<City[]> {
	const queryParams = new URLSearchParams();

	if (params?.stateId) {
		queryParams.append('state_id', params.stateId.toString());
	}
	if (params?.countryId) {
		queryParams.append('country_id', params.countryId.toString());
	}
	if (params?.search) {
		queryParams.append('search', params.search);
	}

	const query = queryParams.toString();
	return ApiClient.get<City[]>(`/locations/cities/${query ? `?${query}` : ''}`, true);
}

/**
 * Get details of a specific city
 */
export async function getCityDetails(cityId: number): Promise<City> {
	return ApiClient.get<City>(`/locations/cities/${cityId}/`, true);
}
