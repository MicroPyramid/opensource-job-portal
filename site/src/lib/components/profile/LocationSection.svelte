<script lang="ts">
	import { onMount } from 'svelte';
	import { MapPin, Loader, X } from '@lucide/svelte';
	import { getCountries, getStates, getCities, type Country, type State, type City } from '$lib/api/locations';
	import type { City as ProfileCity } from '$lib/api/profile';

	// Accept the full formData object, only use the fields we need
	export let formData: {
		city_id?: number;
		state_id?: number;
		country_id?: number;
		current_city_id?: number;
		preferred_city_ids?: number[];
		[key: string]: any;
	};

	// Read-only profile data for display
	export let profile: {
		city?: ProfileCity;
		state?: { id: number; name: string };
		country?: { id: number; name: string };
		current_city?: ProfileCity;
		preferred_city?: ProfileCity[];
	};

	// Dropdown data
	let countries: Country[] = [];
	let states: State[] = [];
	let cities: City[] = [];
	let preferredCities: City[] = [];
	let loadingCountries = false;
	let loadingStates = false;
	let loadingCities = false;
	let loadingPreferredCities = false;

	// Selected values for cascading dropdowns
	let selectedCountryId: number | undefined;
	let selectedStateId: number | undefined;
	let selectedCityId: number | undefined;
	let selectedCurrentCityId: number | undefined;

	// Multi-select for preferred cities
	let selectedPreferredCityIds: number[] = [];
	let preferredCitySearch = '';
	let showPreferredCityDropdown = false;

	onMount(async () => {
		await loadCountries();

		// Initialize from profile data
		if (profile.country?.id) {
			selectedCountryId = profile.country.id;
			formData.country_id = profile.country.id;
			await loadStates(profile.country.id);
		}

		if (profile.state?.id) {
			selectedStateId = profile.state.id;
			formData.state_id = profile.state.id;
			if (selectedCountryId) {
				await loadCities(selectedStateId);
			}
		}

		if (profile.city?.id) {
			selectedCityId = profile.city.id;
			formData.city_id = profile.city.id;
		}

		if (profile.current_city?.id) {
			selectedCurrentCityId = profile.current_city.id;
			formData.current_city_id = profile.current_city.id;
		}

		if (profile.preferred_city && profile.preferred_city.length > 0) {
			selectedPreferredCityIds = profile.preferred_city.map((c) => c.id);
			formData.preferred_city_ids = selectedPreferredCityIds;
		}
	});

	async function loadCountries() {
		try {
			loadingCountries = true;
			countries = await getCountries();
		} catch (err) {
			console.error('Failed to load countries:', err);
		} finally {
			loadingCountries = false;
		}
	}

	async function loadStates(countryId: number) {
		try {
			loadingStates = true;
			states = await getStates(countryId);
			cities = []; // Clear cities when country changes
		} catch (err) {
			console.error('Failed to load states:', err);
		} finally {
			loadingStates = false;
		}
	}

	async function loadCities(stateId: number) {
		try {
			loadingCities = true;
			cities = await getCities({ stateId });
		} catch (err) {
			console.error('Failed to load cities:', err);
		} finally {
			loadingCities = false;
		}
	}

	async function searchPreferredCities(search: string) {
		if (!search || search.length < 2) {
			preferredCities = [];
			return;
		}

		try {
			loadingPreferredCities = true;
			preferredCities = await getCities({ search });
		} catch (err) {
			console.error('Failed to search cities:', err);
		} finally {
			loadingPreferredCities = false;
		}
	}

	function handleCountryChange() {
		formData.country_id = selectedCountryId;
		formData.state_id = undefined;
		formData.city_id = undefined;
		selectedStateId = undefined;
		selectedCityId = undefined;
		states = [];
		cities = [];

		if (selectedCountryId) {
			loadStates(selectedCountryId);
		}
	}

	function handleStateChange() {
		formData.state_id = selectedStateId;
		formData.city_id = undefined;
		selectedCityId = undefined;
		cities = [];

		if (selectedStateId) {
			loadCities(selectedStateId);
		}
	}

	function handleCityChange() {
		formData.city_id = selectedCityId;
	}

	function handleCurrentCityChange() {
		formData.current_city_id = selectedCurrentCityId;
	}

	function togglePreferredCity(cityId: number) {
		if (selectedPreferredCityIds.includes(cityId)) {
			selectedPreferredCityIds = selectedPreferredCityIds.filter((id) => id !== cityId);
		} else {
			selectedPreferredCityIds = [...selectedPreferredCityIds, cityId];
		}
		formData.preferred_city_ids = selectedPreferredCityIds;
	}

	function removePreferredCity(cityId: number) {
		selectedPreferredCityIds = selectedPreferredCityIds.filter((id) => id !== cityId);
		formData.preferred_city_ids = selectedPreferredCityIds;
	}

	// Get selected preferred city names for display
	$: selectedPreferredCityNames = selectedPreferredCityIds
		.map((id) => {
			const city =
				profile.preferred_city?.find((c) => c.id === id) ||
				preferredCities.find((c) => c.id === id);
			return city ? city.name : null;
		})
		.filter(Boolean);

	// Search when user types
	$: searchPreferredCities(preferredCitySearch);
