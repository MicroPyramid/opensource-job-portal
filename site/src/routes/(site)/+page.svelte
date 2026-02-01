<script lang="ts">
  import {
    Search,
    Briefcase,
    MapPin,
    Brain,
    Shield,
    Clock,
    ChevronRight,
    Building2,
    IndianRupee,
    GraduationCap,
    ArrowRight,
    Home,
    Users,
    Zap,
    TrendingUp,
    CheckCircle2,
    Star,
    BadgeCheck,
    Rocket,
  } from "@lucide/svelte";
  import { goto } from "$app/navigation";
  import Autocomplete from "$lib/components/Autocomplete.svelte";
  import { searchSkills, searchLocations } from "$lib/api/search";
  import type { SkillSuggestion, LocationSuggestion } from "$lib/types/search";
  import type { PageData } from "./$types";
  import { onMount } from "svelte";

  // Server-loaded data
  let { data }: { data: PageData } = $props();

  let jobKeyword = $state("");
  let location = $state("");
  let selectedJobType = $state("full-time");
  let selectedSkill: SkillSuggestion | null = $state(null);
  let selectedLocation: LocationSuggestion | null = $state(null);
  let mounted = $state(false);

  // Autocomplete state
  let skillSuggestions: SkillSuggestion[] = $state([]);
  let locationSuggestions: LocationSuggestion[] = $state([]);
  let loadingSkills = $state(false);
  let loadingLocations = $state(false);

  // Use server-loaded data (derived from props)
  const topCategories = $derived(data.topCategories);
  const topLocations = $derived(data.topLocations);
  const featuredJobs = $derived(data.featuredJobs);

  const jobTypes = [
    { id: "full-time", label: "Full Time", icon: Briefcase },
    { id: "internship", label: "Internship", icon: GraduationCap },
    { id: "remote", label: "Remote", icon: Home },
    { id: "fresher", label: "Fresher", icon: Rocket },
  ];

  onMount(() => {
    mounted = true;
  });

  async function handleSkillSearch(event: CustomEvent<string>) {
    const query = event.detail;
    loadingSkills = true;
    try {
      const response = await searchSkills(query);
      skillSuggestions = response.results;
    } catch (error) {
      console.error("Failed to search skills:", error);
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
      console.error("Failed to search locations:", error);
      locationSuggestions = [];
    } finally {
      loadingLocations = false;
    }
  }

  function handleSkillSelect(event: CustomEvent<{ id: number; name: string }>) {
    selectedSkill = event.detail as SkillSuggestion;
    jobKeyword = event.detail.name;
  }

  function handleLocationSelect(
    event: CustomEvent<{ id: number; name: string }>
  ) {
    selectedLocation = event.detail as LocationSuggestion;
    location = event.detail.name;
  }

  function handleSkillClear() {
    selectedSkill = null;
    jobKeyword = "";
    skillSuggestions = [];
  }

  function handleLocationClear() {
    selectedLocation = null;
    location = "";
    locationSuggestions = [];
  }

  function handleSearch(event: Event) {
    event.preventDefault();
    const params = new URLSearchParams();

    if (selectedSkill?.slug) {
      params.append("skills", selectedSkill.slug);
    } else if (jobKeyword.trim()) {
      params.append("search", jobKeyword.trim());
    }

    if (selectedLocation?.slug) {
      params.append("location", selectedLocation.slug);
    } else if (location.trim()) {
      if (!params.has("search")) {
        params.append("search", location.trim());
      }
    }

    if (selectedJobType) {
      if (selectedJobType === "remote") {
        params.append("is_remote", "true");
      } else if (selectedJobType === "fresher") {
        params.append("fresher", "true");
      } else {
        params.append("job_type", selectedJobType);
      }
    }

    const queryString = params.toString();
    goto(`/jobs/${queryString ? "?" + queryString : ""}`);
  }

  function selectJobType(typeId: string) {
    selectedJobType = typeId;
  }

  // Stats for social proof
  const stats = [
    { value: "50K+", label: "Active Jobs", icon: Briefcase },
    { value: "10K+", label: "Companies", icon: Building2 },
    { value: "1M+", label: "Job Seekers", icon: Users },
    { value: "95%", label: "Success Rate", icon: TrendingUp },
  ];
