<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    Search,
    Filter,
    SlidersHorizontal,
    MapPin,
    Briefcase,
    DollarSign,
    Bookmark,
    Building2,
    Clock,
    Users,
    GraduationCap,
    Factory,
    ChevronRight,
    ChevronLeft,
    Sparkles,
    TrendingUp,
    X
  } from '@lucide/svelte';
  import FilterSection from '$lib/components/FilterSection.svelte';
  import FilterModal from '$lib/components/FilterModal.svelte';
  import FilterChips from '$lib/components/FilterChips.svelte';
  import CollapsibleFilterSection from '$lib/components/CollapsibleFilterSection.svelte';
  import { toast } from '$lib/stores/toast';
  import { jobsApi } from '$lib/api/jobs';
  import type { Job, FilterOption as BaseFilterOption, JobFilterOptions } from '$lib/types/jobs';
  import type { PageData } from './$types';

  // Extended filter option with UI state
  interface FilterOption extends BaseFilterOption {
    value: string;
    checked: boolean;
  }

  interface Props {
    data: PageData;
  }

  let { data }: Props = $props();

  // Initialize from server data (reactive to changes)
  let jobs = $state<Job[]>([]);
  const totalJobs = $derived(data.totalJobs || 0);
  const totalPages = $derived(data.totalPages || 0);
  let currentPage = $state(1);
  let filterOptions = $state<JobFilterOptions | null>(null);
  const error = $derived(data.error);

  // Sync jobs and filterOptions when server data changes
  $effect(() => {
    jobs = data.jobs || [];
    filterOptions = data.filterOptions;
  });

  // Search and filter state - initialized empty, synced via $effect
  let searchTerm = $state('');
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

  // Fresher filter
  let isFresher = $state(false);

  // Track if we're syncing from URL (to prevent triggering navigation)
  let isSyncingFromUrl = $state(false);

  // Filter options state
  let locationOptions = $state<FilterOption[]>([]);
  let skillOptions = $state<FilterOption[]>([]);
  let industryOptions = $state<FilterOption[]>([]);
  let educationOptions = $state<FilterOption[]>([]);
  let jobTypeOptions = $state<{ name: string; value: string; count: number; checked: boolean }[]>([]);

  // Initialize filter options from server data
  $effect(() => {
    const params = data.initialParams || {};
    const opts = data.filterOptions;

    const selectedLocations = params.location || [];
    const selectedSkills = params.skills || [];
    const selectedIndustries = params.industry || [];
    const selectedEducation = params.education || [];
    const selectedJobTypes = params.job_type || [];

    locationOptions = opts?.locations.map((opt: BaseFilterOption) => ({
      ...opt,
      value: opt.slug,
      checked: selectedLocations.includes(opt.slug)
    })) || [];

    skillOptions = opts?.skills.map((opt: BaseFilterOption) => ({
      ...opt,
      value: opt.slug,
      checked: selectedSkills.includes(opt.slug)
    })) || [];

    industryOptions = opts?.industries.map((opt: BaseFilterOption) => ({
      ...opt,
      value: opt.slug,
      checked: selectedIndustries.includes(opt.slug)
    })) || [];

    educationOptions = opts?.education.map((opt: BaseFilterOption) => ({
      ...opt,
      value: opt.slug,
      checked: selectedEducation.includes(opt.slug)
    })) || [];

    jobTypeOptions = opts?.job_types.map((opt: { label: string; value: string; count: number }) => ({
      name: opt.label,
      value: opt.value,
      count: opt.count,
      checked: selectedJobTypes.includes(opt.value)
    })) || [];

    currentPage = data.currentPage || 1;
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

    const fresher = urlParams.get('fresher');
    isFresher = fresher === 'true';

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

  // Navigate to new URL with filters (triggers SSR reload)
  let navigationTimeout: ReturnType<typeof setTimeout>;
  function navigateWithFilters(delay: number = 500) {
    clearTimeout(navigationTimeout);
    navigationTimeout = setTimeout(() => {
      // Only navigate if we're on the exact jobs listing page (not job detail pages)
      if ($page.url.pathname !== '/jobs' && $page.url.pathname !== '/jobs/') {
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
      if (isFresher) params.set('fresher', 'true');

      // Add pagination
      if (currentPage > 1) params.set('page', currentPage.toString());

      // Navigate to new URL (triggers SSR)
      const queryString = params.toString();
      const newUrl = queryString ? `/jobs?${queryString}` : '/jobs';

      // Only navigate if URL actually changed
      if ($page.url.pathname + ($page.url.search || '') !== newUrl) {
        goto(newUrl, { replaceState: true, noScroll: true, keepFocus: true });
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
      isFresher,
      currentPage,
    ];

    // Don't navigate if currently syncing from URL (would cause infinite loop)
    if (!isSyncingFromUrl) {
      navigateWithFilters();
    }
  });

  const hasActiveFilters = $derived(
    Boolean(
      searchTerm ||
        locationOptions.some(opt => opt.checked) ||
        skillOptions.some(opt => opt.checked) ||
        industryOptions.some(opt => opt.checked) ||
        educationOptions.some(opt => opt.checked) ||
        jobTypeOptions.some(opt => opt.checked) ||
        salaryMin !== null ||
        salaryMax !== null ||
        experienceMin > 0 ||
        experienceMax < 20 ||
        isRemote ||
        isFresher
    )
  );

  const activeFilterCount = $derived(
    locationOptions.filter(opt => opt.checked).length +
    skillOptions.filter(opt => opt.checked).length +
    industryOptions.filter(opt => opt.checked).length +
    educationOptions.filter(opt => opt.checked).length +
    jobTypeOptions.filter(opt => opt.checked).length +
    (salaryMin !== null || salaryMax !== null ? 1 : 0) +
    (experienceMin > 0 || experienceMax < 20 ? 1 : 0) +
    (isRemote ? 1 : 0) +
    (isFresher ? 1 : 0)
  );

  // Generate filter chips for active filters
  const filterChips = $derived((() => {
    const chips: Array<{ label: string; value: string; type: 'location' | 'skill' | 'industry' | 'education' | 'job_type' | 'salary' | 'experience' | 'remote' | 'fresher' }> = [];

    // Location chips
    locationOptions.filter(opt => opt.checked).forEach(opt => {
      chips.push({ label: opt.name, value: opt.value, type: 'location' });
    });

    // Skill chips
    skillOptions.filter(opt => opt.checked).forEach(opt => {
      chips.push({ label: opt.name, value: opt.value, type: 'skill' });
    });

    // Industry chips
    industryOptions.filter(opt => opt.checked).forEach(opt => {
      chips.push({ label: opt.name, value: opt.value, type: 'industry' });
    });

    // Education chips
    educationOptions.filter(opt => opt.checked).forEach(opt => {
      chips.push({ label: opt.name, value: opt.value, type: 'education' });
    });

    // Job type chips
    jobTypeOptions.filter(opt => opt.checked).forEach(opt => {
      chips.push({ label: opt.name, value: opt.value, type: 'job_type' });
    });

    // Salary chip
    if (salaryMin !== null || salaryMax !== null) {
      const min = salaryMin !== null ? `${salaryMin}L` : '0';
      const max = salaryMax !== null ? `${salaryMax}L` : '∞';
      chips.push({ label: `Salary: ${min} - ${max}`, value: 'salary', type: 'salary' });
    }

    // Experience chip
    if (experienceMin > 0 || experienceMax < 20) {
      const min = experienceMin > 0 ? `${experienceMin}` : '0';
      const max = experienceMax < 20 ? `${experienceMax}` : '20+';
      chips.push({ label: `Experience: ${min} - ${max} years`, value: 'experience', type: 'experience' });
    }

    // Remote chip
    if (isRemote) {
      chips.push({ label: 'Remote Only', value: 'remote', type: 'remote' });
    }

    // Fresher chip
    if (isFresher) {
      chips.push({ label: 'Fresher Jobs', value: 'fresher', type: 'fresher' });
    }

    return chips;
  })());

  // Functions
  function toggleFiltersMobile(): void {
    showFiltersMobile = !showFiltersMobile;
  }

  function resetFilters(): void {
    searchTerm = '';
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
    isFresher = false;
    currentPage = 1;
    showFiltersMobile = false;
  }

  function removeFilterChip(chip: { type: string; value: string }): void {
    switch (chip.type) {
      case 'location':
        toggleLocationFilter(chip.value);
        break;
      case 'skill':
        toggleSkillFilter(chip.value);
        break;
      case 'industry':
        toggleIndustryFilter(chip.value);
        break;
      case 'education':
        toggleEducationFilter(chip.value);
        break;
      case 'job_type':
        toggleJobTypeFilter(chip.value);
        break;
      case 'salary':
        salaryMin = null;
        salaryMax = null;
        break;
      case 'experience':
        experienceMin = 0;
        experienceMax = 20;
        break;
      case 'remote':
        isRemote = false;
        break;
      case 'fresher':
        isFresher = false;
        break;
    }
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
  <title>Find Jobs - PeelJobs</title>
  <meta name="description" content="Discover your dream job with PeelJobs. Browse thousands of job opportunities with advanced filters for location, skills, salary, and more." />
</svelte:head>

<div class="min-h-screen bg-surface-50">
  <!-- Search Header -->
  <section class="bg-white border-b border-border py-6">
    <div class="max-w-7xl mx-auto px-4 lg:px-8">
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 class="text-2xl font-semibold text-black">Find jobs</h1>
          <p class="text-muted text-sm mt-1">{totalJobs.toLocaleString()} opportunities available</p>
        </div>
        <!-- Search Input -->
        <div class="relative flex-1 max-w-md">
          <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search size={18} class="text-muted" />
          </span>
          <input
            type="text"
            bind:value={searchTerm}
            placeholder="Search jobs by title, skill, or company..."
            class="w-full pl-11 pr-4 h-10 bg-surface border border-border rounded-lg text-black placeholder-muted focus:bg-white focus:border-primary-600 focus:ring-2 focus:ring-primary-600/10 transition-all outline-none text-sm"
          />
        </div>
      </div>
    </div>
  </section>

  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-6">
    <!-- Mobile Filter Toggle -->
    <div class="lg:hidden mb-4 flex justify-between items-center">
      <button
        onclick={toggleFiltersMobile}
        class="flex items-center gap-2 h-10 px-4 bg-white border border-border rounded-full text-black font-medium hover:bg-surface transition-colors"
      >
        <SlidersHorizontal size={18} />
        {showFiltersMobile ? 'Hide Filters' : 'Filters'}
        {#if activeFilterCount > 0}
          <span class="bg-primary-600 text-white text-xs px-2 py-0.5 rounded-full">{activeFilterCount}</span>
        {/if}
      </button>
    </div>

    <div class="flex flex-col lg:flex-row gap-6">
      <!-- Filter Sidebar -->
      <aside class="{showFiltersMobile ? 'block' : 'hidden'} lg:block lg:w-72 flex-shrink-0">
        <div class="bg-white rounded-lg border border-border overflow-hidden lg:sticky lg:top-20 lg:max-h-[calc(100vh-6rem)] lg:overflow-y-auto">
          <!-- Filter Header -->
          <div class="flex justify-between items-center px-4 py-3 border-b border-border">
            <h2 class="text-sm font-semibold text-black flex items-center gap-2">
              <Filter size={16} class="text-primary-600" />
              Filters
            </h2>
            {#if hasActiveFilters}
              <button
                onclick={resetFilters}
                class="text-xs text-primary-600 hover:text-primary-700 font-semibold hover:underline"
              >
                Clear all
              </button>
            {/if}
          </div>

          <div class="p-1">
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
              <CollapsibleFilterSection
                title="Job Type"
                hasActiveFilter={jobTypeOptions.some(opt => opt.checked)}
              >
                <div class="space-y-1">
                  {#each jobTypeOptions as option (option.value)}
                    <label class="flex items-center gap-3 cursor-pointer py-2 px-2 rounded-lg hover:bg-surface transition-colors">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleJobTypeFilter(option.value)}
                        class="w-4 h-4 text-primary-600 border-border rounded focus:ring-primary-600 cursor-pointer"
                      />
                      <span class="text-sm text-black flex-1">{option.name}</span>
                      <span class="text-xs text-muted bg-surface px-2 py-0.5 rounded">{option.count}</span>
                    </label>
                  {/each}
                </div>
              </CollapsibleFilterSection>
            {/if}

            <!-- Salary Range -->
            <CollapsibleFilterSection
              title="Salary (LPA)"
              hasActiveFilter={salaryMin !== null || salaryMax !== null}
            >
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label for="salary-min" class="block text-xs text-muted mb-1">Min</label>
                  <input
                    id="salary-min"
                    type="number"
                    bind:value={salaryMin}
                    placeholder="0"
                    class="w-full px-3 py-2 bg-surface border border-border rounded-lg focus:bg-white focus:border-primary-600 focus:ring-2 focus:ring-primary-600/10 text-sm transition-all outline-none"
                  />
                </div>
                <div>
                  <label for="salary-max" class="block text-xs text-muted mb-1">Max</label>
                  <input
                    id="salary-max"
                    type="number"
                    bind:value={salaryMax}
                    placeholder="∞"
                    class="w-full px-3 py-2 bg-surface border border-border rounded-lg focus:bg-white focus:border-primary-600 focus:ring-2 focus:ring-primary-600/10 text-sm transition-all outline-none"
                  />
                </div>
              </div>
            </CollapsibleFilterSection>

            <!-- Experience Range -->
            <CollapsibleFilterSection
              title="Experience"
              hasActiveFilter={experienceMin > 0 || experienceMax < 20}
            >
              <div class="space-y-4">
                <div class="flex justify-between text-xs">
                  <span class="px-2 py-1 bg-primary-50 text-primary-600 rounded font-medium">{experienceMin} yr{experienceMin !== 1 ? 's' : ''}</span>
                  <span class="px-2 py-1 bg-primary-50 text-primary-600 rounded font-medium">{experienceMax === 20 ? '20+' : experienceMax} yr{experienceMax !== 1 ? 's' : ''}</span>
                </div>
                <div class="space-y-2">
                  <input
                    type="range"
                    min="0"
                    max="20"
                    bind:value={experienceMin}
                    class="w-full h-1.5 bg-surface-200 rounded-full appearance-none cursor-pointer accent-primary-600"
                  />
                  <input
                    type="range"
                    min="0"
                    max="20"
                    bind:value={experienceMax}
                    class="w-full h-1.5 bg-surface-200 rounded-full appearance-none cursor-pointer accent-primary-600"
                  />
                </div>
              </div>
            </CollapsibleFilterSection>

            <!-- Remote Toggle -->
            <CollapsibleFilterSection
              title="Work Mode"
              hasActiveFilter={isRemote}
            >
              <label class="flex items-center gap-3 cursor-pointer py-2 px-2 rounded-lg hover:bg-surface transition-colors">
                <input
                  type="checkbox"
                  bind:checked={isRemote}
                  class="w-4 h-4 rounded border-border text-primary-600 focus:ring-primary-600 cursor-pointer"
                />
                <span class="text-sm text-black">Remote Only</span>
              </label>
            </CollapsibleFilterSection>
          </div>
        </div>
      </aside>

      <!-- Job Listings -->
      <main class="flex-1 min-w-0">
        <!-- Active Filter Chips -->
        <FilterChips
          chips={filterChips}
          onRemove={removeFilterChip}
          onClearAll={resetFilters}
        />

        {#if error}
          <!-- Error State -->
          <div class="bg-white rounded-lg border border-border p-12 text-center">
            <div class="w-14 h-14 rounded-lg bg-error-light flex items-center justify-center mx-auto mb-4">
              <X size={24} class="text-error-600" />
            </div>
            <h3 class="text-lg font-semibold text-black mb-2">Something went wrong</h3>
            <p class="text-muted mb-6">{error}</p>
            <button
              onclick={() => window.location.reload()}
              class="h-10 px-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full font-semibold transition-colors"
            >
              Try Again
            </button>
          </div>
        {:else if jobs.length > 0}
          <!-- Job Cards -->
          <div class="space-y-3">
            {#each jobs as job, index (job.id)}
              <article
                class="group bg-white rounded-lg border border-border overflow-hidden transition-all hover:shadow-card-hover hover:border-primary-200"
                style="animation: fade-in-up 0.4s ease forwards; animation-delay: {Math.min(index * 30, 200)}ms; opacity: 0;"
              >
                <a
                  href="/jobs/{job.slug.replace(/^\/+/, '')}"
                  class="block p-4 lg:p-5"
                  aria-label="View details for {job.title} at {job.company_name}"
                >
                  <div class="flex gap-4">
                    <!-- Company Logo -->
                    <div class="flex-shrink-0">
                      {#if job.company_logo}
                        <img
                          src={job.company_logo}
                          alt="{job.company_name} logo"
                          class="w-12 h-12 rounded object-cover bg-surface"
                        />
                      {:else}
                        <div class="w-12 h-12 rounded bg-primary-50 flex items-center justify-center">
                          <Building2 size={24} class="text-primary-600" />
                        </div>
                      {/if}
                    </div>

                    <!-- Job Info -->
                    <div class="flex-1 min-w-0">
                      <div class="flex items-start justify-between gap-3 mb-1">
                        <h3 class="text-base font-semibold text-black group-hover:text-primary-600 transition-colors line-clamp-1">
                          {job.title}
                        </h3>
                        {#if !job.accepts_applications}
                          <span class="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-surface text-muted rounded">Closed</span>
                        {/if}
                      </div>

                      <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted mb-2">
                        <span class="font-medium text-black">{job.company_name}</span>
                        <span class="flex items-center gap-1">
                          <MapPin size={14} />
                          {job.location_display}
                        </span>
                      </div>

                      <!-- Job Meta -->
                      <div class="flex flex-wrap items-center gap-2 mb-3">
                        <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-success-light text-success-600 rounded text-xs font-medium">
                          <DollarSign size={12} />
                          {job.salary_display}
                        </span>
                        <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-600 rounded text-xs font-medium">
                          <Briefcase size={12} />
                          {job.job_type}
                        </span>
                        <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-surface text-muted rounded text-xs font-medium">
                          <Users size={12} />
                          {job.experience_display}
                        </span>
                      </div>

                      <!-- Footer -->
                      <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4 text-xs text-muted">
                          <span class="flex items-center gap-1">
                            <Clock size={12} />
                            {job.time_ago}
                          </span>
                          <span class="flex items-center gap-1">
                            <Users size={12} />
                            {job.applicants_count} applicants
                          </span>
                        </div>
                        <span class="hidden sm:flex items-center gap-1 text-sm font-semibold text-primary-600 group-hover:gap-2 transition-all">
                          View
                          <ChevronRight size={14} />
                        </span>
                      </div>
                    </div>
                  </div>
                </a>

                <!-- Bookmark button -->
                <button
                  type="button"
                  onclick={(event) => {
                    event.preventDefault();
                    event.stopPropagation();
                    saveJob(job.id);
                  }}
                  class="absolute top-4 right-4 z-10 p-2 rounded-full hover:bg-surface text-muted hover:text-primary-600 transition-all {job.is_saved ? 'text-primary-600 bg-primary-50' : ''}"
                  aria-label="Save {job.title}"
                >
                  <Bookmark size={18} class={job.is_saved ? 'fill-current' : ''} />
                </button>
              </article>
            {/each}
          </div>

          <!-- Pagination -->
          {#if totalPages > 1}
            <div class="mt-8 flex justify-center">
              <div class="inline-flex items-center gap-1 bg-white rounded-lg border border-border p-1">
                <button
                  onclick={prevPage}
                  disabled={currentPage === 1}
                  class="flex items-center gap-1 px-3 py-2 text-sm font-medium text-muted rounded-lg hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <ChevronLeft size={16} />
                  <span class="hidden sm:inline">Prev</span>
                </button>

                <div class="flex gap-0.5 px-1">
                  {#each getPageNumbers() as pageNum}
                    <button
                      onclick={() => goToPage(pageNum)}
                      class="w-9 h-9 flex items-center justify-center text-sm font-medium rounded-lg transition-all {pageNum === currentPage ? 'bg-primary-600 text-white' : 'text-muted hover:bg-surface'}"
                    >
                      {pageNum}
                    </button>
                  {/each}
                </div>

                <button
                  onclick={nextPage}
                  disabled={currentPage === totalPages}
                  class="flex items-center gap-1 px-3 py-2 text-sm font-medium text-muted rounded-lg hover:bg-surface transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                >
                  <span class="hidden sm:inline">Next</span>
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          {/if}
        {:else}
          <!-- Empty State -->
          <div class="bg-white rounded-lg border border-border p-12 text-center">
            <div class="w-16 h-16 rounded-lg bg-primary-50 flex items-center justify-center mx-auto mb-5">
              <Search size={28} class="text-primary-600" />
            </div>
            <h3 class="text-lg font-semibold text-black mb-2">No jobs found</h3>
            <p class="text-muted mb-6 max-w-sm mx-auto">
              We couldn't find any jobs matching your criteria. Try adjusting your filters.
            </p>
            <button
              onclick={resetFilters}
              class="h-10 px-6 bg-primary-600 hover:bg-primary-700 text-white rounded-full font-semibold transition-colors"
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
  closeOnSelect={true}
/>

<FilterModal
  title="Skills"
  options={skillOptions}
  bind:isOpen={showSkillsModal}
  onClose={() => showSkillsModal = false}
  onToggle={toggleSkillFilter}
  onApply={() => showSkillsModal = false}
  closeOnSelect={true}
/>

<FilterModal
  title="Industries"
  options={industryOptions}
  bind:isOpen={showIndustryModal}
  onClose={() => showIndustryModal = false}
  onToggle={toggleIndustryFilter}
  onApply={() => showIndustryModal = false}
  closeOnSelect={true}
/>

<FilterModal
  title="Education"
  options={educationOptions}
  bind:isOpen={showEducationModal}
  onClose={() => showEducationModal = false}
  onToggle={toggleEducationFilter}
  onApply={() => showEducationModal = false}
  closeOnSelect={true}
/>
