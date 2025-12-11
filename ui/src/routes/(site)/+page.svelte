<script lang="ts">
  import { Search, Briefcase, MapPin, Brain, Shield, Clock, ChevronRight, Building2, IndianRupee, Sparkles, GraduationCap, ArrowRight, Home, Users, Zap, TrendingUp, CheckCircle2, Star } from '@lucide/svelte';
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

  const jobTypes = [
    { id: 'full-time', label: 'Full Time', icon: Briefcase },
    { id: 'internship', label: 'Internship', icon: GraduationCap },
    { id: 'remote', label: 'Remote', icon: Home },
    { id: 'fresher', label: 'Fresher', icon: Users }
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
    const params = new URLSearchParams();

    if (selectedSkill?.slug) {
      params.append('skills', selectedSkill.slug);
    } else if (jobKeyword.trim()) {
      params.append('search', jobKeyword.trim());
    }

    if (selectedLocation?.slug) {
      params.append('location', selectedLocation.slug);
    } else if (location.trim()) {
      if (!params.has('search')) {
        params.append('search', location.trim());
      }
    }

    if (selectedJobType) {
      if (selectedJobType === 'remote') {
        params.append('is_remote', 'true');
      } else if (selectedJobType === 'fresher') {
        params.append('fresher', 'true');
      } else {
        params.append('job_type', selectedJobType);
      }
    }

    const queryString = params.toString();
    goto(`/jobs/${queryString ? '?' + queryString : ''}`);
  }

  function selectJobType(typeId: string) {
    selectedJobType = typeId;
  }

  // Stats for social proof
  const stats = [
    { value: '50K+', label: 'Active Jobs' },
    { value: '10K+', label: 'Companies' },
    { value: '1M+', label: 'Job Seekers' },
    { value: '95%', label: 'Success Rate' }
  ];
</script>

<svelte:head>
  <title>PeelJobs - Find Your Dream Job | India's Smart Job Platform</title>
  <meta name="description" content="Discover thousands of job opportunities across India. PeelJobs connects talented professionals with top companies using intelligent job matching." />
</svelte:head>