</script>

<div class="p-5 lg:p-6">
	<div class="flex items-center gap-3 mb-6">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<MapPin size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-lg font-semibold text-gray-900">Location Preferences</h2>
			<p class="text-sm text-gray-600">Your location and preferred work cities</p>
		</div>
	</div>

	<div class="grid md:grid-cols-2 gap-5">
		<!-- Country -->
		<div>
			<label for="country" class="block text-sm font-medium text-gray-700 mb-2"> Country </label>
			<select
				id="country"
				bind:value={selectedCountryId}
				onchange={handleCountryChange}
				disabled={loadingCountries}
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
			>
				<option value={undefined}>Select Country</option>
				{#each countries as country}
					<option value={country.id}>{country.name}</option>
				{/each}
			</select>
		</div>

		<!-- State -->
		<div>
			<label for="state" class="block text-sm font-medium text-gray-700 mb-2"> State </label>
			<select
				id="state"
				bind:value={selectedStateId}
				onchange={handleStateChange}
				disabled={!selectedCountryId || loadingStates}
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
			>
				<option value={undefined}>
					{selectedCountryId ? 'Select State' : 'Select Country first'}
				</option>
				{#each states as state}
					<option value={state.id}>{state.name}</option>
				{/each}
			</select>
		</div>

		<!-- City -->
		<div>
			<label for="city" class="block text-sm font-medium text-gray-700 mb-2"> City </label>
			<select
				id="city"
				bind:value={selectedCityId}
				onchange={handleCityChange}
				disabled={!selectedStateId || loadingCities}
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
			>
				<option value={undefined}>{selectedStateId ? 'Select City' : 'Select State first'}</option>
				{#each cities as city}
					<option value={city.id}>{city.name}</option>
				{/each}
			</select>
		</div>

		<!-- Current City -->
		<div>
			<label for="current_city" class="block text-sm font-medium text-gray-700 mb-2">
				Current City
			</label>
			<select
				id="current_city"
				bind:value={selectedCurrentCityId}
				onchange={handleCurrentCityChange}
				disabled={!selectedStateId || loadingCities}
				class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none appearance-none disabled:bg-gray-100 disabled:cursor-not-allowed"
			>
				<option value={undefined}>{selectedStateId ? 'Select Current City' : 'Select State first'}</option>
				{#each cities as city}
					<option value={city.id}>{city.name}</option>
				{/each}
			</select>
		</div>

		<!-- Preferred Cities (multi-select with search) -->
		<div class="md:col-span-2">
			<label for="preferred_cities" class="block text-sm font-medium text-gray-700 mb-2">
				Preferred Cities (Search and Select Multiple)
			</label>

			<!-- Selected cities display -->
			{#if selectedPreferredCityIds.length > 0}
				<div class="flex flex-wrap gap-2 mb-3">
					{#each selectedPreferredCityIds as cityId, index}
						<span
							class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-medium border border-primary-200"
						>
							{selectedPreferredCityNames[index] || `City ${cityId}`}
							<button
								type="button"
								onclick={() => removePreferredCity(cityId)}
								class="hover:bg-primary-100 rounded-full p-0.5 transition-colors"
							>
								<X size={14} />
							</button>
						</span>
					{/each}
				</div>
			{/if}

			<!-- Search input -->
			<div class="relative">
				<input
					type="text"
					id="preferred_cities"
					bind:value={preferredCitySearch}
					onfocus={() => (showPreferredCityDropdown = true)}
					onblur={() => setTimeout(() => (showPreferredCityDropdown = false), 200)}
					placeholder="Search cities... (type at least 2 characters)"
					class="w-full px-4 py-3 border border-gray-200 rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none"
				/>

				{#if loadingPreferredCities}
					<div class="absolute right-3 top-3.5">
						<Loader size={16} class="animate-spin text-gray-400" />
					</div>
				{/if}

				<!-- Dropdown -->
				{#if showPreferredCityDropdown && preferredCities.length > 0}
					<div
						class="absolute z-10 w-full mt-2 bg-white border border-gray-200 rounded-xl elevation-2 max-h-60 overflow-y-auto"
					>
						{#each preferredCities as city}
							<button
								type="button"
								onclick={() => togglePreferredCity(city.id)}
								class="w-full text-left px-4 py-3 hover:bg-primary-50 transition-colors flex items-center justify-between"
							>
								<div>
									<div class="font-medium text-gray-900">{city.name}</div>
									<div class="text-xs text-gray-500">
										{city.state_name}, {city.country_name}
									</div>
								</div>
								{#if selectedPreferredCityIds.includes(city.id)}
									<span class="text-primary-600 font-medium">✓</span>
								{/if}
							</button>
						{/each}
					</div>
				{/if}
			</div>

			<p class="mt-2 text-xs text-gray-500">
				Search for cities you're willing to work in. You can select multiple cities.
			</p>
		</div>
	</div>
</div>
