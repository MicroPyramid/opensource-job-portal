<script>
  import { Search, Filter, SlidersHorizontal, X, MapPin, Briefcase, DollarSign, Bookmark, CalendarDays, Building, Clock, Users } from '@lucide/svelte';

  // Search and filter state
  let searchTerm = '';
  let locationTerm = '';
  let jobType = '';
  let salaryMin = null;
  let salaryMax = null;
  let experienceLevel = '';
  let isRemote = false;
  let showFiltersMobile = false;

  // Constants
  const allJobTypes = ['Full-time', 'Part-time', 'Contract', 'Internship'];
  const allExperienceLevels = ['Entry Level', 'Mid Level', 'Senior Level', 'Lead', 'Manager'];

  // Dummy job data
  const jobs = [
    { 
      id: 1, 
      title: 'Senior Software Engineer', 
      company: 'Tech Solutions Inc.', 
      location: 'New York, NY', 
      salaryMin: 120000, 
      salaryMax: 160000, 
      postedDate: '2024-01-15', 
      type: 'Full-time', 
      experienceLevel: 'Senior Level', 
      isRemote: false,
      applicants: 45,
      saved: false
    },
    { 
      id: 2, 
      title: 'Frontend Developer', 
      company: 'Web Wizards LLC', 
      location: 'Remote', 
      salaryMin: 80000, 
      salaryMax: 110000, 
      postedDate: '2024-01-12', 
      type: 'Full-time', 
      experienceLevel: 'Mid Level', 
      isRemote: true,
      applicants: 78,
      saved: false
    },
    { 
      id: 3, 
      title: 'Product Manager', 
      company: 'Innovate Co.', 
      location: 'San Francisco, CA', 
      salaryMin: 130000, 
      salaryMax: 180000, 
      postedDate: '2024-01-10', 
      type: 'Full-time', 
      experienceLevel: 'Senior Level', 
      isRemote: false,
      applicants: 32,
      saved: false
    },
    { 
      id: 4, 
      title: 'UX Designer', 
      company: 'Creative Designs', 
      location: 'Austin, TX', 
      salaryMin: 70000, 
      salaryMax: 95000, 
      postedDate: '2024-01-18', 
      type: 'Contract', 
      experienceLevel: 'Mid Level', 
      isRemote: false,
      applicants: 23,
      saved: false
    },
    { 
      id: 5, 
      title: 'DevOps Engineer', 
      company: 'CloudNet Systems', 
      location: 'Remote', 
      salaryMin: 100000, 
      salaryMax: 140000, 
      postedDate: '2024-01-05', 
      type: 'Full-time', 
      experienceLevel: 'Senior Level', 
      isRemote: true,
      applicants: 56,
      saved: false
    },
    { 
      id: 6, 
      title: 'Data Analyst', 
      company: 'Analytics Corp', 
      location: 'Chicago, IL', 
      salaryMin: 65000, 
      salaryMax: 85000, 
      postedDate: '2024-01-20', 
      type: 'Part-time', 
      experienceLevel: 'Entry Level', 
      isRemote: false,
      applicants: 67,
      saved: false
    },
    { 
      id: 7, 
      title: 'Full Stack Developer', 
      company: 'StartupHub', 
      location: 'Remote', 
      salaryMin: 90000, 
      salaryMax: 120000, 
      postedDate: '2024-01-22', 
      type: 'Full-time', 
      experienceLevel: 'Mid Level', 
      isRemote: true,
      applicants: 89,
      saved: false
    },
    { 
      id: 8, 
      title: 'Marketing Specialist', 
      company: 'Growth Co.', 
      location: 'Los Angeles, CA', 
      salaryMin: 55000, 
      salaryMax: 75000, 
      postedDate: '2024-01-14', 
      type: 'Full-time', 
      experienceLevel: 'Entry Level', 
      isRemote: false,
      applicants: 34,
      saved: false
    }
  ];

  // Reactive filtered jobs
  $: filteredJobs = jobs.filter(job => {
    const searchMatch = !searchTerm || 
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(searchTerm.toLowerCase());
    
    const locationMatch = !locationTerm || 
      job.location.toLowerCase().includes(locationTerm.toLowerCase());
    
    const typeMatch = !jobType || job.type === jobType;
    
    const salaryMinMatch = !salaryMin || job.salaryMax >= salaryMin;
    const salaryMaxMatch = !salaryMax || job.salaryMin <= salaryMax;
    
    const experienceMatch = !experienceLevel || job.experienceLevel === experienceLevel;
    const remoteMatch = !isRemote || job.isRemote;

    return searchMatch && locationMatch && typeMatch && salaryMinMatch && salaryMaxMatch && experienceMatch && remoteMatch;
  });

  // Check if any filters are applied
  $: hasActiveFilters = searchTerm || locationTerm || jobType || salaryMin || salaryMax || experienceLevel || isRemote;

  // Functions
  function toggleFiltersMobile() {
    showFiltersMobile = !showFiltersMobile;
  }

  function resetFilters() {
    searchTerm = '';
    locationTerm = '';
    jobType = '';
    salaryMin = null;
    salaryMax = null;
    experienceLevel = '';
    isRemote = false;
    showFiltersMobile = false;
  }

  function saveJob(jobId) {
    const jobIndex = jobs.findIndex(job => job.id === jobId);
    if (jobIndex !== -1) {
      jobs[jobIndex].saved = !jobs[jobIndex].saved;
      // Trigger reactivity
      // jobs = [...jobs];
    }
  }

  function viewJobDetails(jobId) {
    // In a real app, navigate to job details page
    // goto(`/jobs/${jobId}`);
    console.log(`Viewing job details for job ${jobId}`);
  }

  function formatSalary(min, max) {
    const formatNumber = (num) => (num / 1000).toFixed(0) + 'k';
    if (min && max) return `$${formatNumber(min)} - $${formatNumber(max)}`;
    if (min) return `From $${formatNumber(min)}`;
    if (max) return `Up to $${formatNumber(max)}`;
    return 'Competitive';
  }

  function timeSince(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} week${Math.floor(diffDays / 7) > 1 ? 's' : ''} ago`;
    return `${Math.floor(diffDays / 30)} month${Math.floor(diffDays / 30) > 1 ? 's' : ''} ago`;
  }
</script>

<svelte:head>
  <title>Job Search - HirePulse.in</title>
  <meta name="description" content="Find your dream job with HirePulse.in's advanced job search and filtering capabilities" />
</svelte:head>

<div class="min-h-screen bg-gray-50 text-gray-900">
  <!-- Header -->
  <header class="bg-white/80 backdrop-blur-sm border-b border-gray-200 sticky top-0 z-40 shadow-sm">
    <div class="max-w-7xl mx-auto px-4 py-6">
      <div class="text-center">
        <h1 class="text-3xl md:text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-cyan-600">
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
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- Keywords Search -->
          <div class="relative">
            <label for="search-keywords" class="block text-sm font-medium text-blue-700 mb-2">
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
            <label for="search-location" class="block text-sm font-medium text-blue-700 mb-2">
              Location
            </label>
            <div class="relative">
              <input
                id="search-location"
                type="text"
                bind:value={locationTerm}
                placeholder="City, state, or remote"
                class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 transition-all"
              />
              <MapPin class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <!-- Job Type -->
          <div>
            <label for="job-type" class="block text-sm font-medium text-blue-700 mb-2">
              Job Type
            </label>
            <select
              id="job-type"
              bind:value={jobType}
              class="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 transition-all"
            >
              <option value="">All Types</option>
              {#each allJobTypes as type}
                <option value={type}>{type}</option>
              {/each}
            </select>
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
        {#if hasActiveFilters}
          <span class="bg-cyan-500 text-white text-xs px-2 py-1 rounded-full font-medium">Active</span>
        {/if}
      </button>
      <div class="text-sm text-gray-600">
        {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
      </div>
    </div>

    <div class="flex flex-col md:flex-row gap-8">
      <!-- Filter Sidebar -->
      <aside class={`${showFiltersMobile ? 'block' : 'hidden'} md:block md:w-80 md:sticky md:top-32 self-start`}>
        <div class="bg-white rounded-xl p-6 border border-gray-200 shadow-sm">
          <div class="flex justify-between items-center mb-6">
            <h2 class="text-xl font-semibold text-blue-700 flex items-center gap-2">
              <Filter size={24} />
              Filters
            </h2>
            {#if hasActiveFilters}
              <button
                onclick={resetFilters}
                class="text-sm text-blue-600 hover:text-blue-700 transition-colors flex items-center gap-1"
              >
                <X size={16} />
                Reset
              </button>
            {/if}
          </div>

          <div class="space-y-6">
            <!-- Salary Range -->
            <div>
              <label class="block text-sm font-medium text-blue-700 mb-3">
                Salary Range (USD)
              </label>
              <div class="grid grid-cols-2 gap-3">
                <div>
                  <input
                    type="number"
                    bind:value={salaryMin}
                    placeholder="Min salary"
                    class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 text-sm transition-all"
                  />
                </div>
                <div>
                  <input
                    type="number"
                    bind:value={salaryMax}
                    placeholder="Max salary"
                    class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 text-sm transition-all"
                  />
                </div>
              </div>
            </div>

            <!-- Experience Level -->
            <div>
              <label for="experience-filter" class="block text-sm font-medium text-blue-700 mb-3">
                Experience Level
              </label>
              <select
                id="experience-filter"
                bind:value={experienceLevel}
                class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 transition-all"
              >
                <option value="">All Levels</option>
                {#each allExperienceLevels as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>

            <!-- Remote Toggle -->
            <div>
              <label class="flex items-center gap-3 text-sm font-medium text-blue-700 cursor-pointer">
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
            {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
          </div>
        </div>

        {#if filteredJobs.length > 0}
          <div class="space-y-4">
            {#each filteredJobs as job (job.id)}
              <article 
                class="bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 cursor-pointer group hover:shadow-lg hover:shadow-blue-100"
                onclick={() => viewJobDetails(job.id)}
                onkeydown={(e) => e.key === 'Enter' && viewJobDetails(job.id)}
                role="button"
                tabindex="0"
                aria-label="View details for {job.title} at {job.company}"
              >
                <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
                  <div class="flex-1">
                    <div class="flex items-start justify-between mb-3">
                      <h3 class="text-xl font-semibold text-blue-600 group-hover:text-blue-700 transition-colors">
                        {job.title}
                      </h3>
                      <button
                        onclick={(e) => e.stopPropagation()}={() => saveJob(job.id)}
                        class="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-blue-600 transition-all {job.saved ? 'text-blue-600 bg-gray-100' : ''}"
                        aria-label="Save {job.title}"
                      >
                        <Bookmark size={20} class={job.saved ? 'fill-current' : ''} />
                      </button>
                    </div>

                    <div class="space-y-2 mb-4">
                      <div class="flex items-center text-gray-700 text-sm">
                        <Building size={16} class="mr-2 text-blue-500" />
                        {job.company}
                      </div>
                      <div class="flex items-center text-gray-700 text-sm">
                        <MapPin size={16} class="mr-2 text-blue-500" />
                        {job.location}
                        {#if job.isRemote}
                          <span class="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">Remote</span>
                        {/if}
                      </div>
                      <div class="flex items-center text-gray-700 text-sm">
                        <DollarSign size={16} class="mr-2 text-green-600" />
                        {formatSalary(job.salaryMin, job.salaryMax)}
                      </div>
                    </div>

                    <div class="flex flex-wrap items-center gap-4 text-xs text-gray-600">
                      <div class="flex items-center gap-1">
                        <Briefcase size={14} />
                        {job.type}
                      </div>
                      <div class="flex items-center gap-1">
                        <Users size={14} />
                        {job.experienceLevel}
                      </div>
                      <div class="flex items-center gap-1">
                        <Clock size={14} />
                        {timeSince(job.postedDate)}
                      </div>
                      <div class="flex items-center gap-1">
                        <Users size={14} />
                        {job.applicants} applicants
                      </div>
                    </div>
                  </div>
                </div>
              </article>
            {/each}
          </div>

          <!-- Pagination -->
          <div class="mt-12 flex justify-center">
            <div class="flex items-center gap-2">
              <button class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors disabled:opacity-50" disabled>
                Previous
              </button>
              <div class="flex gap-1">
                <button class="px-3 py-2 bg-blue-600 text-white rounded-lg">1</button>
                <button class="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors">2</button>
                <button class="px-3 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors">3</button>
              </div>
              <button class="px-4 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-colors">
                Next
              </button>
            </div>
          </div>
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