<!-- Hero Section - Material Design 3 with clean, elevated aesthetic -->
<section class="bg-white">
  <div class="max-w-7xl mx-auto px-4 lg:px-8 pt-12 pb-20 md:pt-16 md:pb-28 lg:pt-20 lg:pb-32">
    <div class="max-w-3xl mx-auto text-center">
      <!-- Badge -->
      <div class="inline-flex items-center gap-2 px-4 py-2 bg-primary-50 rounded-full text-primary-700 text-sm font-medium mb-8 animate-fade-in-down">
        <Sparkles size={16} />
        <span>Smart Job Matching Platform</span>
      </div>

      <!-- Heading -->
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 tracking-tight leading-tight mb-6 animate-fade-in-down delay-100" style="opacity: 0;">
        Find the job that
        <span class="text-primary-600">fits your life</span>
      </h1>

      <p class="text-lg md:text-xl text-gray-600 leading-relaxed mb-10 max-w-2xl mx-auto animate-fade-in-up delay-200" style="opacity: 0;">
        Join millions of professionals who trust PeelJobs to connect them with opportunities at India's top companies.
      </p>

      <!-- Search Form - Elevated Card Style -->
      <form onsubmit={handleSearch} class="bg-white rounded-2xl elevation-3 p-4 md:p-6 animate-scale-in delay-300 max-w-2xl mx-auto" style="opacity: 0;">
        <div class="flex flex-col md:flex-row gap-3">
          <!-- Location Input -->
          <div class="flex-1">
            <Autocomplete
              id="location-search"
              placeholder="City or Location"
              bind:value={location}
              icon={MapPin}
              suggestions={locationSuggestions}
              loading={loadingLocations}
              showJobCount={true}
              inputClass="!rounded-xl !border-gray-200 !bg-gray-50 focus:!bg-white"
              on:search={handleLocationSearch}
              on:select={handleLocationSelect}
              on:clear={handleLocationClear}
            />
          </div>

          <!-- Skills/Job Input -->
          <div class="flex-1">
            <Autocomplete
              id="job-search"
              placeholder="Skills or Job Title"
              bind:value={jobKeyword}
              icon={Search}
              suggestions={skillSuggestions}
              loading={loadingSkills}
              showJobCount={true}
              inputClass="!rounded-xl !border-gray-200 !bg-gray-50 focus:!bg-white"
              on:search={handleSkillSearch}
              on:select={handleSkillSelect}
              on:clear={handleSkillClear}
            />
          </div>

          <!-- Search Button -->
          <button
            type="submit"
            class="flex items-center justify-center gap-2 px-8 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-xl transition-all duration-200 elevation-1 hover:elevation-2 whitespace-nowrap"
          >
            <Search size={20} />
            <span class="hidden md:inline">Search</span>
          </button>
        </div>

        <!-- Job Type Chips -->
        <div class="flex flex-wrap justify-center gap-2 mt-5 pt-5 border-t border-gray-100">
          {#each jobTypes as jobType}
            <button
              type="button"
              onclick={() => selectJobType(jobType.id)}
              class="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 {selectedJobType === jobType.id
                ? 'bg-primary-600 text-white elevation-1'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}"
            >
              <svelte:component this={jobType.icon} size={16} />
              <span>{jobType.label}</span>
            </button>
          {/each}
        </div>
      </form>

      <!-- Quick Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 mt-12 animate-fade-in-up delay-500" style="opacity: 0;">
        {#each stats as stat, i}
          <div class="text-center">
            <div class="text-2xl md:text-3xl font-bold text-gray-900">{stat.value}</div>
            <div class="text-sm text-gray-500 mt-1">{stat.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- Browse by Category - Material Design Cards -->
<section class="py-16 lg:py-24 bg-surface-50">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
      <div>
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">Browse by Category</h2>
        <p class="text-gray-600 mt-2">Explore opportunities across different industries</p>
      </div>
      <a
        href="/jobs/"
        class="inline-flex items-center gap-2 text-primary-600 font-medium hover:text-primary-700 transition-colors group"
      >
        View All Jobs
        <ArrowRight size={18} class="group-hover:translate-x-1 transition-transform" />
      </a>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {#each topCategories as category, i}
        <a
          href="/jobs/?industry={category.slug}"
          class="group bg-white rounded-2xl p-5 transition-all duration-300 hover:elevation-3 border border-gray-100 hover:border-primary-200"
          style="animation: fade-in-up 0.5s ease forwards; animation-delay: {i * 50}ms; opacity: 0;"
        >
          <div class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center mb-4 group-hover:bg-primary-100 transition-colors">
            <Building2 size={22} class="text-primary-600" />
          </div>
          <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2">
            {category.name}
          </h3>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- Browse by Location -->
<section class="py-16 lg:py-24 bg-white">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
      <div>
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">Jobs by Location</h2>
        <p class="text-gray-600 mt-2">Find opportunities in your preferred city</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {#each topLocations as loc, i}
        <a
          href="/jobs/?location={loc.slug}"
          class="group flex items-center gap-4 bg-surface-50 rounded-2xl p-4 transition-all duration-300 hover:bg-primary-50 border border-transparent hover:border-primary-200"
          style="animation: fade-in-up 0.5s ease forwards; animation-delay: {i * 50}ms; opacity: 0;"
        >
          <div class="w-10 h-10 rounded-xl bg-white flex items-center justify-center group-hover:bg-primary-100 transition-colors elevation-1">
            <MapPin size={18} class="text-primary-600" />
          </div>
          <span class="font-medium text-gray-900 group-hover:text-primary-700 transition-colors">{loc.name}</span>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- Why Choose PeelJobs - Feature Cards -->
<section class="py-16 lg:py-24 bg-gray-900 text-white">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="text-center mb-16">
      <h2 class="text-3xl lg:text-4xl font-bold tracking-tight mb-4">Why Choose PeelJobs?</h2>
      <p class="text-lg text-gray-400 max-w-2xl mx-auto">
        Experience the future of job searching with features designed for your success.
      </p>
    </div>

    <div class="grid md:grid-cols-3 gap-6 lg:gap-8">
      <!-- Feature 1 -->
      <div class="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300">
        <div class="w-14 h-14 rounded-2xl bg-primary-500/20 flex items-center justify-center mb-6">
          <Brain size={28} class="text-primary-400" />
        </div>
        <h3 class="text-xl font-bold mb-3">Smart Matching</h3>
        <p class="text-gray-400 leading-relaxed">
          Our intelligent algorithms analyze your skills and experience to surface the most relevant opportunities for you.
        </p>
      </div>

      <!-- Feature 2 -->
      <div class="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300">
        <div class="w-14 h-14 rounded-2xl bg-success-500/20 flex items-center justify-center mb-6">
          <Shield size={28} class="text-success-500" />
        </div>
        <h3 class="text-xl font-bold mb-3">Verified Companies</h3>
        <p class="text-gray-400 leading-relaxed">
          Every employer is thoroughly vetted to ensure you're applying to legitimate, trustworthy opportunities.
        </p>
      </div>

      <!-- Feature 3 -->
      <div class="bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:bg-white/10 transition-all duration-300">
        <div class="w-14 h-14 rounded-2xl bg-warning-500/20 flex items-center justify-center mb-6">
          <Zap size={28} class="text-warning-500" />
        </div>
        <h3 class="text-xl font-bold mb-3">Quick Apply</h3>
        <p class="text-gray-400 leading-relaxed">
          Apply to multiple jobs in minutes with our streamlined process and smart profile autofill.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Featured Jobs Section -->
<section class="py-16 lg:py-24 bg-surface-50">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-10">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-success-500/10 rounded-full text-success-600 text-sm font-medium mb-3">
          <TrendingUp size={14} />
          <span>Latest Openings</span>
        </div>
        <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight">Featured Jobs</h2>
        <p class="text-gray-600 mt-2">Fresh opportunities from top companies across India</p>
      </div>
      <a
        href="/jobs/"
        class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white font-medium rounded-full hover:bg-primary-700 transition-colors elevation-1"
      >
        View All Jobs
        <ArrowRight size={18} />
      </a>
    </div>

    <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-5">
      {#each featuredJobs as job, i (job.id)}
        <a
          href="{job.slug}"
          class="group bg-white rounded-2xl overflow-hidden transition-all duration-300 hover:elevation-3 border border-gray-100"
          style="animation: fade-in-up 0.5s ease forwards; animation-delay: {i * 75}ms; opacity: 0;"
        >
          <div class="p-5">
            <!-- Company Info -->
            <div class="flex items-start gap-3 mb-4">
              <img
                src={job.company_logo}
                alt="{job.company_name} logo"
                class="w-12 h-12 rounded-xl object-cover bg-gray-100 flex-shrink-0"
                onerror={(e) => {
                  const target = e.target as HTMLImageElement;
                  const initial = job.company_name.charAt(0).toUpperCase();
                  target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23E8F0FE' width='48' height='48' rx='12'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='20' font-weight='600' fill='%231A73E8'%3E${initial}%3C/text%3E%3C/svg%3E`;
                }}
              />
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-gray-900 group-hover:text-primary-600 transition-colors line-clamp-2 leading-snug">
                  {job.title}
                </h3>
                <p class="text-sm text-gray-500 mt-0.5 truncate">{job.company_name}</p>
              </div>
            </div>

            <!-- Job Details -->
            <div class="space-y-2 mb-4">
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <MapPin size={14} class="text-gray-400 flex-shrink-0" />
                <span class="truncate">{job.location_display}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-gray-600">
                <Briefcase size={14} class="text-gray-400 flex-shrink-0" />
                <span class="truncate">{job.experience_display}</span>
              </div>
              {#if job.salary_display}
                <div class="flex items-center gap-2 text-sm text-gray-600">
                  <IndianRupee size={14} class="text-gray-400 flex-shrink-0" />
                  <span class="truncate">{job.salary_display}</span>
                </div>
              {/if}
            </div>

            <!-- Skills -->
            <div class="flex flex-wrap gap-1.5 mb-4">
              {#each job.skills.slice(0, 3) as skill}
                <span class="px-2.5 py-1 bg-primary-50 text-primary-700 text-xs font-medium rounded-lg">{skill.name}</span>
              {/each}
              {#if job.skills.length > 3}
                <span class="px-2.5 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-lg">+{job.skills.length - 3}</span>
              {/if}
            </div>
          </div>

          <!-- Footer -->
          <div class="px-5 py-3 bg-gray-50 border-t border-gray-100 flex items-center justify-between">
            <span class="text-xs text-gray-500">{job.time_ago}</span>
            <span class="text-sm font-medium text-primary-600 flex items-center gap-1 group-hover:gap-2 transition-all">
              View Job
              <ChevronRight size={16} />
            </span>
          </div>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- CTA Section -->
<section class="py-16 lg:py-24 bg-primary-600">
  <div class="max-w-4xl mx-auto px-4 lg:px-8 text-center">
    <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 rounded-full text-white/90 text-sm font-medium mb-6">
      <Star size={16} />
      <span>Join 1M+ professionals</span>
    </div>

    <h2 class="text-3xl lg:text-4xl font-bold text-white tracking-tight mb-6">
      Ready to take the next step in your career?
    </h2>

    <p class="text-lg text-primary-100 mb-10 max-w-2xl mx-auto">
      Create your free profile today and get matched with opportunities that align with your skills and goals.
    </p>

    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a
        href="/register/"
        class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-primary-600 font-semibold rounded-full hover:bg-gray-100 transition-all duration-200 elevation-2"
      >
        <CheckCircle2 size={20} />
        Get Started Free
      </a>
      <a
        href="/jobs/"
        class="inline-flex items-center justify-center px-8 py-4 text-white font-semibold rounded-full border-2 border-white/30 hover:bg-white/10 transition-all duration-200"
      >
        Browse Jobs
      </a>
    </div>
  </div>
</section>
