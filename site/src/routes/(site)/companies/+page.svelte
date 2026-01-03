<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    Search,
    ChevronDown,
    ChevronRight,
    MapPin,
    Building2,
    Users,
    Factory,
    Briefcase,
    Filter,
    SlidersHorizontal,
    X,
    Sparkles,
    TrendingUp,
    ChevronLeft
  } from '@lucide/svelte';
  import CollapsibleFilterSection from '$lib/components/CollapsibleFilterSection.svelte';
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

  // Mobile filter toggle
  let showFiltersMobile = $state(false);

  // Search state
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

  // Count active filters
  const activeFilterCount = $derived(
    companyTypeOptions.filter(opt => opt.checked).length +
    locationOptions.filter(opt => opt.checked).length +
    industryOptions.filter(opt => opt.checked).length +
    sizeOptions.filter(opt => opt.checked).length
  );

  const hasActiveFilters = $derived(activeFilterCount > 0);

  // Functions
  function toggleFilter(options: FilterOption[], value: string): void {
    const option = options.find(opt => opt.value === value);
    if (option) {
      option.checked = !option.checked;
      navigateWithFilters();
    }
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
    showFiltersMobile = false;
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

  function nextPage(): void {
    if (currentPage < totalPages) {
      goToPage(currentPage + 1);
    }
  }

  function prevPage(): void {
    if (currentPage > 1) {
      goToPage(currentPage - 1);
    }
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

  function toggleFiltersMobile(): void {
    showFiltersMobile = !showFiltersMobile;
  }
</script>

<svelte:head>
  <title>Top Companies Hiring in India - PeelJobs</title>
  <meta name="description" content="Discover top companies hiring in India. Browse {totalCompanies.toLocaleString()} companies by industry, location, and company type." />
</svelte:head>

<div class="min-h-screen bg-surface">
  <!-- Hero Section -->
  <section class="bg-[#1D2226] relative overflow-hidden">
    <!-- Decorative Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-primary/10 rounded-full blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-12 lg:py-16 relative">
      <div class="text-center max-w-3xl mx-auto">
        <div class="inline-flex items-center gap-2 px-4 py-2 bg-primary/20 border border-primary/30 rounded-full text-white/80 text-sm font-medium mb-6 animate-fade-in-down" style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;">
          <Sparkles class="w-4 h-4" />
          <span>{totalCompanies.toLocaleString()} Companies Listed</span>
        </div>

        <h1 class="text-3xl md:text-4xl lg:text-5xl font-semibold text-white tracking-tight mb-4 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms; animation-fill-mode: forwards;">
          Discover Top Companies
        </h1>

        <p class="text-lg text-gray-400 animate-fade-in-up" style="opacity: 0; animation-delay: 300ms; animation-fill-mode: forwards;">
          Explore companies hiring now and find your perfect workplace
        </p>
      </div>
    </div>
  </section>

  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-8">
    <!-- Mobile Filter Toggle -->
    <div class="lg:hidden mb-6 flex justify-between items-center">
      <button
        onclick={toggleFiltersMobile}
        class="flex items-center gap-2 h-10 px-4 bg-primary hover:bg-primary-hover rounded-full text-white font-medium transition-colors shadow-sm"
      >
        <SlidersHorizontal class="w-5 h-5" />
        {showFiltersMobile ? 'Hide Filters' : 'Filters'}
        {#if activeFilterCount > 0}
          <span class="bg-white text-primary text-xs px-2 py-0.5 rounded-full font-semibold">{activeFilterCount}</span>
        {/if}
      </button>
      <div class="flex items-center gap-2 text-sm text-muted">
        <TrendingUp class="w-4 h-4 text-primary" />
        <span class="font-medium text-black">{totalCompanies.toLocaleString()}</span> companies
      </div>
    </div>

    <div class="flex flex-col lg:flex-row gap-8">
      <!-- Filter Sidebar -->
      <aside class="{showFiltersMobile ? 'block' : 'hidden'} lg:block lg:w-72 flex-shrink-0">
        <div class="bg-white rounded-lg shadow-sm border border-border overflow-hidden lg:sticky lg:top-24">
          <!-- Filter Header -->
          <div class="flex justify-between items-center px-4 py-3 border-b border-border bg-surface">
            <h2 class="text-sm font-semibold text-black flex items-center gap-2">
              <div class="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <Filter class="w-4 h-4 text-primary" />
              </div>
              Filters
            </h2>
            {#if hasActiveFilters}
              <button
                onclick={clearAllFilters}
                class="text-sm text-primary hover:text-primary-hover font-medium px-3 py-1 rounded-full hover:bg-primary/5 transition-colors"
              >
                Clear ({activeFilterCount})
              </button>
            {/if}
          </div>

          <div class="p-4 space-y-1">
            <!-- Company Type Filter -->
            {#if companyTypeOptions.length > 0}
              <CollapsibleFilterSection
                title="Company Type"
                hasActiveFilter={companyTypeOptions.some(opt => opt.checked)}
              >
                <div class="space-y-1">
                  {#each companyTypeOptions as option (option.value)}
                    <label class="flex items-center gap-3 cursor-pointer py-2 px-2 -mx-2 rounded-lg hover:bg-surface transition-colors">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleFilter(companyTypeOptions, option.value)}
                        class="w-4 h-4 text-primary border-border rounded focus:ring-primary cursor-pointer"
                      />
                      <span class="text-black flex-1 text-sm">{option.label}</span>
                      <span class="text-muted text-xs font-medium bg-surface px-2 py-0.5 rounded">
                        {option.count}
                      </span>
                    </label>
                  {/each}
                </div>
              </CollapsibleFilterSection>
            {/if}

            <!-- Location Filter -->
            {#if locationOptions.length > 0}
              <CollapsibleFilterSection
                title="Location"
                hasActiveFilter={locationOptions.some(opt => opt.checked)}
              >
                <!-- Search box -->
                <div class="relative mb-3">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search class="w-4 h-4 text-muted" />
                  </span>
                  <input
                    type="text"
                    bind:value={locationSearchTerm}
                    placeholder="Search location..."
                    class="w-full h-8 pl-9 pr-3 bg-surface border border-border rounded-lg focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 text-sm text-black placeholder-muted transition-all outline-none"
                  />
                </div>
                <div class="space-y-1 max-h-60 overflow-y-auto">
                  {#each filteredLocationOptions.slice(0, 10) as option (option.value)}
                    <label class="flex items-center gap-3 cursor-pointer py-2 px-2 -mx-2 rounded-lg hover:bg-surface transition-colors">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleFilter(locationOptions, option.value)}
                        class="w-4 h-4 text-primary border-border rounded focus:ring-primary cursor-pointer"
                      />
                      <span class="text-black flex-1 text-sm">{option.label}</span>
                      <span class="text-muted text-xs font-medium bg-surface px-2 py-0.5 rounded">
                        {option.count}
                      </span>
                    </label>
                  {/each}
                </div>
                {#if filteredLocationOptions.length > 10}
                  <p class="mt-2 text-xs text-muted">
                    Use search to find more locations
                  </p>
                {/if}
              </CollapsibleFilterSection>
            {/if}

            <!-- Industry Filter -->
            {#if industryOptions.length > 0}
              <CollapsibleFilterSection
                title="Industry"
                hasActiveFilter={industryOptions.some(opt => opt.checked)}
              >
                <!-- Search box -->
                <div class="relative mb-3">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search class="w-4 h-4 text-muted" />
                  </span>
                  <input
                    type="text"
                    bind:value={industrySearchTerm}
                    placeholder="Search industry..."
                    class="w-full h-8 pl-9 pr-3 bg-surface border border-border rounded-lg focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 text-sm text-black placeholder-muted transition-all outline-none"
                  />
                </div>
                <div class="space-y-1 max-h-60 overflow-y-auto">
                  {#each filteredIndustryOptions.slice(0, 10) as option (option.value)}
                    <label class="flex items-center gap-3 cursor-pointer py-2 px-2 -mx-2 rounded-lg hover:bg-surface transition-colors">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleFilter(industryOptions, option.value)}
                        class="w-4 h-4 text-primary border-border rounded focus:ring-primary cursor-pointer"
                      />
                      <span class="text-black flex-1 text-sm">{option.label}</span>
                      <span class="text-muted text-xs font-medium bg-surface px-2 py-0.5 rounded">
                        {option.count}
                      </span>
                    </label>
                  {/each}
                </div>
                {#if filteredIndustryOptions.length > 10}
                  <p class="mt-2 text-xs text-muted">
                    Use search to find more industries
                  </p>
                {/if}
              </CollapsibleFilterSection>
            {/if}

            <!-- Company Size Filter -->
            {#if sizeOptions.length > 0}
              <CollapsibleFilterSection
                title="Company Size"
                hasActiveFilter={sizeOptions.some(opt => opt.checked)}
              >
                <div class="space-y-1">
                  {#each sizeOptions as option (option.value)}
                    <label class="flex items-center gap-3 cursor-pointer py-2 px-2 -mx-2 rounded-lg hover:bg-surface transition-colors">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleFilter(sizeOptions, option.value)}
                        class="w-4 h-4 text-primary border-border rounded focus:ring-primary cursor-pointer"
                      />
                      <span class="text-black flex-1 text-sm">{option.label}</span>
                      <span class="text-muted text-xs font-medium bg-surface px-2 py-0.5 rounded">
                        {option.count}
                      </span>
                    </label>
                  {/each}
                </div>
              </CollapsibleFilterSection>
            {/if}
          </div>
        </div>
      </aside>

      <!-- Companies Grid -->
      <main class="flex-1 min-w-0">
        <!-- Results Header -->
        <div class="hidden lg:flex justify-between items-center mb-6">
          <h2 class="text-xl font-semibold text-black flex items-center gap-3">
            Companies
            <span class="text-sm font-normal text-muted">({totalCompanies.toLocaleString()} results)</span>
          </h2>
        </div>

        <!-- Applied Filters -->
        {#if appliedFilters().length > 0}
          <div class="mb-6 flex flex-wrap items-center gap-2">
            {#each appliedFilters() as filter}
              <button
                onclick={() => clearFilter(filter.type as any)}
                class="inline-flex items-center gap-1.5 px-3 py-1.5 bg-primary/10 text-primary rounded-full text-sm font-medium hover:bg-primary/20 transition-colors group"
              >
                <span>{filter.label}</span>
                <X class="w-3.5 h-3.5 group-hover:text-primary-hover" />
              </button>
            {/each}
            <button
              onclick={clearAllFilters}
              class="text-sm text-muted hover:text-black font-medium px-2 py-1"
            >
              Clear all
            </button>
          </div>
        {/if}

        {#if error}
          <!-- Error State -->
          <div class="bg-white rounded-lg shadow-sm border border-border p-12 text-center">
            <div class="w-16 h-16 rounded-lg bg-error-light flex items-center justify-center mx-auto mb-4">
              <X class="w-8 h-8 text-error" />
            </div>
            <h3 class="text-xl font-semibold text-black mb-2">Something went wrong</h3>
            <p class="text-muted mb-6">{error}</p>
            <button
              onclick={() => window.location.reload()}
              class="h-10 px-6 bg-primary hover:bg-primary-hover text-white rounded-full font-medium transition-colors shadow-sm"
            >
              Try Again
            </button>
          </div>
        {:else if companies.length > 0}
          <!-- Companies Grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {#each companies as company, index (company.id)}
              <article
                class="group bg-white rounded-lg overflow-hidden transition-all duration-300 hover:shadow-md border border-border hover:border-primary/30"
                style="animation: fade-in-up 0.5s ease forwards; animation-delay: {Math.min(index * 50, 300)}ms; opacity: 0;"
              >
                <a
                  href="/companies/{company.slug}/"
                  class="block p-4"
                >
                  <div class="flex gap-4">
                    <!-- Company Logo -->
                    <div class="flex-shrink-0">
                      {#if company.logo}
                        <div class="w-14 h-14 rounded bg-surface border border-border overflow-hidden flex items-center justify-center p-2">
                          <img
                            src={company.logo}
                            alt="{company.name} logo"
                            class="w-full h-full object-contain"
                            loading="lazy"
                          />
                        </div>
                      {:else}
                        <div class="w-14 h-14 rounded bg-primary/10 flex items-center justify-center">
                          <Building2 class="w-7 h-7 text-primary" />
                        </div>
                      {/if}
                    </div>

                    <!-- Company Info -->
                    <div class="flex-1 min-w-0">
                      <h3 class="text-base font-semibold text-black group-hover:text-primary transition-colors mb-2 line-clamp-1">
                        {company.name}
                      </h3>

                      <!-- Company Details -->
                      <div class="flex flex-wrap items-center gap-2 text-xs mb-3">
                        {#if company.company_type}
                          <span class="inline-flex items-center gap-1 px-2 py-1 bg-surface text-muted rounded">
                            <Building2 class="w-3 h-3" />
                            {company.company_type}
                          </span>
                        {/if}
                        {#if company.industry_name}
                          <span class="inline-flex items-center gap-1 px-2 py-1 bg-primary/10 text-primary rounded">
                            <Factory class="w-3 h-3" />
                            {company.industry_name}
                          </span>
                        {/if}
                      </div>

                      <div class="flex flex-wrap items-center gap-3 text-xs text-muted">
                        {#if company.size}
                          <span class="flex items-center gap-1">
                            <Users class="w-3.5 h-3.5" />
                            {company.size}
                          </span>
                        {/if}
                        {#if company.nature_of_business && company.nature_of_business.length > 0}
                          <span class="flex items-center gap-1">
                            <Briefcase class="w-3.5 h-3.5" />
                            {company.nature_of_business[0]}
                          </span>
                        {/if}
                      </div>
                    </div>

                    <!-- Arrow -->
                    <div class="flex-shrink-0 self-center">
                      <div class="w-8 h-8 rounded-full bg-surface flex items-center justify-center group-hover:bg-primary/10 transition-colors">
                        <ChevronRight class="w-4 h-4 text-muted group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  </div>
                </a>
              </article>
            {/each}
          </div>

          <!-- Pagination -->
          {#if totalPages > 1}
            <div class="mt-10 flex justify-center">
              <div class="inline-flex items-center gap-1 bg-white rounded-lg shadow-sm border border-border p-2">
                <button
                  onclick={prevPage}
                  disabled={currentPage === 1}
                  class="flex items-center gap-1 h-10 px-4 text-sm font-medium text-black rounded-lg hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft class="w-4 h-4" />
                  <span class="hidden sm:inline">Previous</span>
                </button>

                <div class="flex gap-1 px-2">
                  {#each getPageNumbers() as pageNum}
                    <button
                      onclick={() => goToPage(pageNum)}
                      class="w-10 h-10 flex items-center justify-center text-sm font-medium rounded-lg transition-all {pageNum === currentPage ? 'bg-primary text-white shadow-sm' : 'text-black hover:bg-surface'}"
                    >
                      {pageNum}
                    </button>
                  {/each}
                </div>

                <button
                  onclick={nextPage}
                  disabled={currentPage === totalPages}
                  class="flex items-center gap-1 h-10 px-4 text-sm font-medium text-black rounded-lg hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <span class="hidden sm:inline">Next</span>
                  <ChevronRight class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div class="mt-4 text-center text-sm text-muted">
              Page {currentPage} of {totalPages}
            </div>
          {/if}
        {:else}
          <!-- Empty State -->
          <div class="bg-white rounded-lg shadow-sm border border-border p-12 text-center">
            <div class="w-20 h-20 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-6">
              <Building2 class="w-10 h-10 text-primary" />
            </div>
            <h3 class="text-xl font-semibold text-black mb-2">No Companies Found</h3>
            <p class="text-muted mb-8 max-w-md mx-auto">
              We couldn't find any companies matching your criteria. Try adjusting your filters.
            </p>
            <button
              onclick={clearAllFilters}
              class="h-10 px-6 bg-primary hover:bg-primary-hover text-white rounded-full font-medium transition-colors shadow-sm hover:shadow-md"
            >
              Clear All Filters
            </button>
          </div>
        {/if}
      </main>
    </div>
  </div>
</div>
