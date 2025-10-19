<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Search, Filter, SlidersHorizontal, X, MapPin, Briefcase, DollarSign, Bookmark, Building, Clock, Users, GraduationCap, Factory } from '@lucide/svelte';
  import FilterSection from '$lib/components/FilterSection.svelte';
  import FilterModal from '$lib/components/FilterModal.svelte';
  import { toast } from '$lib/stores/toast';
  import { authStore } from '$lib/stores/auth';
  import { jobsApi } from '$lib/api/jobs';
  import type { Job, FilterOption, JobFilterOptions, JobSearchParams } from '$lib/types/jobs';
  import type { PageData } from './$types';

  interface Props {
    data: PageData;
  }

  let { data }: Props = $props();

  // Initialize from server data (reactive to changes)
  let jobs = $state<Job[]>(data.jobs || []);
  let totalJobs = $derived(data.totalJobs || 0);
  let totalPages = $derived(data.totalPages || 0);
  let currentPage = $state(data.currentPage || 1);
  let filterOptions = $state<JobFilterOptions | null>(data.filterOptions);
  let error = $derived(data.error);

  // Sync jobs when server data changes
  $effect(() => {
    jobs = data.jobs || [];
  });

  // Search and filter state
  let searchTerm = $state('');
  let locationSearchTerm = $state('');
  let showFiltersMobile = $state(false);

  // Modal states
  let showLocationModal = $state(false);
  let showSkillsModal = $state(false);
  let showIndustryModal = $state(false);
  let showEducationModal = $state(false);

  // Salary filter (INR in Lakhs per Annum)
  let salaryMin = $state<number | null>(null);
  let salaryMax = $state<number | null>(null);

  // Experience range filter (in years)
  let experienceMin = $state(0);
  let experienceMax = $state(20);

  // Remote filter
  let isRemote = $state(false);

  // Track if we've mounted (to prevent navigation on initial SSR)
  let hasMounted = $state(false);
  // Track if we're syncing from URL (to prevent triggering navigation)
  let isSyncingFromUrl = $state(false);

  // Filter options with job counts
  let locationOptions = $state<FilterOption[]>([]);
  let skillOptions = $state<FilterOption[]>([]);
  let industryOptions = $state<FilterOption[]>([]);
  let educationOptions = $state<FilterOption[]>([]);
  let jobTypeOptions = $state<{ name: string; value: string; count: number; checked: boolean }[]>([]);

  // Sync currentPage when data changes
  $effect(() => {
    currentPage = data.currentPage || 1;
  });

  // Initialize filter options from server data
  onMount(() => {
    if (filterOptions) {
      locationOptions = filterOptions.locations.map(opt => ({
        ...opt,
        value: opt.slug,
        checked: false
      }));

      skillOptions = filterOptions.skills.map(opt => ({
        ...opt,
        value: opt.slug,
        checked: false
      }));

      industryOptions = filterOptions.industries.map(opt => ({
        ...opt,
        value: opt.slug,
        checked: false
      }));

      educationOptions = filterOptions.education.map(opt => ({
        ...opt,
        value: opt.slug,
        checked: false
      }));

      jobTypeOptions = filterOptions.job_types.map(opt => ({
        name: opt.label,
        value: opt.value,
        count: opt.count,
        checked: false
      }));
    }

    // Mark as mounted
    hasMounted = true;
  });

  // Sync filter state with URL params whenever they change
  $effect(() => {
    const urlParams = $page.url.searchParams;

    // Prevent infinite loop - don't sync if we're already syncing
    isSyncingFromUrl = true;

    // Clear all filters first
    locationOptions.forEach(opt => opt.checked = false);
    skillOptions.forEach(opt => opt.checked = false);
    industryOptions.forEach(opt => opt.checked = false);
    educationOptions.forEach(opt => opt.checked = false);
    jobTypeOptions.forEach(opt => opt.checked = false);

    // Reset search
    searchTerm = urlParams.get('search') || '';

    // Parse multi-select filters
    const selectedLocations = urlParams.getAll('location');
    selectedLocations.forEach(loc => {
      const option = locationOptions.find(opt => opt.slug === loc);
      if (option) option.checked = true;
    });

    const selectedSkills = urlParams.getAll('skills');
    selectedSkills.forEach(skill => {
      const option = skillOptions.find(opt => opt.slug === skill);
      if (option) option.checked = true;
    });

    const selectedIndustries = urlParams.getAll('industry');
    selectedIndustries.forEach(ind => {
      const option = industryOptions.find(opt => opt.slug === ind);
      if (option) option.checked = true;
    });

    const selectedEducation = urlParams.getAll('education');
    selectedEducation.forEach(edu => {
      const option = educationOptions.find(opt => opt.slug === edu);
      if (option) option.checked = true;
    });

    const selectedJobTypes = urlParams.getAll('job_type');
    selectedJobTypes.forEach(type => {
      const option = jobTypeOptions.find(opt => opt.value === type);
      if (option) option.checked = true;
    });

    // Parse numeric filters
    const minSal = urlParams.get('min_salary');
    salaryMin = minSal ? parseFloat(minSal) : null;

    const maxSal = urlParams.get('max_salary');
    salaryMax = maxSal ? parseFloat(maxSal) : null;

    const minExp = urlParams.get('min_experience');
    experienceMin = minExp ? parseInt(minExp, 10) : 0;

    const maxExp = urlParams.get('max_experience');
    experienceMax = maxExp ? parseInt(maxExp, 10) : 20;

    // Parse boolean filters
    const remote = urlParams.get('is_remote');
    isRemote = remote === 'true';

    // Done syncing
    isSyncingFromUrl = false;
  });

  // Filter toggle handlers
  function toggleLocationFilter(value: string) {
    const option = locationOptions.find(opt => opt.value === value);
    if (option) option.checked = !option.checked;
  }

  function toggleSkillFilter(value: string) {
    const option = skillOptions.find(opt => opt.value === value);
    if (option) option.checked = !option.checked;
  }

  function toggleIndustryFilter(value: string) {
    const option = industryOptions.find(opt => opt.value === value);
    if (option) option.checked = !option.checked;
  }

  function toggleEducationFilter(value: string) {
    const option = educationOptions.find(opt => opt.value === value);
    if (option) option.checked = !option.checked;
  }

  function toggleJobTypeFilter(value: string) {
    const option = jobTypeOptions.find(opt => opt.value === value);
    if (option) option.checked = !option.checked;
  }

  // Build API params from current filter state
  function buildApiParams(): JobSearchParams {
    return {
      page: currentPage,
      page_size: 20,
      search: searchTerm || undefined,
      location: locationOptions.filter(opt => opt.checked).map(opt => opt.slug),
      skills: skillOptions.filter(opt => opt.checked).map(opt => opt.slug),
      industry: industryOptions.filter(opt => opt.checked).map(opt => opt.slug),
      education: educationOptions.filter(opt => opt.checked).map(opt => opt.slug),
      job_type: jobTypeOptions.filter(opt => opt.checked).map(opt => opt.value),
      min_salary: salaryMin || undefined,
      max_salary: salaryMax || undefined,
      min_experience: experienceMin > 0 ? experienceMin : undefined,
      max_experience: experienceMax < 20 ? experienceMax : undefined,
      is_remote: isRemote || undefined,
    };
  }

  // Update URL with current filters
  function updateURL() {
    const params = new URLSearchParams();

    if (searchTerm) params.set('search', searchTerm);

    locationOptions.filter(opt => opt.checked).forEach(opt => params.append('location', opt.slug));
    skillOptions.filter(opt => opt.checked).forEach(opt => params.append('skills', opt.slug));
    industryOptions.filter(opt => opt.checked).forEach(opt => params.append('industry', opt.slug));
    educationOptions.filter(opt => opt.checked).forEach(opt => params.append('education', opt.slug));
    jobTypeOptions.filter(opt => opt.checked).forEach(opt => params.append('job_type', opt.value));

    if (salaryMin !== null) params.set('min_salary', salaryMin.toString());
    if (salaryMax !== null) params.set('max_salary', salaryMax.toString());
    if (experienceMin > 0) params.set('min_experience', experienceMin.toString());
    if (experienceMax < 20) params.set('max_experience', experienceMax.toString());
    if (isRemote) params.set('is_remote', 'true');
    if (currentPage > 1) params.set('page', currentPage.toString());

    const url = params.toString() ? `/jobs?${params.toString()}` : '/jobs';
    goto(url, { replaceState: true, noScroll: true, keepFocus: true });
  }

  // Navigate to new URL with filters (triggers SSR reload)
  let navigationTimeout: ReturnType<typeof setTimeout>;
  function navigateWithFilters(delay: number = 500) {
    clearTimeout(navigationTimeout);
    navigationTimeout = setTimeout(() => {
      // Only navigate if we're still on the jobs page
      if (!$page.url.pathname.startsWith('/jobs')) {
        return;
      }

      const params = new URLSearchParams();

      // Add search
      if (searchTerm) params.set('search', searchTerm);

      // Add filters
      locationOptions.filter(opt => opt.checked).forEach(opt => params.append('location', opt.slug));
      skillOptions.filter(opt => opt.checked).forEach(opt => params.append('skills', opt.slug));
      industryOptions.filter(opt => opt.checked).forEach(opt => params.append('industry', opt.slug));
      educationOptions.filter(opt => opt.checked).forEach(opt => params.append('education', opt.slug));
      jobTypeOptions.filter(opt => opt.checked).forEach(opt => params.append('job_type', opt.value));

      // Add numeric filters
      if (salaryMin !== null && salaryMin > 0) params.set('min_salary', salaryMin.toString());
      if (salaryMax !== null && salaryMax > 0) params.set('max_salary', salaryMax.toString());
      if (experienceMin > 0) params.set('min_experience', experienceMin.toString());
      if (experienceMax < 20) params.set('max_experience', experienceMax.toString());

      // Add boolean filters
      if (isRemote) params.set('is_remote', 'true');

      // Add pagination
      if (currentPage > 1) params.set('page', currentPage.toString());

      // Navigate to new URL (triggers SSR)
      const queryString = params.toString();
      const newUrl = queryString ? `/jobs?${queryString}` : '/jobs';

      // Only navigate if URL actually changed
      if ($page.url.pathname + ($page.url.search || '') !== newUrl) {
        goto(newUrl);
      }
    }, delay);
  }

  // Watch for filter changes
  $effect(() => {
    // React to any filter change - need to track checked states
    const selectedLocations = locationOptions.filter(opt => opt.checked).map(opt => opt.slug).join(',');
    const selectedSkills = skillOptions.filter(opt => opt.checked).map(opt => opt.slug).join(',');
    const selectedIndustries = industryOptions.filter(opt => opt.checked).map(opt => opt.slug).join(',');
    const selectedEducation = educationOptions.filter(opt => opt.checked).map(opt => opt.slug).join(',');
    const selectedJobTypes = jobTypeOptions.filter(opt => opt.checked).map(opt => opt.value).join(',');

    const _ = [
      searchTerm,
      selectedLocations,
      selectedSkills,
      selectedIndustries,
      selectedEducation,
      selectedJobTypes,
      salaryMin,
      salaryMax,
      experienceMin,
      experienceMax,
      isRemote,
      currentPage,
    ];

    // Don't navigate if:
    // 1. Not mounted yet (initial SSR)
    // 2. Currently syncing from URL (would cause infinite loop)
    if (hasMounted && !isSyncingFromUrl) {
      navigateWithFilters();
    }
  });

  const hasActiveFilters = $derived(
    Boolean(
      searchTerm ||
        locationSearchTerm ||
        locationOptions.some(opt => opt.checked) ||
        skillOptions.some(opt => opt.checked) ||
        industryOptions.some(opt => opt.checked) ||
        educationOptions.some(opt => opt.checked) ||
        jobTypeOptions.some(opt => opt.checked) ||
        salaryMin !== null ||
        salaryMax !== null ||
        experienceMin > 0 ||
        experienceMax < 20 ||
        isRemote
    )
  );

  const activeFilterCount = $derived(
    locationOptions.filter(opt => opt.checked).length +
    skillOptions.filter(opt => opt.checked).length +
    industryOptions.filter(opt => opt.checked).length +
    educationOptions.filter(opt => opt.checked).length +
    jobTypeOptions.filter(opt => opt.checked).length +
    (salaryMin !== null ? 1 : 0) +
    (salaryMax !== null ? 1 : 0) +
    (experienceMin > 0 ? 1 : 0) +
    (experienceMax < 20 ? 1 : 0) +
    (isRemote ? 1 : 0)
  );

  // Filter jobs locally by location search term
  let filteredJobs = $derived<Job[]>(
    (() => {
      if (!locationSearchTerm) return jobs;

      const term = locationSearchTerm.toLowerCase();
      return jobs.filter(job =>
        job.location_display.toLowerCase().includes(term)
      );
    })()
  );

  // Functions
  function toggleFiltersMobile(): void {
    showFiltersMobile = !showFiltersMobile;
  }

  function resetFilters(): void {
    searchTerm = '';
    locationSearchTerm = '';
    locationOptions.forEach(opt => opt.checked = false);
    skillOptions.forEach(opt => opt.checked = false);
    industryOptions.forEach(opt => opt.checked = false);
    educationOptions.forEach(opt => opt.checked = false);
    jobTypeOptions.forEach(opt => opt.checked = false);
    salaryMin = null;
    salaryMax = null;
    experienceMin = 0;
    experienceMax = 20;
    isRemote = false;
    currentPage = 1;
    showFiltersMobile = false;
  }

  async function saveJob(jobId: number): Promise<void> {
    const job = jobs.find(j => j.id === jobId);
    if (!job) return;

    const wasSaved = job.is_saved;

    try {
      if (wasSaved) {
        await jobsApi.unsave(jobId);
        toast.success('Job removed from saved');
      } else {
        await jobsApi.save(jobId);
        toast.success('Job saved!');
      }

      // Update the job in the data (trigger reactivity)
      // Create a new array with the updated job
      jobs = jobs.map(j => j.id === jobId ? { ...j, is_saved: !wasSaved } : j);
    } catch (err) {
      console.error('Failed to save job:', err);
      toast.error('Please login to save jobs');
    }
  }

  function goToPage(page: number): void {
    currentPage = page;
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

  function timeSince(dateString: string): string {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
    return `${Math.floor(diffDays / 30)} month${Math.floor(diffDays / 30) > 1 ? 's' : ''} ago`;
  }

  // Generate array of page numbers to display
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
  <title>Job Search - PeelJobs</title>
  <meta name="description" content="Find your dream job with PeelJobs advanced job search and filtering capabilities" />
</svelte:head>

<div class="min-h-screen bg-gray-50 text-gray-900">
  <!-- Header -->
  <header class="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-40 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="text-center">
        <h1 class="text-3xl md:text-4xl font-bold text-gray-800">
          Find Your Dream Job
        </h1>
        <p class="text-gray-600 mt-2">Discover opportunities that match your skills and ambitions</p>
      </div>
    </div>
  </header>

  <div class="max-w-7xl mx-auto px-4 py-8">
    <!-- Search Section -->
    <section class="mb-8">
      <div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <!-- Keywords Search -->
          <div class="relative">
            <label for="search-keywords" class="block text-sm font-medium text-gray-700 mb-2">
              Keywords
            </label>
            <div class="relative">
              <input
                id="search-keywords"
                type="text"
                bind:value={searchTerm}
                placeholder="Job title, company, skills..."
                class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 transition-all"
              />
              <Search class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <!-- Location Search -->
          <div class="relative">
            <label for="search-location" class="block text-sm font-medium text-gray-700 mb-2">
              Location
            </label>
            <div class="relative">
              <input
                id="search-location"
                type="text"
                bind:value={locationSearchTerm}
                placeholder="Filter displayed results by location..."
                class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 transition-all"
              />
              <MapPin class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Mobile Filter Toggle -->
    <div class="md:hidden mb-6 flex justify-between items-center">
      <button
        onclick={toggleFiltersMobile}
        class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors"
      >
        <SlidersHorizontal size={20} />
        {showFiltersMobile ? 'Hide Filters' : 'Show Filters'}
        {#if activeFilterCount > 0}
          <span class="bg-cyan-400 text-white text-xs px-2 py-1 rounded-full font-medium">{activeFilterCount}</span>
        {/if}
      </button>
      <div class="text-sm text-gray-600">
        {totalJobs.toLocaleString()} job{totalJobs !== 1 ? 's' : ''} found
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-8">
      <!-- Filter Sidebar -->
      <aside class={`${showFiltersMobile ? 'block' : 'hidden'} md:block md:w-80 md:sticky md:top-24 self-start`}>
        <div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-gray-800 flex items-center gap-2">
              <Filter size={24} class="text-blue-600" />
              Filters
            </h2>
            {#if hasActiveFilters}
              <button
                onclick={resetFilters}
                class="text-sm text-blue-600 hover:text-blue-700 transition-colors flex items-center gap-1"
              >
                <X size={16} />
                Clear All
              </button>
            {/if}
          </div>

          <div class="space-y-4">
            <!-- Location Filter -->
            {#if locationOptions.length > 0}
              <FilterSection
                title="Location"
                icon={MapPin}
                options={locationOptions}
                showMoreButton={locationOptions.length > 5}
                onToggle={toggleLocationFilter}
                onShowMore={() => showLocationModal = true}
              />
            {/if}

            <!-- Skills Filter -->
            {#if skillOptions.length > 0}
              <FilterSection
                title="Skills"
                icon={Briefcase}
                options={skillOptions}
                showMoreButton={skillOptions.length > 5}
                onToggle={toggleSkillFilter}
                onShowMore={() => showSkillsModal = true}
              />
            {/if}

            <!-- Industry Filter -->
            {#if industryOptions.length > 0}
              <FilterSection
                title="Industry"
                icon={Factory}
                options={industryOptions}
                showMoreButton={industryOptions.length > 5}
                onToggle={toggleIndustryFilter}
                onShowMore={() => showIndustryModal = true}
              />
            {/if}

            <!-- Education Filter -->
            {#if educationOptions.length > 0}
              <FilterSection
                title="Education"
                icon={GraduationCap}
                options={educationOptions}
                showMoreButton={educationOptions.length > 5}
                onToggle={toggleEducationFilter}
                onShowMore={() => showEducationModal = true}
              />
            {/if}

            <!-- Job Type Filter -->
            {#if jobTypeOptions.length > 0}
              <div class="border border-gray-200 rounded-lg">
                <div class="p-4 bg-gray-50 border-b border-gray-200">
                  <h3 class="font-medium text-gray-800">Job Type</h3>
                </div>
                <div class="p-4 bg-white">
                  <div class="space-y-2">
                    {#each jobTypeOptions as option (option.value)}
                      <label class="flex items-center space-x-2 text-sm cursor-pointer min-h-[44px] hover:bg-gray-50 -mx-2 px-2 rounded transition-colors">
                        <input
                          type="checkbox"
                          checked={option.checked}
                          onchange={() => toggleJobTypeFilter(option.value)}
                          class="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500 focus:ring-2"
                        />
                        <span class="text-gray-700">{option.name}</span>
                        <span class="text-gray-500 text-xs ml-auto">({option.count})</span>
                      </label>
                    {/each}
                  </div>
                </div>
              </div>
            {/if}

            <!-- Salary Range -->
            <div class="border border-gray-200 rounded-lg">
              <div class="p-4 bg-gray-50 border-b border-gray-200">
                <h3 class="font-medium text-gray-800">Salary (LPA)</h3>
              </div>
              <div class="p-4 bg-white">
                <div class="grid grid-cols-2 gap-3">
                  <div>
                    <label for="salary-min" class="sr-only">Minimum salary</label>
                    <input
                      id="salary-min"
                      type="number"
                      bind:value={salaryMin}
                      placeholder="Min"
                      class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 text-sm transition-all"
                    />
                  </div>
                  <div>
                    <label for="salary-max" class="sr-only">Maximum salary</label>
                    <input
                      id="salary-max"
                      type="number"
                      bind:value={salaryMax}
                      placeholder="Max"
                      class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 text-sm transition-all"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Experience Range Slider -->
            <div class="border border-gray-200 rounded-lg">
              <div class="p-4 bg-gray-50 border-b border-gray-200">
                <h3 class="font-medium text-gray-800">Experience</h3>
              </div>
              <div class="p-4 bg-white">
                <div class="space-y-4">
                  <div class="flex justify-between text-sm text-gray-600">
                    <span>Min: {experienceMin} years</span>
                    <span>Max: {experienceMax} years</span>
                  </div>

                  <div class="space-y-3">
                    <div>
                      <label for="min-experience" class="block text-xs text-gray-500 mb-1">Min Experience</label>
                      <input
                        id="min-experience"
                        type="range"
                        min="0"
                        max="20"
                        bind:value={experienceMin}
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      />
                    </div>
                    <div>
                      <label for="max-experience" class="block text-xs text-gray-500 mb-1">Max Experience</label>
                      <input
                        id="max-experience"
                        type="range"
                        min="0"
                        max="20"
                        bind:value={experienceMax}
                        class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                      />
                    </div>
                  </div>

                  <div class="flex justify-between text-xs text-gray-400">
                    <span>0 years</span>
                    <span>20+ years</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Remote Toggle -->
            <div class="border border-gray-200 rounded-lg p-4">
              <label class="flex items-center gap-3 text-sm font-medium text-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={isRemote}
                  class="w-4 h-4 rounded border-gray-300 bg-gray-50 text-blue-600 focus:ring-blue-500 focus:ring-2"
                />
                Remote Work Only
              </label>
            </div>
          </div>

          {#if hasActiveFilters}
            <button
              onclick={resetFilters}
              class="mt-6 w-full flex items-center justify-center gap-2 px-4 py-2 border border-blue-500 text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
            >
              <X size={18} />
              Clear All Filters
            </button>
          {/if}
        </div>
      </aside>

      <!-- Job Listings -->
      <main class="flex-1">
        <div class="hidden md:flex justify-between items-center mb-6">
          <h2 class="text-2xl font-semibold text-gray-800">
            Job Opportunities
          </h2>
          <div class="text-sm text-gray-600">
            {totalJobs.toLocaleString()} job{totalJobs !== 1 ? 's' : ''} found
          </div>
        </div>

        {#if error}
          <div class="text-center py-16">
            <p class="text-red-600 mb-4">{error}</p>
            <button
              onclick={() => window.location.reload()}
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        {:else if filteredJobs.length > 0}
          <div class="space-y-4">
            {#each filteredJobs as job (job.id)}
              <article class="relative bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 group hover:shadow-lg hover:shadow-blue-100">
                <a
                  href="/jobs/{job.slug.replace(/^\/+/, '')}"
                  class="block after:absolute after:inset-0"
                  aria-label="View details for {job.title} at {job.company_name}"
                >
                  <div class="flex-1">
                    <h3 class="text-xl font-semibold text-blue-600 group-hover:text-blue-700 transition-colors mb-3">
                      {job.title}
                    </h3>

                    <div class="space-y-2 mb-4">
                      <div class="flex items-center text-gray-700 text-sm">
                        <Building size={16} class="mr-2 text-blue-500" />
                        {job.company_name}
                      </div>
                      <div class="flex items-center text-gray-700 text-sm">
                        <MapPin size={16} class="mr-2 text-blue-500" />
                        {job.location_display}
                      </div>
                      <div class="flex items-center text-gray-700 text-sm">
                        <DollarSign size={16} class="mr-2 text-green-600" />
                        {job.salary_display}
                      </div>
                    </div>

                    <div class="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                      <div class="flex items-center gap-1">
                        <Briefcase size={14} />
                        {job.job_type}
                      </div>
                      <div class="flex items-center gap-1">
                        <Users size={14} />
                        {job.experience_display}
                      </div>
                      <div class="flex items-center gap-1">
                        <Clock size={14} />
                        {job.time_ago}
                      </div>
                      <div class="flex items-center gap-1">
                        <Users size={14} />
                        {job.applicants_count} applicants
                      </div>
                    </div>
                  </div>
                </a>

                <!-- Bookmark button with higher z-index to be clickable -->
                <button
                  type="button"
                  onclick={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    saveJob(job.id);
                  }}
                  class="absolute top-6 right-6 z-10 p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-blue-600 transition-all {job.is_saved ? 'text-blue-600 bg-gray-100' : ''}"
                  aria-label="Save {job.title}"
                >
                  <Bookmark size={20} class={job.is_saved ? 'fill-current' : ''} />
                </button>
              </article>
            {/each}
          </div>

          <!-- Pagination -->
          {#if totalPages > 1}
            <div class="mt-12 flex justify-center">
              <div class="flex items-center gap-2">
                <button
                  onclick={prevPage}
                  disabled={currentPage === 1}
                  class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <div class="flex gap-1">
                  {#each getPageNumbers() as pageNum}
                    <button
                      onclick={() => goToPage(pageNum)}
                      class="{pageNum === currentPage ? 'bg-blue-600 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700'} px-3 py-2 rounded-lg transition-colors"
                    >
                      {pageNum}
                    </button>
                  {/each}
                </div>
                <button
                  onclick={nextPage}
                  disabled={currentPage === totalPages}
                  class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          {/if}
        {:else}
          <div class="text-center py-16">
            <Search size={64} class="mx-auto text-gray-400 mb-4" />
            <h3 class="text-xl font-semibold text-gray-700 mb-2">No Jobs Found</h3>
            <p class="text-gray-600 mb-6">
              Try adjusting your search criteria or filters to find more opportunities.
            </p>
            <button
              onclick={resetFilters}
              class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
            >
              Clear All Filters
            </button>
          </div>
        {/if}
      </main>
    </div>
  </div>
</div>

<!-- Modals -->
<FilterModal
  title="Locations"
  options={locationOptions}
  bind:isOpen={showLocationModal}
  onClose={() => showLocationModal = false}
  onToggle={toggleLocationFilter}
  onApply={() => showLocationModal = false}
/>

<FilterModal
  title="Skills"
  options={skillOptions}
  bind:isOpen={showSkillsModal}
  onClose={() => showSkillsModal = false}
  onToggle={toggleSkillFilter}
  onApply={() => showSkillsModal = false}
/>

<FilterModal
  title="Industries"
  options={industryOptions}
  bind:isOpen={showIndustryModal}
  onClose={() => showIndustryModal = false}
  onToggle={toggleIndustryFilter}
  onApply={() => showIndustryModal = false}
/>

<FilterModal
  title="Education"
  options={educationOptions}
  bind:isOpen={showEducationModal}
  onClose={() => showEducationModal = false}
  onToggle={toggleEducationFilter}
  onApply={() => showEducationModal = false}
/>
