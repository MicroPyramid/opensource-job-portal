<script lang="ts">
  import { Search, Filter, SlidersHorizontal, X, MapPin, Briefcase, DollarSign, Bookmark, Building, Clock, Users, GraduationCap, Factory } from '@lucide/svelte';
  import FilterSection from '$lib/components/FilterSection.svelte';
  import FilterModal from '$lib/components/FilterModal.svelte';

  interface FilterOption {
    name: string;
    value: string;
    count: number;
    checked: boolean;
  }

  type JobType = 'full-time' | 'internship' | 'walk-in' | 'fresher';

  interface Job {
    id: number;
    title: string;
    company: string;
    location: string;
    salaryMin: number;
    salaryMax: number;
    postedDate: string;
    type: JobType;
    experienceMin: number;
    experienceMax: number;
    isRemote: boolean;
    applicants: number;
    saved: boolean;
    skills: string[];
    industry: string;
    education: string;
  }

  // Search and filter state
  let searchTerm = $state('');
  let locationSearchTerm = $state('');
  let jobTypeFilter = $state<JobType | ''>('');
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

  // Filter options with job counts
  let locationOptions = $state<FilterOption[]>([
    { name: 'Chennai', value: 'chennai', count: 2250, checked: false },
    { name: 'Bangalore', value: 'bangalore', count: 2234, checked: false },
    { name: 'Mumbai', value: 'mumbai', count: 2190, checked: false },
    { name: 'Kolkata', value: 'kolkata', count: 2173, checked: false },
    { name: 'Delhi', value: 'delhi', count: 1922, checked: false },
    { name: 'Hyderabad', value: 'hyderabad', count: 1856, checked: false },
    { name: 'Noida', value: 'noida', count: 1645, checked: false },
    { name: 'Gurgaon', value: 'gurgaon', count: 1542, checked: false },
    { name: 'Pune', value: 'pune', count: 1489, checked: false },
    { name: 'Ahmedabad', value: 'ahmedabad', count: 1321, checked: false },
  ]);

  let skillOptions = $state<FilterOption[]>([
    { name: 'Basic Computer Knowledge', value: 'basic-computer-knowledge', count: 1565, checked: false },
    { name: 'Basic Computer Skills', value: 'basic-computer-skills', count: 1279, checked: false },
    { name: 'Sales', value: 'sales', count: 891, checked: false },
    { name: 'Communication Skills', value: 'communication-skills', count: 861, checked: false },
    { name: 'Java', value: 'java', count: 860, checked: false },
    { name: 'JavaScript', value: 'javascript', count: 752, checked: false },
    { name: 'Python', value: 'python', count: 720, checked: false },
    { name: 'PHP', value: 'php', count: 680, checked: false },
    { name: 'HTML', value: 'html', count: 650, checked: false },
    { name: 'CSS', value: 'css', count: 620, checked: false },
  ]);

  let industryOptions = $state<FilterOption[]>([
    { name: 'IT Services', value: 'it-services', count: 5531, checked: false },
    { name: 'BPO', value: 'bpo', count: 2430, checked: false },
    { name: 'Advertising', value: 'advertising', count: 1364, checked: false },
    { name: 'Other', value: 'other', count: 660, checked: false },
    { name: 'Education', value: 'education', count: 651, checked: false },
    { name: 'Banking', value: 'banking', count: 580, checked: false },
    { name: 'Healthcare', value: 'healthcare', count: 520, checked: false },
    { name: 'E-commerce', value: 'e-commerce', count: 480, checked: false },
  ]);

  let educationOptions = $state<FilterOption[]>([
    { name: 'Graduate', value: 'graduate', count: 4914, checked: false },
    { name: '12th pass', value: '12th-pass', count: 3008, checked: false },
    { name: 'B.Tech', value: 'btech', count: 2532, checked: false },
    { name: 'MCA', value: 'mca', count: 1124, checked: false },
    { name: '10th pass', value: '10th-pass', count: 1004, checked: false },
    { name: 'MBA', value: 'mba', count: 892, checked: false },
    { name: 'M.Tech', value: 'mtech', count: 756, checked: false },
  ]);

  let jobTypeOptions = $state<FilterOption[]>([
    { name: 'Full-Time', value: 'full-time', count: 8500, checked: false },
    { name: 'Internship', value: 'internship', count: 1200, checked: false },
    { name: 'Walk-in', value: 'walk-in', count: 850, checked: false },
    { name: 'Fresher', value: 'fresher', count: 3200, checked: false },
  ]);

  // Dummy job data (expanded with new fields)
  let jobs = $state<Job[]>([
    {
      id: 1,
      title: 'Senior Software Engineer',
      company: 'Tech Solutions Inc.',
      location: 'chennai',
      salaryMin: 12,
      salaryMax: 16,
      postedDate: '2024-01-15',
      type: 'full-time',
      experienceMin: 5,
      experienceMax: 8,
      isRemote: false,
      applicants: 45,
      saved: false,
      skills: ['java', 'python'],
      industry: 'it-services',
      education: 'btech'
    },
    {
      id: 2,
      title: 'Frontend Developer',
      company: 'Web Wizards LLC',
      location: 'bangalore',
      salaryMin: 8,
      salaryMax: 11,
      postedDate: '2024-01-12',
      type: 'full-time',
      experienceMin: 2,
      experienceMax: 4,
      isRemote: true,
      applicants: 78,
      saved: false,
      skills: ['javascript', 'html', 'css'],
      industry: 'it-services',
      education: 'graduate'
    },
    {
      id: 3,
      title: 'Product Manager',
      company: 'Innovate Co.',
      location: 'mumbai',
      salaryMin: 13,
      salaryMax: 18,
      postedDate: '2024-01-10',
      type: 'full-time',
      experienceMin: 5,
      experienceMax: 10,
      isRemote: false,
      applicants: 32,
      saved: false,
      skills: ['communication-skills'],
      industry: 'it-services',
      education: 'mba'
    },
    {
      id: 4,
      title: 'UX Designer',
      company: 'Creative Designs',
      location: 'delhi',
      salaryMin: 7,
      salaryMax: 9.5,
      postedDate: '2024-01-18',
      type: 'internship',
      experienceMin: 1,
      experienceMax: 3,
      isRemote: false,
      applicants: 23,
      saved: false,
      skills: ['basic-computer-skills'],
      industry: 'advertising',
      education: 'graduate'
    },
    {
      id: 5,
      title: 'DevOps Engineer',
      company: 'CloudNet Systems',
      location: 'hyderabad',
      salaryMin: 10,
      salaryMax: 14,
      postedDate: '2024-01-05',
      type: 'full-time',
      experienceMin: 4,
      experienceMax: 7,
      isRemote: true,
      applicants: 56,
      saved: false,
      skills: ['python'],
      industry: 'it-services',
      education: 'btech'
    },
    {
      id: 6,
      title: 'Data Analyst',
      company: 'Analytics Corp',
      location: 'pune',
      salaryMin: 6.5,
      salaryMax: 8.5,
      postedDate: '2024-01-20',
      type: 'fresher',
      experienceMin: 0,
      experienceMax: 1,
      isRemote: false,
      applicants: 67,
      saved: false,
      skills: ['basic-computer-knowledge'],
      industry: 'bpo',
      education: 'graduate'
    },
    {
      id: 7,
      title: 'Full Stack Developer',
      company: 'StartupHub',
      location: 'bangalore',
      salaryMin: 9,
      salaryMax: 12,
      postedDate: '2024-01-22',
      type: 'full-time',
      experienceMin: 3,
      experienceMax: 5,
      isRemote: true,
      applicants: 89,
      saved: false,
      skills: ['javascript', 'java', 'html', 'css'],
      industry: 'it-services',
      education: 'btech'
    },
    {
      id: 8,
      title: 'Marketing Specialist',
      company: 'Growth Co.',
      location: 'mumbai',
      salaryMin: 5.5,
      salaryMax: 7.5,
      postedDate: '2024-01-14',
      type: 'full-time',
      experienceMin: 1,
      experienceMax: 3,
      isRemote: false,
      applicants: 34,
      saved: false,
      skills: ['sales', 'communication-skills'],
      industry: 'advertising',
      education: 'graduate'
    }
  ]);

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

  // Reactive filtered jobs
  let filteredJobs = $derived<Job[]>(
    (() => {
      const searchTermLower = searchTerm.toLowerCase();
      const locationTermLower = locationSearchTerm.toLowerCase();

      const selectedLocations = locationOptions.filter(opt => opt.checked).map(opt => opt.value);
      const selectedSkills = skillOptions.filter(opt => opt.checked).map(opt => opt.value);
      const selectedIndustries = industryOptions.filter(opt => opt.checked).map(opt => opt.value);
      const selectedEducation = educationOptions.filter(opt => opt.checked).map(opt => opt.value);
      const selectedJobTypes = jobTypeOptions.filter(opt => opt.checked).map(opt => opt.value);

      return jobs.filter(job => {
        const searchMatch =
          searchTermLower === '' ||
          job.title.toLowerCase().includes(searchTermLower) ||
          job.company.toLowerCase().includes(searchTermLower);

        const locationSearchMatch =
          locationTermLower === '' ||
          job.location.toLowerCase().includes(locationTermLower);

        const locationMatch =
          selectedLocations.length === 0 ||
          selectedLocations.includes(job.location);

        const skillMatch =
          selectedSkills.length === 0 ||
          job.skills.some(skill => selectedSkills.includes(skill));

        const industryMatch =
          selectedIndustries.length === 0 ||
          selectedIndustries.includes(job.industry);

        const educationMatch =
          selectedEducation.length === 0 ||
          selectedEducation.includes(job.education);

        const jobTypeMatch =
          selectedJobTypes.length === 0 ||
          selectedJobTypes.includes(job.type);

        const salaryMinMatch = salaryMin === null || job.salaryMax >= salaryMin;
        const salaryMaxMatch = salaryMax === null || job.salaryMin <= salaryMax;

        const experienceMinMatch = job.experienceMax >= experienceMin;
        const experienceMaxMatch = job.experienceMin <= experienceMax;

        const remoteMatch = !isRemote || job.isRemote;

        return (
          searchMatch &&
          locationSearchMatch &&
          locationMatch &&
          skillMatch &&
          industryMatch &&
          educationMatch &&
          jobTypeMatch &&
          salaryMinMatch &&
          salaryMaxMatch &&
          experienceMinMatch &&
          experienceMaxMatch &&
          remoteMatch
        );
      });
    })()
  );

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
    showFiltersMobile = false;
  }

  function saveJob(jobId: number): void {
    const jobIndex = jobs.findIndex(job => job.id === jobId);
    if (jobIndex !== -1) {
      jobs[jobIndex].saved = !jobs[jobIndex].saved;
      jobs = [...jobs];
    }
  }

  function viewJobDetails(jobId: number): void {
    console.log(`Viewing job details for job ${jobId}`);
  }

  function formatSalary(min: number | null, max: number | null): string {
    if (min !== null && max !== null) return `₹${min} - ₹${max} LPA`;
    if (min !== null) return `From ₹${min} LPA`;
    if (max !== null) return `Up to ₹${max} LPA`;
    return 'Competitive';
  }

  function formatLocation(location: string): string {
    const option = locationOptions.find(opt => opt.value === location);
    return option ? option.name : location;
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
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
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
                placeholder="City, state, or remote"
                class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500 transition-all"
              />
              <MapPin class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
          </div>

          <!-- Job Type -->
          <div>
            <label for="job-type" class="block text-sm font-medium text-gray-700 mb-2">
              Quick Filter
            </label>
            <select
              id="job-type"
              bind:value={jobTypeFilter}
              class="w-full px-4 py-3 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 transition-all"
            >
              <option value="">All Types</option>
              <option value="full-time">Full-Time</option>
              <option value="internship">Internship</option>
              <option value="walk-in">Walk-in</option>
              <option value="fresher">Fresher</option>
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
        {#if activeFilterCount > 0}
          <span class="bg-cyan-400 text-white text-xs px-2 py-1 rounded-full font-medium">{activeFilterCount}</span>
        {/if}
      </button>
      <div class="text-sm text-gray-600">
        {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
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
            <FilterSection
              title="Location"
              icon={MapPin}
              options={locationOptions}
              showMoreButton={true}
              onToggle={toggleLocationFilter}
              onShowMore={() => showLocationModal = true}
            />

            <!-- Skills Filter -->
            <FilterSection
              title="Skills"
              icon={Briefcase}
              options={skillOptions}
              showMoreButton={true}
              onToggle={toggleSkillFilter}
              onShowMore={() => showSkillsModal = true}
            />

            <!-- Industry Filter -->
            <FilterSection
              title="Industry"
              icon={Factory}
              options={industryOptions}
              showMoreButton={true}
              onToggle={toggleIndustryFilter}
              onShowMore={() => showIndustryModal = true}
            />

            <!-- Education Filter -->
            <FilterSection
              title="Education"
              icon={GraduationCap}
              options={educationOptions}
              showMoreButton={true}
              onToggle={toggleEducationFilter}
              onShowMore={() => showEducationModal = true}
            />

            <!-- Job Type Filter -->
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
                    </label>
                  {/each}
                </div>
              </div>
            </div>

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
            {filteredJobs.length} job{filteredJobs.length !== 1 ? 's' : ''} found
          </div>
        </div>

        {#if filteredJobs.length > 0}
          <div class="space-y-4">
            {#each filteredJobs as job (job.id)}
              <button
                type="button"
                class="w-full text-left bg-white rounded-xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 cursor-pointer group hover:shadow-lg hover:shadow-blue-100"
                onclick={() => viewJobDetails(job.id)}
                aria-label="View details for {job.title} at {job.company}"
              >
                <div class="flex flex-col sm:flex-row justify-between items-start gap-4">
                  <div class="flex-1">
                    <div class="flex items-start justify-between mb-3">
                      <h3 class="text-xl font-semibold text-blue-600 group-hover:text-blue-700 transition-colors">
                        {job.title}
                      </h3>
                      <span
                        role="button"
                        tabindex="0"
                        onclick={(event) => {
                          event.stopPropagation();
                          saveJob(job.id);
                        }}
                        onkeydown={(event) => {
                          if (event.key === 'Enter' || event.key === ' ') {
                            event.preventDefault();
                            event.stopPropagation();
                            saveJob(job.id);
                          }
                        }}
                        class="p-2 rounded-lg hover:bg-gray-100 text-gray-400 hover:text-blue-600 transition-all {job.saved ? 'text-blue-600 bg-gray-100' : ''}"
                        aria-label="Save {job.title}"
                      >
                        <Bookmark size={20} class={job.saved ? 'fill-current' : ''} />
                      </span>
                    </div>

                    <div class="space-y-2 mb-4">
                      <div class="flex items-center text-gray-700 text-sm">
                        <Building size={16} class="mr-2 text-blue-500" />
                        {job.company}
                      </div>
                      <div class="flex items-center text-gray-700 text-sm">
                        <MapPin size={16} class="mr-2 text-blue-500" />
                        {formatLocation(job.location)}
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
                        {job.experienceMin}-{job.experienceMax} years
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
              </button>
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
