<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Search, Filter, SlidersHorizontal, MapPin, Briefcase, DollarSign, Bookmark, Building, Clock, Users, GraduationCap, Factory } from '@lucide/svelte';
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

  <div class="max-w-7xl mx-auto px-4 py-8">
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
        <div class="bg-white border border-gray-200 rounded-lg">
          <div class="flex justify-between items-center px-4 py-4 border-b border-gray-200">
            <h2 class="text-base font-semibold text-gray-900 flex items-center gap-2">
              <Filter size={18} class="text-gray-600" />
              All Filters
            </h2>
            {#if hasActiveFilters}
              <button
                onclick={resetFilters}
                class="text-sm text-blue-600 hover:text-blue-700 transition-colors"
              >
                Clear ({activeFilterCount})
              </button>
            {/if}
          </div>

          <div>
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
                <div class="space-y-2">
                  {#each jobTypeOptions as option (option.value)}
                    <label class="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={option.checked}
                        onchange={() => toggleJobTypeFilter(option.value)}
                        class="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500 cursor-pointer"
                      />
                      <span class="text-gray-700 flex-1 text-sm">{option.name}</span>
                      <span class="text-gray-500 text-xs">({option.count})</span>
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
              <div class="grid grid-cols-2 gap-2">
                <div>
                  <label for="salary-min" class="block text-xs text-gray-600 mb-1 font-medium">Min</label>
                  <input
                    id="salary-min"
                    type="number"
                    bind:value={salaryMin}
                    placeholder="0"
                    class="w-full px-2 py-1.5 bg-gray-50 border border-gray-200 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 text-sm transition-all"
                  />
                </div>
                <div>
                  <label for="salary-max" class="block text-xs text-gray-600 mb-1 font-medium">Max</label>
                  <input
                    id="salary-max"
                    type="number"
                    bind:value={salaryMax}
                    placeholder="∞"
                    class="w-full px-2 py-1.5 bg-gray-50 border border-gray-200 rounded focus:ring-1 focus:ring-blue-500 focus:border-blue-500 text-gray-900 placeholder-gray-400 text-sm transition-all"
                  />
                </div>
              </div>
            </CollapsibleFilterSection>

            <!-- Experience Range Slider -->
            <CollapsibleFilterSection
              title="Experience"
              hasActiveFilter={experienceMin > 0 || experienceMax < 20}
            >
              <div class="space-y-3">
                <div class="flex justify-between text-xs text-gray-700 font-semibold">
                  <span>{experienceMin} {experienceMin === 1 ? 'yr' : 'yrs'}</span>
                  <span>{experienceMax === 20 ? '20+' : experienceMax} {experienceMax === 1 ? 'yr' : 'yrs'}</span>
                </div>

                <div class="space-y-2">
                  <div>
                    <label for="min-experience" class="block text-xs text-gray-500 mb-1">Min</label>
                    <input
                      id="min-experience"
                      type="range"
                      min="0"
                      max="20"
                      bind:value={experienceMin}
                      class="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-blue-600"
                    />
                  </div>
                  <div>
                    <label for="max-experience" class="block text-xs text-gray-500 mb-1">Max</label>
                    <input
                      id="max-experience"
                      type="range"
                      min="0"
                      max="20"
                      bind:value={experienceMax}
                      class="w-full h-1.5 bg-gray-200 rounded-full appearance-none cursor-pointer accent-blue-600"
                    />
                  </div>
                </div>

                <div class="flex justify-between text-xs text-gray-400">
                  <span>Fresher</span>
                  <span>20+ yrs</span>
                </div>
              </div>
            </CollapsibleFilterSection>

            <!-- Remote Toggle -->
            <CollapsibleFilterSection
              title="Work Mode"
              hasActiveFilter={isRemote}
            >
              <label class="flex items-center gap-2 text-sm cursor-pointer py-1.5 hover:bg-gray-50 -mx-1 px-1 rounded transition-colors">
                <input
                  type="checkbox"
                  bind:checked={isRemote}
                  class="w-3.5 h-3.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-1 cursor-pointer"
                />
                <span class="text-gray-700 text-sm leading-tight">Remote Work Only</span>
              </label>
            </CollapsibleFilterSection>
          </div>
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

        <!-- Active Filter Chips -->
        <FilterChips
          chips={filterChips}
          onRemove={removeFilterChip}
          onClearAll={resetFilters}
        />

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
        {:else if jobs.length > 0}
          <div class="space-y-4">
            {#each jobs as job (job.id)}
              <article class="relative bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 group hover:shadow-lg hover:shadow-blue-100">
                <a
                  href="/jobs/{job.slug.replace(/^\/+/, '')}"
                  class="block after:absolute after:inset-0"
                  aria-label="View details for {job.title} at {job.company_name}"
                >
                  <div class="flex-1">
                    <div class="flex items-start gap-3 mb-3">
                      <h3 class="text-xl font-semibold text-blue-600 group-hover:text-blue-700 transition-colors flex-1">
                        {job.title}
                      </h3>
                      {#if !job.accepts_applications}
                        <span class="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-md border border-gray-300 flex-shrink-0">
                          Closed
                        </span>
                      {/if}
                    </div>

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
