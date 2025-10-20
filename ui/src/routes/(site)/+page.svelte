<script lang="ts">
  import { Search, Briefcase, Users, Star, MapPin, Brain, TrendingUp, Shield, Clock, ChevronRight, Building, DollarSign, Sparkles, GraduationCap, CalendarDays, UserCheck, ArrowRight, Code, Database, Palette, BarChart, Home, UserSquare2 } from '@lucide/svelte';
  import { goto } from '$app/navigation';
  import Autocomplete from '$lib/components/Autocomplete.svelte';
  import { searchSkills, searchLocations } from '$lib/api/search';
  import type { SkillSuggestion, LocationSuggestion } from '$lib/types/search';
  import type { PageData } from './$types';

  // Server-loaded data
  export let data: PageData;

  let jobKeyword = '';
  let location = '';
  let selectedJobType = 'full-time';
  let selectedSkill: SkillSuggestion | null = null;
  let selectedLocation: LocationSuggestion | null = null;

  // Autocomplete state
  let skillSuggestions: SkillSuggestion[] = [];
  let locationSuggestions: LocationSuggestion[] = [];
  let loadingSkills = false;
  let loadingLocations = false;

  // Use server-loaded data
  const topCategories = data.topCategories;
  const topLocations = data.topLocations;
  const featuredJobs = data.featuredJobs;

  const heroStats = [
    { label: 'Jobs', value: '10K+', icon: Briefcase },
    { label: 'Users', value: '50K+', icon: Users },
    { label: 'Companies', value: '5K+', icon: Building },
    { label: 'Cities', value: '100+', icon: MapPin }
  ];

  const jobTypes = [
    { id: 'full-time', label: 'Full Time', icon: Briefcase },
    { id: 'internship', label: 'Internship', icon: GraduationCap },
    { id: 'remote', label: 'Remote', icon: Home },
    { id: 'fresher', label: 'Fresher', icon: UserSquare2 }
  ];

  const stats = [
    { label: 'Active Jobs', value: '50,000+', icon: Briefcase },
    { label: 'Happy Users', value: '100,000+', icon: Users },
    { label: 'Companies', value: '5,000+', icon: Building },
    { label: 'Success Rate', value: '95%', icon: TrendingUp }
  ];




  async function handleSkillSearch(event: CustomEvent<string>) {
    const query = event.detail;
    loadingSkills = true;
    try {
      const response = await searchSkills(query);
      skillSuggestions = response.results;
    } catch (error) {
      console.error('Failed to search skills:', error);
      skillSuggestions = [];
    } finally {
      loadingSkills = false;
    }
  }

  async function handleLocationSearch(event: CustomEvent<string>) {
    const query = event.detail;
    loadingLocations = true;
    try {
      const response = await searchLocations(query);
      locationSuggestions = response.results;
    } catch (error) {
      console.error('Failed to search locations:', error);
      locationSuggestions = [];
    } finally {
      loadingLocations = false;
    }
  }

  function handleSkillSelect(event: CustomEvent<{ id: number; name: string }>) {
    selectedSkill = event.detail as SkillSuggestion;
    jobKeyword = event.detail.name;
  }

  function handleLocationSelect(event: CustomEvent<{ id: number; name: string }>) {
    selectedLocation = event.detail as LocationSuggestion;
    location = event.detail.name;
  }

  function handleSkillClear() {
    selectedSkill = null;
    jobKeyword = '';
    skillSuggestions = [];
  }

  function handleLocationClear() {
    selectedLocation = null;
    location = '';
    locationSuggestions = [];
  }

  function handleSearch(event: Event) {
    event.preventDefault();

    // Build query parameters for job search
    const params = new URLSearchParams();

    // Add skill filter if provided
    if (selectedSkill?.slug) {
      params.append('skills', selectedSkill.slug);
    } else if (jobKeyword.trim()) {
      // If no skill selected but keyword typed, add to search
      params.append('search', jobKeyword.trim());
    }

    // Add location filter if provided
    if (selectedLocation?.slug) {
      params.append('location', selectedLocation.slug);
    } else if (location.trim()) {
      // If no location selected but text typed, add to search
      if (!params.has('search')) {
        params.append('search', location.trim());
      }
    }

    // Add job type filter
    if (selectedJobType) {
      // Handle special job types
      if (selectedJobType === 'remote') {
        params.append('is_remote', 'true');
      } else if (selectedJobType === 'fresher') {
        params.append('fresher', 'true');
      } else {
        // Regular job types (full-time, internship, etc.)
        params.append('job_type', selectedJobType);
      }
    }

    // Navigate to jobs page with filters using SvelteKit navigation
    const queryString = params.toString();
    goto(`/jobs/${queryString ? '?' + queryString : ''}`);
  }

  function selectJobType(typeId: string) {
    selectedJobType = typeId;
  }
</script>

