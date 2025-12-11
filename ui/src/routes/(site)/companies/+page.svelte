<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    Search,
    ChevronDown,
    ChevronRight,
    MapPin,
    Building,
    Users,
    Factory,
    Briefcase,
    Calendar,
    X
  } from '@lucide/svelte';
  import type { PageData } from './$types';
  import type { Company as APICompany } from '$lib/api/companies';

  // Types
  interface FilterOption {
    label: string;
    value: string;
    count: number;
    checked: boolean;
  }

  interface Props {
    data: PageData;
  }

  let { data }: Props = $props();

  // Initialize from server data - use $derived for reactive values
  let companies = $state<APICompany[]>([]);
  const totalCompanies = $derived(data.totalCompanies || 0);
  const totalPages = $derived(data.totalPages || 0);
  let currentPage = $state(1);
  const error = $derived(data.error);

  // Sync companies and currentPage when server data changes
  $effect(() => {
    companies = data.companies || [];
    currentPage = data.currentPage || 1;
  });

  // Filter state
  let selectedCategory = $state<string | null>(null);

  // Filter options with collapsible state
  let companyTypeExpanded = $state(true);
  let locationExpanded = $state(false);
  let industryExpanded = $state(false);
  let sizeExpanded = $state(false);

  let locationSearchTerm = $state('');
  let industrySearchTerm = $state('');

  // Filter options state
  let companyTypeOptions = $state<FilterOption[]>([]);
  let locationOptions = $state<FilterOption[]>([]);
  let industryOptions = $state<FilterOption[]>([]);
  let sizeOptions = $state<FilterOption[]>([]);

  // Initialize filter options from server data
  $effect(() => {
    const initialParams = data.initialParams || {};

    companyTypeOptions = (data.filterOptions?.company_types || []).map(opt => ({
      ...opt,
      checked: initialParams.company_type === opt.value
    }));

    locationOptions = (data.filterOptions?.locations || []).map(opt => ({
      ...opt,
      checked: initialParams.location === opt.value
    }));

    industryOptions = (data.filterOptions?.industries || []).map(opt => ({
      ...opt,
      checked: initialParams.industry === opt.value
    }));

    sizeOptions = (data.filterOptions?.sizes || []).map(opt => ({
      ...opt,
      checked: initialParams.size === opt.value
    }));
  });

  // Track if we've mounted
  let hasMounted = $state(false);
  let isSyncingFromUrl = $state(false);

  onMount(() => {
    hasMounted = true;
  });

  const displayedCompanies = $derived(companies.length);

  // Filtered location options based on search
  const filteredLocationOptions = $derived(
    locationSearchTerm
      ? locationOptions.filter(opt =>
          opt.label.toLowerCase().includes(locationSearchTerm.toLowerCase())
        )
      : locationOptions
  );

  // Filtered industry options based on search
  const filteredIndustryOptions = $derived(
    industrySearchTerm
      ? industryOptions.filter(opt =>
          opt.label.toLowerCase().includes(industrySearchTerm.toLowerCase())
        )
      : industryOptions
  );

  // Functions
  function toggleFilter(options: FilterOption[], value: string): void {
    const option = options.find(opt => opt.value === value);
    if (option) {
      option.checked = !option.checked;
      navigateWithFilters();
    }
  }

  function formatCount(count: number): string {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}K+`;
    }
    return count.toString();
  }

  // Navigate with filters
  let navigationTimeout: ReturnType<typeof setTimeout>;
  function navigateWithFilters(delay: number = 500) {
    if (!hasMounted) return;

    clearTimeout(navigationTimeout);
    navigationTimeout = setTimeout(() => {
      const params = new URLSearchParams();

      // Add company type filter (single select)
      const selectedCompanyType = companyTypeOptions.find(opt => opt.checked);
      if (selectedCompanyType) {
        params.set('company_type', selectedCompanyType.value);
      }

      // Add size filter (single select)
      const selectedSize = sizeOptions.find(opt => opt.checked);
      if (selectedSize) {
        params.set('size', selectedSize.value);
      }

      // Add location filter (single select)
      const selectedLocation = locationOptions.find(opt => opt.checked);
      if (selectedLocation) {
        params.set('location', selectedLocation.value);
      }

      // Add industry filter (single select)
      const selectedIndustry = industryOptions.find(opt => opt.checked);
      if (selectedIndustry) {
        params.set('industry', selectedIndustry.value);
      }

      // Add pagination
      if (currentPage > 1) params.set('page', currentPage.toString());

      // Navigate to new URL (triggers SSR)
      const queryString = params.toString();
      const newUrl = queryString ? `/companies/?${queryString}` : '/companies/';

      // Only navigate if URL actually changed
      if ($page.url.pathname + ($page.url.search || '') !== newUrl) {
        goto(newUrl);
      }
    }, delay);
  }

  function clearFilter(filterType: 'company_type' | 'size' | 'location' | 'industry'): void {
    switch (filterType) {
      case 'company_type':
        companyTypeOptions.forEach(opt => opt.checked = false);
        break;
      case 'size':
        sizeOptions.forEach(opt => opt.checked = false);
        break;
      case 'location':
        locationOptions.forEach(opt => opt.checked = false);
        break;
      case 'industry':
        industryOptions.forEach(opt => opt.checked = false);
        break;
    }
    navigateWithFilters(0);
  }

  function clearAllFilters(): void {
    companyTypeOptions.forEach(opt => opt.checked = false);
    sizeOptions.forEach(opt => opt.checked = false);
    locationOptions.forEach(opt => opt.checked = false);
    industryOptions.forEach(opt => opt.checked = false);
    navigateWithFilters(0);
  }

  // Get applied filters for display
  const appliedFilters = $derived(() => {
    const filters: Array<{ type: string; label: string; value: string }> = [];

    const selectedCompanyType = companyTypeOptions.find(opt => opt.checked);
    if (selectedCompanyType) {
      filters.push({ type: 'company_type', label: selectedCompanyType.label, value: selectedCompanyType.value });
    }

    const selectedSize = sizeOptions.find(opt => opt.checked);
    if (selectedSize) {
      filters.push({ type: 'size', label: `Size: ${selectedSize.label}`, value: selectedSize.value });
    }

    const selectedLocation = locationOptions.find(opt => opt.checked);
    if (selectedLocation) {
      filters.push({ type: 'location', label: selectedLocation.label, value: selectedLocation.value });
    }

    const selectedIndustry = industryOptions.find(opt => opt.checked);
    if (selectedIndustry) {
      filters.push({ type: 'industry', label: selectedIndustry.label, value: selectedIndustry.value });
    }

    return filters;
  });

  function goToPage(page: number): void {
    currentPage = page;
    navigateWithFilters(0);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function getPageNumbers(): number[] {
    const maxPagesToShow = 5;
    const pages: number[] = [];

    if (totalPages <= maxPagesToShow) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      const startPage = Math.max(1, currentPage - 2);
      const endPage = Math.min(totalPages, startPage + maxPagesToShow - 1);

      for (let i = startPage; i <= endPage; i++) {
        pages.push(i);
      }
    }

    return pages;
  }

</script>

<svelte:head>
  <title>Top Companies Hiring in India - PeelJobs</title>
  <meta name="description" content="Discover top companies hiring in India. Browse {totalCompanies.toLocaleString()} companies by industry, location, and company type." />
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Page Header -->
  <div class="bg-white border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 py-6 md:py-8">
      <h1 class="text-xl md:text-2xl font-bold text-gray-900">Top companies hiring now</h1>
    </div>
  </div>

  <!-- Category Chips - Horizontal Scroll (TODO: Connect to real data) -->
  <!-- Temporarily disabled until we have category data from backend
  <div class="bg-white border-b border-gray-200">
    <div class="max-w-7xl mx-auto px-4 py-4">
      <div class="relative">
        <div class="flex gap-3 overflow-x-auto pb-2 scrollbar-hide snap-x snap-mandatory">
          ...
        </div>
      </div>
    </div>
  </div>
  -->

  <!-- Main Content -->
  <div class="max-w-7xl mx-auto px-4 py-6 md:py-8">
    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Filters Sidebar -->
      <aside class="lg:w-80 flex-shrink-0">
        <div class="bg-white rounded-lg border border-gray-200 sticky top-6">
          <div class="p-4 border-b border-gray-200">
            <h2 class="text-base font-semibold text-gray-900">All Filters</h2>
          </div>

          <div class="divide-y divide-gray-200">
            <!-- Company Type Filter -->
            <div class="p-4">
              <button
                onclick={() => companyTypeExpanded = !companyTypeExpanded}
                class="flex items-center justify-between w-full text-left"
              >
                <h3 class="text-sm font-semibold text-gray-900">Company type</h3>
                <ChevronDown
                  size={16}
                  class="text-gray-500 transition-transform {companyTypeExpanded ? 'rotate-180' : ''}"
                />
              </button>
              {#if companyTypeExpanded}
                <div class="mt-3 space-y-2">
                  {#each companyTypeOptions as option (option.value)}
                    <label class="flex items-start gap-2 cursor-pointer text-sm hover:bg-gray-50 -mx-2 px-2 py-1.5 rounded">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleFilter(companyTypeOptions, option.value)}
                        class="mt-0.5 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                      />
                      <span class="flex-1 text-gray-700">{option.label}</span>
                      <span class="text-gray-500 text-xs">({option.count})</span>
                    </label>
                  {/each}
                </div>
              {/if}
            </div>

            <!-- Location Filter -->
            <div class="p-4">
              <button
                onclick={() => locationExpanded = !locationExpanded}
                class="flex items-center justify-between w-full text-left"
              >
                <h3 class="text-sm font-semibold text-gray-900">Location</h3>
                <ChevronDown
                  size={16}
                  class="text-gray-500 transition-transform {locationExpanded ? 'rotate-180' : ''}"
                />
              </button>
              {#if locationExpanded}
                <div class="mt-3">
                  <!-- Search box -->
                  <div class="relative mb-3">
                    <Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      bind:value={locationSearchTerm}
                      placeholder="Search Location"
                      class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div class="space-y-2 max-h-60 overflow-y-auto">
                    {#each filteredLocationOptions as option (option.value)}
                      <label class="flex items-start gap-2 cursor-pointer text-sm hover:bg-gray-50 -mx-2 px-2 py-1.5 rounded">
                        <input
                          type="checkbox"
                          checked={option.checked}
                          onchange={() => toggleFilter(locationOptions, option.value)}
                          class="mt-0.5 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                        />
                        <span class="flex-1 text-gray-700">{option.label}</span>
                        <span class="text-gray-500 text-xs">({option.count})</span>
                      </label>
                    {/each}
                  </div>
                  <button class="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                    +90 more
                  </button>
                </div>
              {/if}
            </div>

            <!-- Industry Filter -->
            <div class="p-4">
              <button
                onclick={() => industryExpanded = !industryExpanded}
                class="flex items-center justify-between w-full text-left"
              >
                <h3 class="text-sm font-semibold text-gray-900">Industry</h3>
                <ChevronDown
                  size={16}
                  class="text-gray-500 transition-transform {industryExpanded ? 'rotate-180' : ''}"
                />
              </button>
              {#if industryExpanded}
                <div class="mt-3">
                  <!-- Search box -->
                  <div class="relative mb-3">
                    <Search size={16} class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                      type="text"
                      bind:value={industrySearchTerm}
                      placeholder="Search Industry"
                      class="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div class="space-y-2 max-h-60 overflow-y-auto">
                    {#each filteredIndustryOptions as option (option.value)}
                      <label class="flex items-start gap-2 cursor-pointer text-sm hover:bg-gray-50 -mx-2 px-2 py-1.5 rounded">
                        <input
                          type="checkbox"
                          checked={option.checked}
                          onchange={() => toggleFilter(industryOptions, option.value)}
                          class="mt-0.5 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                        />
                        <span class="flex-1 text-gray-700">{option.label}</span>
                        <span class="text-gray-500 text-xs">({option.count})</span>
                      </label>
                    {/each}
                  </div>
                  <button class="mt-2 text-sm text-blue-600 hover:text-blue-700 font-medium">
                    +72 more
                  </button>
                </div>
              {/if}
            </div>

            <!-- Company Size Filter -->
            {#if sizeOptions.length > 0}
              <div class="p-4">
                <button
                  onclick={() => sizeExpanded = !sizeExpanded}
                  class="flex items-center justify-between w-full text-left"
                >
                  <h3 class="text-sm font-semibold text-gray-900">Company Size</h3>
                  <ChevronDown
                    size={16}
                    class="text-gray-500 transition-transform {sizeExpanded ? 'rotate-180' : ''}"
                  />
                </button>
                {#if sizeExpanded}
                  <div class="mt-3 space-y-2">
                    {#each sizeOptions as option (option.value)}
                      <label class="flex items-start gap-2 cursor-pointer text-sm hover:bg-gray-50 -mx-2 px-2 py-1.5 rounded">
                        <input
                          type="checkbox"
                          checked={option.checked}
                          onchange={() => toggleFilter(sizeOptions, option.value)}
                          class="mt-0.5 w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                        />
                        <span class="flex-1 text-gray-700">{option.label}</span>
                        <span class="text-gray-500 text-xs">({option.count})</span>
                      </label>
                    {/each}
                  </div>
                {/if}
              </div>
            {/if}
          </div>
        </div>
      </aside>

      <!-- Companies Grid -->
      <main class="flex-1">
        <!-- Applied Filters -->
        {#if appliedFilters().length > 0}
          <div class="mb-4 bg-white rounded-lg border border-gray-200 p-4">
            <div class="flex flex-wrap items-center gap-3">
              <span class="text-sm font-medium text-gray-700">Applied Filters:</span>

              <!-- Filter Tags -->
              <div class="flex flex-wrap gap-2">
                {#each appliedFilters() as filter}
                  <button
                    onclick={(e) => { e.stopPropagation(); clearFilter(filter.type as any); }}
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-700 rounded-full text-sm font-medium hover:bg-blue-100 transition-colors group"
                  >
                    <span>{filter.label}</span>
                    <X size={14} class="group-hover:text-blue-900" />
                  </button>
                {/each}
              </div>

              <!-- Clear All Button -->
              <button
                onclick={clearAllFilters}
                class="ml-auto text-sm text-red-600 hover:text-red-700 font-medium hover:underline"
              >
                Clear all filters
              </button>
            </div>
          </div>
        {/if}

        <div class="mb-6">
          <h2 class="text-lg md:text-xl font-semibold text-gray-900">
            Showing {totalCompanies.toLocaleString()} companies
          </h2>
        </div>

        <!-- Companies List -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          {#each companies as company (company.id)}
            <article class="bg-white rounded-lg border border-gray-200 hover:border-blue-300 transition-all duration-200 hover:shadow-md relative group">
              <a
                href="/companies/{company.slug}/"
                class="block p-4 md:p-5 after:absolute after:inset-0"
              >
                <div class="flex gap-4">
                  <!-- Company Logo -->
                  <div class="flex-shrink-0">
                    <div class="w-16 h-16 md:w-20 md:h-20 bg-gray-50 rounded border border-gray-200 overflow-hidden flex items-center justify-center p-2">
                      <img
                        src={company.logo}
                        alt="{company.name} logo"
                        class="w-full h-full object-contain"
                        loading="lazy"
                      />
                    </div>
                  </div>

                  <!-- Company Info -->
                  <div class="flex-1 min-w-0">
                    <h3 class="text-base md:text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors mb-2 line-clamp-1">
                      {company.name}
                    </h3>

                    <!-- Company Details -->
                    <div class="flex flex-wrap gap-x-2 gap-y-1 text-xs text-gray-600">
                      <span class="after:content-['•'] after:ml-2 after:text-gray-400 last:after:content-['']">
                        {company.company_type}
                      </span>
                      <span class="after:content-['•'] after:ml-2 after:text-gray-400 last:after:content-['']">
                        {company.industry_name}
                      </span>
                      {#if company.size}
                        <span class="after:content-['•'] after:ml-2 after:text-gray-400 last:after:content-['']">
                          {company.size}
                        </span>
                      {/if}
                      {#if company.nature_of_business && company.nature_of_business.length > 0}
                        {#each company.nature_of_business as business}
                          <span class="after:content-['•'] after:ml-2 after:text-gray-400 last:after:content-['']">
                            {business}
                          </span>
                        {/each}
                      {/if}
                    </div>
                  </div>
                </div>
              </a>

              <!-- Arrow icon -->
              <div class="absolute top-4 right-4 md:top-5 md:right-5 pointer-events-none">
                <ChevronRight size={20} class="text-gray-400 group-hover:text-blue-600 transition-colors" />
              </div>
            </article>
          {/each}
        </div>

        <!-- Pagination -->
        {#if totalPages > 1}
          <div class="mt-8 flex items-center justify-center gap-2">
            <button
              onclick={() => goToPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              class="px-4 py-2 text-sm border border-gray-300 rounded bg-white hover:bg-gray-50 text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:text-gray-400"
            >
              Previous
            </button>
            <div class="flex gap-1">
              {#each getPageNumbers() as pageNum}
                <button
                  onclick={() => goToPage(pageNum)}
                  class="{pageNum === currentPage ? 'bg-blue-600 text-white' : 'bg-white hover:bg-gray-50 text-gray-700'} px-3 py-2 text-sm border border-gray-300 rounded transition-colors"
                >
                  {pageNum}
                </button>
              {/each}
            </div>
            <button
              onclick={() => goToPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              class="px-4 py-2 text-sm border border-gray-300 rounded bg-white hover:bg-gray-50 text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed disabled:text-gray-400"
            >
              Next
            </button>
          </div>

          <div class="mt-4 text-center text-sm text-gray-600">
            Page {currentPage} of {totalPages}
          </div>
        {/if}
      </main>
    </div>
  </div>
</div>

<style>
  /* Hide scrollbar but keep functionality */
  :global(.scrollbar-hide::-webkit-scrollbar) {
    display: none;
  }
  :global(.scrollbar-hide) {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }

  .line-clamp-1 {
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
  }
</style>