</script>

<svelte:head>
  <title>PeelJobs - Find Your Dream Job | India's Smart Job Platform</title>
  <meta
    name="description"
    content="Discover thousands of job opportunities across India. PeelJobs connects talented professionals with top companies using intelligent job matching."
  />
</svelte:head>

<!-- Hero Section -->
<section class="relative bg-white border-b border-border">
  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-12 lg:py-20">
    <div class="grid lg:grid-cols-2 gap-12 items-center">
      <!-- Left Column - Content -->
      <div class="max-w-xl">
        <!-- Badge -->
        <div
          class="inline-flex items-center gap-2 px-3 py-1.5 bg-primary-50 text-primary-600 rounded-full text-sm font-medium mb-6 hero-fade-in"
          style="--delay: 0ms;"
        >
          <span class="relative flex h-2 w-2">
            <span
              class="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary-500 opacity-75"
            ></span>
            <span
              class="relative inline-flex rounded-full h-2 w-2 bg-primary-500"
            ></span>
          </span>
          <span>50,000+ Jobs Available</span>
        </div>

        <!-- Headline -->
        <h1 class="mb-6">
          <span
            class="block text-3xl md:text-4xl lg:text-5xl font-semibold text-black tracking-tight leading-tight hero-fade-in"
            style="--delay: 100ms;"
          >
            Find your next
          </span>
          <span
            class="block text-3xl md:text-4xl lg:text-5xl font-semibold text-primary-600 tracking-tight leading-tight hero-fade-in"
            style="--delay: 150ms;"
          >
            career opportunity
          </span>
        </h1>

        <!-- Subheadline -->
        <p
          class="text-lg text-muted leading-relaxed mb-8 hero-fade-in"
          style="--delay: 200ms;"
        >
          Join over <span class="font-semibold text-black"
            >1 million professionals</span
          > who use PeelJobs to discover verified opportunities at India's top companies.
        </p>

        <!-- Trust Badges -->
        <div
          class="flex flex-wrap gap-4 mb-8 hero-fade-in"
          style="--delay: 250ms;"
        >
          <div class="flex items-center gap-2 text-sm text-muted">
            <BadgeCheck size={18} class="text-success-500" />
            <span>Verified Jobs</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-muted">
            <Shield size={18} class="text-primary-600" />
            <span>Safe & Secure</span>
          </div>
          <div class="flex items-center gap-2 text-sm text-muted">
            <Zap size={18} class="text-warning-500" />
            <span>Quick Apply</span>
          </div>
        </div>

        <!-- Stats -->
        <div
          class="grid grid-cols-4 gap-6 hero-fade-in"
          style="--delay: 300ms;"
        >
          {#each stats as stat}
            <div>
              <div class="text-2xl font-semibold text-black">{stat.value}</div>
              <div class="text-xs text-muted">{stat.label}</div>
            </div>
          {/each}
        </div>
      </div>

      <!-- Right Column - Search Card -->
      <div class="hero-fade-in" style="--delay: 200ms;">
        <form
          onsubmit={handleSearch}
          class="bg-white rounded-lg border border-border p-6 shadow-card"
        >
          <!-- Card Header -->
          <div class="flex items-center gap-3 mb-6">
            <div
              class="w-10 h-10 rounded-lg bg-primary-600 flex items-center justify-center"
            >
              <Search size={20} class="text-white" />
            </div>
            <div>
              <h2 class="text-lg font-semibold text-black">Search Jobs</h2>
              <p class="text-sm text-muted">Find your perfect match</p>
            </div>
          </div>

          <!-- Search Fields -->
          <div class="space-y-4 mb-6">
            <!-- Skills/Job Input -->
            <div>
              <label
                for="job-search"
                class="block text-sm font-medium text-black mb-2"
                >Job title or skill</label
              >
              <Autocomplete
                id="job-search"
                placeholder="e.g. Python Developer, React, Sales"
                bind:value={jobKeyword}
                icon={Briefcase}
                suggestions={skillSuggestions}
                loading={loadingSkills}
                showJobCount={true}
                inputClass="!rounded-lg !border-border focus:!border-primary-600"
                on:search={handleSkillSearch}
                on:select={handleSkillSelect}
                on:clear={handleSkillClear}
              />
            </div>

            <!-- Location Input -->
            <div>
              <label
                for="location-search"
                class="block text-sm font-medium text-black mb-2"
                >Location</label
              >
              <Autocomplete
                id="location-search"
                placeholder="e.g. Bangalore, Mumbai, Remote"
                bind:value={location}
                icon={MapPin}
                suggestions={locationSuggestions}
                loading={loadingLocations}
                showJobCount={true}
                inputClass="!rounded-lg !border-border focus:!border-primary-600"
                on:search={handleLocationSearch}
                on:select={handleLocationSelect}
                on:clear={handleLocationClear}
              />
            </div>
          </div>

          <!-- Job Type Pills -->
          <div class="mb-6">
            <!-- svelte-ignore a11y_label_has_associated_control -->
            <label class="block text-sm font-medium text-black mb-3"
              >Job type</label
            >
            <div class="flex flex-wrap gap-2">
              {#each jobTypes as jobType}
                {@const Icon = jobType.icon}
                <button
                  type="button"
                  onclick={() => selectJobType(jobType.id)}
                  class="flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all {selectedJobType ===
                  jobType.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-surface border border-border text-muted hover:border-primary-600 hover:text-primary-600'}"
                >
                  <Icon size={16} />
                  <span>{jobType.label}</span>
                </button>
              {/each}
            </div>
          </div>

          <!-- Search Button -->
          <button
            type="submit"
            class="w-full h-12 flex items-center justify-center gap-2 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-full transition-colors"
          >
            <Search size={20} />
            <span>Search Jobs</span>
          </button>

          <!-- Popular Searches -->
          <div class="mt-5 pt-5 border-t border-border">
            <p class="text-xs text-muted mb-2">Popular:</p>
            <div class="flex flex-wrap gap-2">
              {#each ["Python Developer", "React", "Bangalore", "Remote", "Fresher"] as term}
                <a
                  href="/jobs/?search={encodeURIComponent(term)}"
                  class="px-3 py-1 bg-surface text-muted hover:text-primary-600 hover:bg-primary-50 rounded-full text-xs font-medium transition-colors"
                >
                  {term}
                </a>
              {/each}
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</section>

<!-- Browse by Category -->
<section class="py-16 bg-surface-50">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div
      class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8"
    >
      <div>
        <h2 class="text-2xl font-semibold text-black">Browse by category</h2>
        <p class="text-muted mt-1">Explore opportunities in your industry</p>
      </div>
      <a
        href="/jobs/"
        class="inline-flex items-center gap-1 text-primary-600 font-semibold hover:text-primary-700 hover:underline transition-colors"
      >
        View all jobs
        <ArrowRight size={16} />
      </a>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {#each topCategories as category, i}
        <a
          href="/jobs/?industry={category.slug}"
          class="group bg-white rounded-lg border border-border p-4 hover:shadow-md hover:border-primary-200 transition-all"
          style="animation: fade-in-up 0.4s ease forwards; animation-delay: {i *
            30}ms; opacity: 0;"
        >
          <div
            class="w-10 h-10 rounded-lg bg-primary-50 flex items-center justify-center mb-3 group-hover:bg-primary-100 transition-colors"
          >
            <Building2 size={20} class="text-primary-600" />
          </div>
          <h3
            class="font-medium text-black group-hover:text-primary-600 transition-colors line-clamp-2 text-sm"
          >
            {category.name}
          </h3>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- Browse by Location -->
<section class="py-16 bg-white">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div
      class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8"
    >
      <div>
        <h2 class="text-2xl font-semibold text-black">Jobs by location</h2>
        <p class="text-muted mt-1">Find opportunities in your city</p>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
      {#each topLocations as loc, i}
        <a
          href="/jobs/?location={loc.slug}"
          class="group flex items-center gap-3 bg-surface-50 rounded-lg p-4 hover:bg-primary-50 border border-transparent hover:border-primary-200 transition-all"
          style="animation: fade-in-up 0.4s ease forwards; animation-delay: {i *
            30}ms; opacity: 0;"
        >
          <div
            class="w-9 h-9 rounded-lg bg-white flex items-center justify-center shadow-sm group-hover:bg-primary-100 transition-colors"
          >
            <MapPin size={16} class="text-primary-600" />
          </div>
          <span
            class="font-medium text-black group-hover:text-primary-600 transition-colors text-sm"
            >{loc.name}</span
          >
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- Why Choose PeelJobs -->
<section class="py-16 bg-[#1D2226]">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div class="text-center mb-12">
      <h2 class="text-2xl lg:text-3xl font-semibold text-white mb-3">
        Why choose PeelJobs?
      </h2>
      <p class="text-gray-400 max-w-xl mx-auto">
        Built for job seekers who want results, not hassles.
      </p>
    </div>

    <div class="grid md:grid-cols-3 gap-6">
      <!-- Feature 1 -->
      <div class="bg-white/5 rounded-lg p-6 border border-white/10">
        <div
          class="w-12 h-12 rounded-lg bg-primary-600/20 flex items-center justify-center mb-4"
        >
          <Brain size={24} class="text-primary-400" />
        </div>
        <h3 class="text-lg font-semibold text-white mb-2">Smart Matching</h3>
        <p class="text-gray-400 text-sm leading-relaxed">
          Our algorithms analyze your profile to show jobs that match your
          skills and experience.
        </p>
      </div>

      <!-- Feature 2 -->
      <div class="bg-white/5 rounded-lg p-6 border border-white/10">
        <div
          class="w-12 h-12 rounded-lg bg-success-500/20 flex items-center justify-center mb-4"
        >
          <Shield size={24} class="text-success-500" />
        </div>
        <h3 class="text-lg font-semibold text-white mb-2">
          Verified Companies
        </h3>
        <p class="text-gray-400 text-sm leading-relaxed">
          Every employer is vetted to ensure you're applying to legitimate
          opportunities.
        </p>
      </div>

      <!-- Feature 3 -->
      <div class="bg-white/5 rounded-lg p-6 border border-white/10">
        <div
          class="w-12 h-12 rounded-lg bg-warning-500/20 flex items-center justify-center mb-4"
        >
          <Zap size={24} class="text-warning-500" />
        </div>
        <h3 class="text-lg font-semibold text-white mb-2">Quick Apply</h3>
        <p class="text-gray-400 text-sm leading-relaxed">
          Apply to multiple jobs in minutes with our streamlined one-click
          application.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Featured Jobs -->
<section class="py-16 bg-surface-50">
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <div
      class="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8"
    >
      <div>
        <div
          class="inline-flex items-center gap-2 px-3 py-1 bg-success-light text-success-600 rounded-full text-sm font-medium mb-2"
        >
          <TrendingUp size={14} />
          <span>Latest Openings</span>
        </div>
        <h2 class="text-2xl font-semibold text-black">Featured jobs</h2>
        <p class="text-muted mt-1">Fresh opportunities from top companies</p>
      </div>
      <a
        href="/jobs/"
        class="inline-flex items-center gap-2 h-10 px-5 bg-primary-600 text-white font-semibold rounded-full hover:bg-primary-700 transition-colors"
      >
        View all jobs
        <ArrowRight size={16} />
      </a>
    </div>

    <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-4">
      {#each featuredJobs as job, i (job.id)}
        <a
          href={job.slug}
          class="group bg-white rounded-lg border border-border overflow-hidden hover:shadow-md hover:border-primary-200 transition-all"
          style="animation: fade-in-up 0.4s ease forwards; animation-delay: {i *
            50}ms; opacity: 0;"
        >
          <div class="p-4">
            <!-- Company Info -->
            <div class="flex items-start gap-3 mb-3">
              <img
                src={job.company_logo}
                alt="{job.company_name} logo"
                class="w-12 h-12 rounded object-cover bg-surface flex-shrink-0"
                onerror={(e) => {
                  const target = e.target as HTMLImageElement;
                  const initial = job.company_name.charAt(0).toUpperCase();
                  target.src = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='48' height='48'%3E%3Crect fill='%23E8F4FC' width='48' height='48' rx='4'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='system-ui' font-size='20' font-weight='600' fill='%230A66C2'%3E${initial}%3C/text%3E%3C/svg%3E`;
                }}
              />
              <div class="flex-1 min-w-0">
                <h3
                  class="font-semibold text-black group-hover:text-primary-600 transition-colors line-clamp-2 text-sm leading-snug"
                >
                  {job.title}
                </h3>
                <p class="text-sm text-muted mt-0.5 truncate">
                  {job.company_name}
                </p>
              </div>
            </div>

            <!-- Job Details -->
            <div class="space-y-1.5 mb-3">
              <div class="flex items-center gap-2 text-sm text-muted">
                <MapPin size={14} class="flex-shrink-0" />
                <span class="truncate">{job.location_display}</span>
              </div>
              <div class="flex items-center gap-2 text-sm text-muted">
                <Briefcase size={14} class="flex-shrink-0" />
                <span class="truncate">{job.experience_display}</span>
              </div>
              {#if job.salary_display}
                <div class="flex items-center gap-2 text-sm text-muted">
                  <IndianRupee size={14} class="flex-shrink-0" />
                  <span class="truncate">{job.salary_display}</span>
                </div>
              {/if}
            </div>

            <!-- Skills -->
            <div class="flex flex-wrap gap-1.5">
              {#each job.skills.slice(0, 3) as skill}
                <span
                  class="px-2 py-0.5 bg-primary-50 text-primary-600 text-xs font-medium rounded"
                  >{skill.name}</span
                >
              {/each}
              {#if job.skills.length > 3}
                <span
                  class="px-2 py-0.5 bg-surface text-muted text-xs font-medium rounded"
                  >+{job.skills.length - 3}</span
                >
              {/if}
            </div>
          </div>

          <!-- Footer -->
          <div
            class="px-4 py-3 bg-surface-50 border-t border-border flex items-center justify-between"
          >
            <span class="text-xs text-muted">{job.time_ago}</span>
            <span
              class="text-sm font-semibold text-primary-600 flex items-center gap-1 group-hover:gap-2 transition-all"
            >
              View
              <ChevronRight size={14} />
            </span>
          </div>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- CTA Section -->
<section class="py-16 bg-primary-600">
  <div class="max-w-3xl mx-auto px-4 lg:px-8 text-center">
    <div
      class="inline-flex items-center gap-2 px-3 py-1 bg-white/10 rounded-full text-white/90 text-sm font-medium mb-6"
    >
      <Star size={14} />
      <span>Join 1M+ professionals</span>
    </div>

    <h2 class="text-2xl lg:text-3xl font-semibold text-white mb-4">
      Ready to take the next step?
    </h2>

    <p class="text-primary-100 mb-8 max-w-lg mx-auto">
      Create your free profile and get matched with opportunities that align
      with your skills and goals.
    </p>

    <div class="flex flex-col sm:flex-row gap-3 justify-center">
      <a
        href="/register/"
        class="inline-flex items-center justify-center gap-2 h-12 px-8 bg-white text-primary-600 font-semibold rounded-full hover:bg-gray-50 transition-colors"
      >
        <CheckCircle2 size={18} />
        Get started free
      </a>
      <a
        href="/jobs/"
        class="inline-flex items-center justify-center h-12 px-8 text-white font-semibold rounded-full border border-white/30 hover:bg-white/10 transition-colors"
      >
        Browse jobs
      </a>
    </div>
  </div>
</section>

<style>
  .hero-fade-in {
    opacity: 0;
    transform: translateY(16px);
    animation: heroFadeIn 0.6s ease-out forwards;
    animation-delay: var(--delay, 0ms);
  }

  @keyframes heroFadeIn {
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