<svelte:head>
  <title>PeelJobs - Find Your Dream Job with Smart Precision | AI-Powered Job Matching</title>
  <meta name="description" content="PeelJobs uses advanced AI to match you with perfect job opportunities across India. Search thousands of jobs, get personalized recommendations, and accelerate your career growth." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-12 md:py-16 lg:py-20 relative overflow-hidden">
  <div class="container mx-auto px-4 lg:px-6 relative z-10">
    <div class="max-w-4xl mx-auto">
      <!-- Content -->
      <div class="space-y-6">
        <!-- AI Badge -->
        <div class="inline-flex items-center gap-2 bg-blue-800 bg-opacity-50 px-4 py-2 rounded-full text-sm border border-blue-600">
          <Sparkles size={16} class="text-blue-300" />
          <span>AI-Powered Job Matching</span>
        </div>

        <!-- Heading -->
        <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold leading-tight animate-fade-in-down">
          Find Your Dream Job with
          <span class="text-blue-300">Smart Precision</span>
        </h1>

        <p class="text-base md:text-lg text-blue-100 leading-relaxed animate-fade-in-up max-w-xl">
          Join thousands of professionals who've accelerated their careers with our intelligent job matching platform. Your perfect opportunity is just one search away.
        </p>

        <!-- Search Form -->
        <form onsubmit={handleSearch} class="bg-white p-4 md:p-6 rounded-xl shadow-2xl animate-fade-in space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
            <!-- Location Autocomplete -->
            <div>
              <Autocomplete
                id="location-search"
                placeholder="Select Location"
                bind:value={location}
                icon={MapPin}
                suggestions={locationSuggestions}
                loading={loadingLocations}
                showJobCount={true}
                on:search={handleLocationSearch}
                on:select={handleLocationSelect}
                on:clear={handleLocationClear}
              />
            </div>

            <!-- Skills Autocomplete with Search Button -->
            <div class="flex gap-2">
              <div class="flex-1">
                <Autocomplete
                  id="job-search"
                  placeholder="Enter skills or job title"
                  bind:value={jobKeyword}
                  icon={Search}
                  suggestions={skillSuggestions}
                  loading={loadingSkills}
                  showJobCount={true}
                  on:search={handleSkillSearch}
                  on:select={handleSkillSelect}
                  on:clear={handleSkillClear}
                />
              </div>
              <button
                type="submit"
                class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition duration-200 flex items-center gap-2 shadow-lg hover:shadow-xl whitespace-nowrap"
              >
                <Search size={18} />
                <span class="hidden md:inline">Search Jobs</span>
              </button>
            </div>
          </div>

          <!-- Job Type Filters -->
          <div class="flex flex-wrap gap-2">
            {#each jobTypes as jobType}
              <button
                type="button"
                onclick={() => selectJobType(jobType.id)}
                class="flex items-center gap-2 px-4 py-2 rounded-lg border transition-all duration-200 {selectedJobType === jobType.id
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:border-blue-400 hover:bg-blue-50'}"
              >
                <svelte:component this={jobType.icon} size={16} />
                <span class="text-sm font-medium">{jobType.label}</span>
              </button>
            {/each}
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

<!-- Browse Jobs Section -->
<section class="py-16 lg:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <!-- Browse by Category -->
    <div class="mb-16">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-800 mb-2">Browse Jobs by Category</h2>
          <p class="text-gray-600">Explore opportunities across different industries</p>
        </div>
        <a
          href="/jobs/"
          class="hidden md:flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold transition-colors"
        >
          View All Jobs
          <ArrowRight size={18} />
        </a>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {#each topCategories as category}
          <a
            href="/jobs/?industry={category.slug}"
            class="group bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
          >
            <div class="flex items-center mb-3">
              <Briefcase size={20} class="text-blue-600" />
            </div>
            <h3 class="font-semibold text-gray-800 group-hover:text-blue-600 transition-colors text-sm leading-snug">
              {category.name}
            </h3>
          </a>
        {/each}
      </div>
    </div>

    <!-- Browse by Location -->
    <div>
      <div class="flex items-center justify-between mb-8">
        <div>
          <h2 class="text-2xl lg:text-3xl font-bold text-gray-800 mb-2">Browse Jobs by Location</h2>
          <p class="text-gray-600">Find opportunities in your preferred city</p>
        </div>
      </div>

      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {#each topLocations as location}
          <a
            href="/jobs/?location={location.slug}"
            class="group bg-gray-50 hover:bg-blue-50 border border-gray-200 hover:border-blue-300 rounded-lg p-4 transition-all duration-200 hover:shadow-md"
          >
            <div class="flex items-center mb-3">
              <MapPin size={20} class="text-blue-600" />
            </div>
            <h3 class="font-semibold text-gray-800 group-hover:text-blue-600 transition-colors text-sm leading-snug">
              {location.name}
            </h3>
          </a>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- Platform Highlights -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Why Choose PeelJobs?</h2>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto">Experience the future of job searching with our cutting-edge features designed to accelerate your career.</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-blue-100 rounded-full">
            <Brain class="text-blue-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">AI-Powered Matching</h3>
        <p class="text-gray-600 text-center leading-relaxed">Our advanced algorithms analyze your skills, experience, and preferences to find the most relevant opportunities.</p>
      </div>
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-green-100 rounded-full">
            <Shield class="text-green-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Verified Companies</h3>
        <p class="text-gray-600 text-center leading-relaxed">All employers are thoroughly vetted to ensure you're applying to legitimate, high-quality opportunities.</p>
      </div>
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-purple-100 rounded-full">
            <Clock class="text-purple-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Fast Applications</h3>
        <p class="text-gray-600 text-center leading-relaxed">Apply to multiple jobs in minutes with our streamlined application process and smart autofill features.</p>
      </div>
    </div>
  </div>
</section>

<!-- Featured Jobs Section -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Latest Job Opportunities</h2>
      <p class="text-lg text-gray-600">Explore the newest openings from companies across India</p>
    </div>

    <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
      {#each featuredJobs as job (job.id)}
        <a
          href="{job.slug}"
          class="group bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100"
        >
          <div class="p-6">
            <div class="flex items-start mb-4">
              <img
                src={job.company_logo}
                alt="{job.company_name} logo"
                class="w-12 h-12 rounded-lg mr-3 object-cover border border-gray-200"
                onerror={(e) => {
                  const target = e.target as HTMLImageElement;
                  const initial = job.company_name.charAt(0).toUpperCase();
                  target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23E5E7EB' width='48' height='48'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='20' fill='%236B7280'%3E${initial}%3C/text%3E%3C/svg%3E`;
                }}
              >
              <div class="flex-1">
                <h3 class="font-bold text-gray-800 text-base leading-tight group-hover:text-blue-600 transition-colors mb-1 line-clamp-2">
                  {job.title}
                </h3>
                <p class="text-gray-600 text-sm truncate">{job.company_name}</p>
              </div>
            </div>

            <div class="space-y-2 mb-4">
              <div class="flex items-center text-gray-600 text-sm">
                <MapPin size={14} class="mr-2 text-gray-400 flex-shrink-0" />
                <span class="truncate">{job.location_display}</span>
              </div>
              <div class="flex items-center text-gray-600 text-sm">
                <Briefcase size={14} class="mr-2 text-gray-400 flex-shrink-0" />
                <span class="truncate">{job.experience_display}</span>
              </div>
              {#if job.salary_display}
                <div class="flex items-center text-gray-600 text-sm">
                  <DollarSign size={14} class="mr-2 text-gray-400 flex-shrink-0" />
                  <span class="truncate">{job.salary_display}</span>
                </div>
              {/if}
            </div>

            <div class="flex flex-wrap gap-1 mb-4">
              {#each job.skills.slice(0, 3) as skill}
                <span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">{skill.name}</span>
              {/each}
              {#if job.skills.length > 3}
                <span class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full">+{job.skills.length - 3}</span>
              {/if}
            </div>

            <div class="flex items-center justify-between pt-2 border-t border-gray-100">
              <span class="text-xs text-gray-500">{job.time_ago}</span>
              <span class="text-blue-600 text-sm font-medium inline-flex items-center group-hover:text-blue-700">
                View Details
                <ChevronRight size={14} class="ml-1" />
              </span>
            </div>
          </div>
        </a>
      {/each}
    </div>

    <div class="text-center">
      <a href="/jobs/" class="inline-flex items-center bg-transparent hover:bg-blue-600 text-blue-600 font-semibold hover:text-white py-3 px-8 border-2 border-blue-500 hover:border-blue-600 rounded-lg transition duration-200">
        View All Jobs
        <ChevronRight size={20} class="ml-2" />
      </a>
    </div>
  </div>
</section>

<!-- CTA Section -->
<section class="py-16 lg:py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
  <div class="container mx-auto px-4 lg:px-6 text-center">
    <h2 class="text-3xl lg:text-4xl font-bold mb-6">Ready to Transform Your Career?</h2>
    <p class="text-lg lg:text-xl mb-8 max-w-2xl mx-auto text-blue-100">
      Join thousands of professionals who've found their dream jobs through our AI-powered platform.
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="/register/" class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition duration-200 inline-flex items-center justify-center">
        Get Started Free
        <ChevronRight size={20} class="ml-2" />
      </a>
      <a href="/jobs/" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition duration-200">
        Browse Jobs
      </a>
    </div>
  </div>
</section>

<style>
  /* Enhanced animations */
  .animate-fade-in-down {
    animation: fadeInDown 0.8s ease-out forwards;
  }
  .animate-fade-in-up {
    animation: fadeInUp 0.8s ease-out 0.2s forwards;
    opacity: 0;
  }
  .animate-fade-in {
    animation: fadeIn 1s ease-out 0.4s forwards;
    opacity: 0;
  }

  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  /* Smooth scrolling for anchor links */
  :global(html) {
    scroll-behavior: smooth;
  }
</style>
