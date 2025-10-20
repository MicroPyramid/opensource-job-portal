<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { authStore } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { jobsApi } from '$lib/api/jobs';
  import {
    MapPin,
    DollarSign,
    Clock,
    Building,
    Bookmark,
    BookmarkCheck,
    Send,
    Calendar,
    Users,
    Award,
    CheckCircle,
    ArrowLeft,
    Share2,
    ExternalLink,
    Briefcase,
    GraduationCap,
  } from '@lucide/svelte';
  import type { PageData } from './$types';
  import type { JobDetail, Job } from '$lib/types/jobs';

  // Get data from server
  let { data }: { data: PageData } = $props();
  let job: JobDetail = $derived(data.job);
  let relatedJobs: Job[] = $derived(data.relatedJobs || []);

  // Component state - use $derived for SSR compatibility
  let isJobSaved = $derived(job.is_saved);
  let isJobApplied = $derived(job.is_applied);
  let showApplyModal = $state(false);
  let showLoginPrompt = $state(false);
  let isApplying = $state(false);
  let isSaving = $state(false);

  // Check if user is authenticated
  let isAuthenticated = $derived($authStore.isAuthenticated);

  // Handle save/unsave job
  async function handleSaveJob(): Promise<void> {
    if (!isAuthenticated) {
      toast.info('Please login to save jobs');
      return;
    }

    isSaving = true;
    try {
      if (isJobSaved) {
        await jobsApi.unsave(job.id);
        toast.success('Job removed from saved list');
      } else {
        await jobsApi.save(job.id);
        toast.success('Job saved successfully');
      }
      // Reload data from server to update is_saved state (SSR-friendly)
      await invalidateAll();
    } catch (error: any) {
      console.error('Error saving job:', error);
      const errorMessage = error?.message || error?.error || String(error);
      if (errorMessage.includes('already saved')) {
        toast.info('Job is already saved');
        await invalidateAll();
      } else {
        toast.error('Failed to save job. Please try again.');
      }
    } finally {
      isSaving = false;
    }
  }

  // Handle apply for job
  function handleApply(): void {
    if (!isAuthenticated) {
      showLoginPrompt = true;
      return;
    }
    if (isJobApplied) {
      toast.info('You have already applied for this job');
      return;
    }
    showApplyModal = true;
  }

  // Handle share job
  function handleShare(): void {
    if (typeof navigator === 'undefined' || typeof window === 'undefined') {
      return;
    }

    const shareData = {
      title: `${job.title} at ${job.company_name}`,
      text: `Check out this job: ${job.title} at ${job.company_name}`,
      url: window.location.href,
    };

    if (navigator.share) {
      void navigator.share(shareData).catch((err) => {
        if (err.name !== 'AbortError') {
          console.error('Error sharing:', err);
        }
      });
    } else if (navigator.clipboard) {
      void navigator.clipboard.writeText(shareData.url).then(() => {
        toast.success('Link copied to clipboard!');
      });
    }
  }

  // Submit application
  async function submitApplication(): Promise<void> {
    isApplying = true;
    try {
      await jobsApi.apply(job.id);
      toast.success('Application submitted successfully!');
      showApplyModal = false;
      // Reload data from server to update is_applied state (SSR-friendly)
      await invalidateAll();
    } catch (error) {
      console.error('Error submitting application:', error);
      toast.error('Failed to submit application. Please try again.');
    } finally {
      isApplying = false;
    }
  }

  // Navigate back
  function goBack(): void {
    if (typeof window !== 'undefined' && window.history.length > 1) {
      history.back();
    } else {
      goto('/jobs');
    }
  }
</script>

<svelte:head>
  <title>{job.title} at {job.company_name} | PeelJobs</title>
  <meta
    name="description"
    content="{job.title} at {job.company_name} in {job.location_display}. {job.salary_display}, {job.experience_display}. {job.vacancies > 0 ? `${job.vacancies} openings.` : ''} Apply now!"
  />
  <meta
    name="keywords"
    content="{[
      job.title,
      job.company_name,
      ...job.skills.map((s) => s.name),
      ...job.industries.map((i) => i.name),
      ...job.locations.map((l) => l.name),
      job.job_type,
      'jobs'
    ].join(', ')}"
  />

  <!-- Open Graph (Facebook, LinkedIn) -->
  <meta property="og:title" content="{job.title} - {job.company_name}" />
  <meta
    property="og:description"
    content="{job.title} at {job.company_name} in {job.location_display}. {job.salary_display}, {job.experience_display}. Apply now!"
  />
  {#if job.company_logo}
    <meta property="og:image" content="{job.company_logo}" />
  {/if}
  <meta property="og:type" content="website" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{job.title} - {job.company_name}" />
  <meta
    name="twitter:description"
    content="{job.title} at {job.company_name} in {job.location_display}. {job.salary_display}, {job.experience_display}."
  />
  {#if job.company_logo}
    <meta name="twitter:image" content="{job.company_logo}" />
  {/if}

  <!-- JSON-LD Structured Data for Job Posting -->
  {@html `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'JobPosting',
    title: job.title,
    description: job.description || `${job.title} at ${job.company_name}`,
    datePosted: job.published_on,
    validThrough: job.last_date || undefined,
    employmentType: job.job_type.toUpperCase().replace('-', '_'),
    hiringOrganization: {
      '@type': 'Organization',
      name: job.company_name,
      sameAs: job.company_links || undefined,
      logo: job.company_logo || undefined,
    },
    jobLocation: job.locations.map((loc) => ({
      '@type': 'Place',
      address: {
        '@type': 'PostalAddress',
        addressLocality: loc.name,
        addressRegion: loc.state,
        addressCountry: 'IN',
      },
    })),
    baseSalary: job.min_salary > 0 || job.max_salary > 0
      ? {
          '@type': 'MonetaryAmount',
          currency: 'INR',
          value: {
            '@type': 'QuantitativeValue',
            minValue: job.min_salary || undefined,
            maxValue: job.max_salary || undefined,
            unitText: job.salary_type === 'Year' ? 'YEAR' : 'MONTH',
          },
        }
      : undefined,
    qualifications: job.edu_qualification.map((q) => q.name).join(', ') || undefined,
    skills: job.skills.map((s) => s.name).join(', ') || undefined,
    experienceRequirements: {
      '@type': 'OccupationalExperienceRequirements',
      monthsOfExperience: job.min_year * 12 + job.min_month,
    },
    industry: job.industries.map((i) => i.name).join(', ') || undefined,
  })}</script>`}
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header with back button -->
  <div class="bg-white border-b border-gray-200 sticky top-0 z-10">
    <div class="max-w-6xl mx-auto px-4 py-4">
      <button
        onclick={goBack}
        class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft class="w-5 h-5" />
        <span class="hidden sm:inline">Back to Jobs</span>
      </button>
    </div>
  </div>

  <div class="max-w-6xl mx-auto px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Job Header Card -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex flex-col sm:flex-row gap-4">
            {#if job.company_logo}
              <img
                src={job.company_logo}
                alt="{job.company_name} logo"
                class="w-16 h-16 rounded-lg object-cover border border-gray-200"
              />
            {:else}
              <div
                class="w-16 h-16 rounded-lg border border-gray-200 bg-blue-50 flex items-center justify-center"
              >
                <Building class="w-8 h-8 text-blue-600" />
              </div>
            {/if}
            <div class="flex-1">
              <h1 class="text-2xl font-bold text-gray-900 mb-2">{job.title}</h1>
              <div class="flex items-center gap-2 text-lg font-semibold text-blue-600 mb-3">
                <Building class="w-5 h-5" />
                {job.company_name}
              </div>

              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600">
                <div class="flex items-center gap-2">
                  <MapPin class="w-4 h-4 flex-shrink-0" />
                  {job.location_display}
                </div>
                <div class="flex items-center gap-2">
                  <DollarSign class="w-4 h-4 flex-shrink-0" />
                  {job.salary_display}
                </div>
                <div class="flex items-center gap-2">
                  <Clock class="w-4 h-4 flex-shrink-0" />
                  {job.job_type} • {job.experience_display}
                </div>
                <div class="flex items-center gap-2">
                  <Calendar class="w-4 h-4 flex-shrink-0" />
                  Posted {job.time_ago}
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons (Mobile Only - Desktop uses sticky sidebar) -->
          <div class="flex flex-col sm:flex-row gap-3 mt-6 pt-6 border-t border-gray-100 lg:hidden">
            <button
              onclick={handleApply}
              disabled={isJobApplied}
              class="flex-1 px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 {isJobApplied
                ? 'bg-green-50 text-green-700 border border-green-300 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'}"
            >
              {#if isJobApplied}
                <CheckCircle class="w-5 h-5" />
                Applied
              {:else}
                <Send class="w-5 h-5" />
                Apply Now
              {/if}
            </button>
            <button
              onclick={handleSaveJob}
              disabled={isSaving}
              class="px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 {isJobSaved
                ? 'text-blue-600 border-blue-300 bg-blue-50'
                : 'text-gray-700'} disabled:opacity-50"
            >
              {#if isSaving}
                <div class="w-5 h-5 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
              {:else if isJobSaved}
                <BookmarkCheck class="w-5 h-5" />
                Saved
              {:else}
                <Bookmark class="w-5 h-5" />
                Save Job
              {/if}
            </button>
            <button
              onclick={handleShare}
              class="px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 text-gray-700"
            >
              <Share2 class="w-5 h-5" />
              <span class="hidden sm:inline">Share</span>
            </button>
          </div>
        </div>

        <!-- Quick Info Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {#if job.vacancies > 0}
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-blue-50 rounded-lg">
                  <Briefcase class="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <div class="text-sm text-gray-600">Openings</div>
                  <div class="font-semibold text-gray-900">{job.vacancies} positions</div>
                </div>
              </div>
            </div>
          {/if}

          {#if job.applicants_count > 0}
            <div class="bg-white rounded-lg border border-gray-200 p-4">
              <div class="flex items-center gap-3">
                <div class="p-2 bg-green-50 rounded-lg">
                  <Users class="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <div class="text-sm text-gray-600">Applicants</div>
                  <div class="font-semibold text-gray-900">{job.applicants_count} applied</div>
                </div>
              </div>
            </div>
          {/if}
        </div>

        <!-- Skills -->
        {#if job.skills && job.skills.length > 0}
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Required Skills</h2>
            <div class="flex flex-wrap gap-2">
              {#each job.skills as skill}
                <span
                  class="px-3 py-1.5 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium border border-blue-200"
                >
                  {skill.name}
                </span>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Job Description -->
        {#if job.description}
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">Job Description</h2>
            <div class="text-gray-700 leading-relaxed whitespace-pre-line">{job.description}</div>
          </div>
        {/if}

        <!-- Education & Qualifications -->
        {#if job.edu_qualification && job.edu_qualification.length > 0}
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <GraduationCap class="w-6 h-6 text-blue-600" />
              Education Requirements
            </h2>
            <div class="flex flex-wrap gap-2">
              {#each job.edu_qualification as edu}
                <span
                  class="px-3 py-1.5 bg-purple-50 text-purple-700 rounded-lg text-sm font-medium border border-purple-200"
                >
                  {edu.name}
                </span>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Walk-in Details -->
        {#if job.job_type === 'walk-in' && (job.walkin_from_date || job.walkin_time)}
          <div class="bg-amber-50 rounded-xl border border-amber-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">🚶 Walk-in Interview Details</h2>
            <div class="space-y-3 text-gray-700">
              {#if job.walkin_from_date || job.walkin_to_date}
                <div>
                  <strong>Date:</strong>
                  {#if job.walkin_from_date}
                    {new Date(job.walkin_from_date).toLocaleDateString()}
                  {/if}
                  {#if job.walkin_to_date}
                    - {new Date(job.walkin_to_date).toLocaleDateString()}
                  {/if}
                </div>
              {/if}
              {#if job.walkin_time}
                <div><strong>Time:</strong> {job.walkin_time}</div>
              {/if}
              {#if job.company_address}
                <div><strong>Venue:</strong> {job.company_address}</div>
              {/if}
              {#if job.walkin_show_contact_info && job.walkin_contactinfo}
                <div><strong>Contact:</strong> {job.walkin_contactinfo}</div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Government Job Details -->
        {#if job.job_type === 'government'}
          <div class="bg-blue-50 rounded-xl border border-blue-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">🏛️ Government Job Details</h2>
            <div class="space-y-4">
              {#if job.govt_job_type}
                <div>
                  <strong class="text-gray-900">Job Type:</strong>
                  <span class="text-gray-700 ml-2">{job.govt_job_type} Government</span>
                </div>
              {/if}
              {#if job.application_fee > 0}
                <div>
                  <strong class="text-gray-900">Application Fee:</strong>
                  <span class="text-gray-700 ml-2">₹{job.application_fee}</span>
                </div>
              {/if}
              {#if job.govt_from_date || job.govt_to_date}
                <div>
                  <strong class="text-gray-900">Application Period:</strong>
                  <span class="text-gray-700 ml-2">
                    {#if job.govt_from_date}
                      {new Date(job.govt_from_date).toLocaleDateString()}
                    {/if}
                    {#if job.govt_to_date}
                      - {new Date(job.govt_to_date).toLocaleDateString()}
                    {/if}
                  </span>
                </div>
              {/if}
              {#if job.govt_exam_date}
                <div>
                  <strong class="text-gray-900">Exam Date:</strong>
                  <span class="text-gray-700 ml-2">
                    {new Date(job.govt_exam_date).toLocaleDateString()}
                  </span>
                </div>
              {/if}
              {#if job.selection_process}
                <div>
                  <h3 class="font-bold text-gray-900 mb-2">📋 Selection Process</h3>
                  <div class="text-gray-700 whitespace-pre-line">{job.selection_process}</div>
                </div>
              {/if}
              {#if job.how_to_apply}
                <div>
                  <h3 class="font-bold text-gray-900 mb-2">📝 How to Apply</h3>
                  <div class="text-gray-700 whitespace-pre-line">{job.how_to_apply}</div>
                </div>
              {/if}
              {#if job.important_dates}
                <div>
                  <h3 class="font-bold text-gray-900 mb-2">📅 Important Dates</h3>
                  <div class="text-gray-700 whitespace-pre-line">{job.important_dates}</div>
                </div>
              {/if}
              {#if job.age_relaxation}
                <div>
                  <h3 class="font-bold text-gray-900 mb-2">⚖️ Age Relaxation</h3>
                  <div class="text-gray-700 whitespace-pre-line">{job.age_relaxation}</div>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Company Information -->
        {#if job.company}
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h2 class="text-xl font-bold text-gray-900 mb-4">About {job.company.name}</h2>
            {#if job.company_description}
              <p class="text-gray-700 leading-relaxed mb-4 whitespace-pre-line">
                {job.company_description}
              </p>
            {/if}
            {#if job.company_address}
              <div class="mb-3">
                <strong class="text-gray-900">Address:</strong>
                <span class="text-gray-700 ml-2">{job.company_address}</span>
              </div>
            {/if}
            {#if job.company_links}
              <div class="mb-3">
                <strong class="text-gray-900">Website:</strong>
                <a
                  href={job.company_links}
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-blue-600 hover:text-blue-700 ml-2 inline-flex items-center gap-1"
                >
                  {job.company_links}
                  <ExternalLink class="w-4 h-4" />
                </a>
              </div>
            {/if}
            {#if job.company_emails}
              <div>
                <strong class="text-gray-900">Email:</strong>
                <a
                  href="mailto:{job.company_emails}"
                  class="text-blue-600 hover:text-blue-700 ml-2"
                >
                  {job.company_emails}
                </a>
              </div>
            {/if}
          </div>
        {/if}
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Apply Card -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-24">
          <div class="text-center mb-4">
            {#if job.applicants_count > 0}
              <div class="flex items-center justify-center gap-2 text-sm text-gray-600 mb-2">
                <Users class="w-4 h-4" />
                {job.applicants_count} applicants
              </div>
            {/if}
            {#if job.last_date}
              <div class="text-sm text-amber-600 font-medium">
                Apply by: {new Date(job.last_date).toLocaleDateString()}
              </div>
            {/if}
          </div>

          <button
            onclick={handleApply}
            disabled={isJobApplied}
            class="w-full px-6 py-3 rounded-lg font-semibold transition-colors flex items-center justify-center gap-2 mb-3 {isJobApplied
              ? 'bg-green-50 text-green-700 border border-green-300 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'}"
          >
            {#if isJobApplied}
              <CheckCircle class="w-5 h-5" />
              Applied
            {:else}
              <Send class="w-5 h-5" />
              Quick Apply
            {/if}
          </button>

          <button
            onclick={handleSaveJob}
            disabled={isSaving}
            class="w-full px-6 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 {isJobSaved
              ? 'text-blue-600 border-blue-300 bg-blue-50'
              : 'text-gray-700'} disabled:opacity-50"
          >
            {#if isSaving}
              <div class="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin"></div>
            {:else if isJobSaved}
              <BookmarkCheck class="w-4 h-4" />
              Saved
            {:else}
              <Bookmark class="w-4 h-4" />
              Save for Later
            {/if}
          </button>
        </div>

        <!-- Industries -->
        {#if job.industries && job.industries.length > 0}
          <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 class="text-lg font-bold text-gray-900 mb-4">Industries</h3>
            <div class="flex flex-wrap gap-2">
              {#each job.industries as industry}
                <span class="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg text-sm">
                  {industry.name}
                </span>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </div>

    <!-- Related Jobs -->
    {#if relatedJobs.length > 0}
      <div class="mt-12">
        <h2 class="text-2xl font-bold text-gray-900 mb-6">Related Jobs</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {#each relatedJobs as relatedJob}
            <a
              href="/jobs/{relatedJob.slug.replace(/^\/+/, '')}"
              class="block bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              aria-label="View job {relatedJob.title} at {relatedJob.company_name}"
            >
              <div class="flex items-start gap-4 mb-4">
                {#if relatedJob.company_logo}
                  <img
                    src={relatedJob.company_logo}
                    alt="{relatedJob.company_name} logo"
                    class="w-12 h-12 rounded-lg object-cover border border-gray-200"
                  />
                {:else}
                  <div
                    class="w-12 h-12 rounded-lg border border-gray-200 bg-blue-50 flex items-center justify-center"
                  >
                    <Building class="w-6 h-6 text-blue-600" />
                  </div>
                {/if}
                <div class="flex-1 min-w-0">
                  <h3 class="font-semibold text-gray-900 hover:text-blue-600 transition-colors truncate">
                    {relatedJob.title}
                  </h3>
                  <p class="text-gray-600 text-sm truncate">{relatedJob.company_name}</p>
                </div>
              </div>
              <div class="space-y-2 text-sm text-gray-600">
                <div class="flex items-center gap-2">
                  <MapPin class="w-4 h-4 flex-shrink-0" />
                  <span class="truncate">{relatedJob.location_display}</span>
                </div>
                <div class="flex items-center gap-2">
                  <DollarSign class="w-4 h-4 flex-shrink-0" />
                  <span>{relatedJob.salary_display}</span>
                </div>
                <div class="flex items-center gap-2">
                  <Calendar class="w-4 h-4 flex-shrink-0" />
                  <span>Posted {relatedJob.time_ago}</span>
                </div>
              </div>
            </a>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</div>

<!-- Apply Modal -->
{#if showApplyModal}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    onclick={() => (showApplyModal = false)}
    onkeydown={(event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        showApplyModal = false;
      }
    }}
    role="button"
    tabindex="0"
    aria-label="Close apply modal"
  >
    <div
      class="bg-white rounded-xl max-w-md w-full p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Apply for job"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <h3 class="text-xl font-bold text-gray-900 mb-4">Apply for {job.title}</h3>
      <p class="text-gray-600 mb-6">
        Your profile and resume will be sent to {job.company_name} for review.
      </p>

      <div class="flex gap-3">
        <button
          onclick={() => (showApplyModal = false)}
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          disabled={isApplying}
        >
          Cancel
        </button>
        <button
          onclick={submitApplication}
          class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          disabled={isApplying}
        >
          {#if isApplying}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Applying...
          {:else}
            <Send class="w-4 h-4" />
            Confirm Application
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Login Prompt Modal -->
{#if showLoginPrompt}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    onclick={() => (showLoginPrompt = false)}
    onkeydown={(event) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        showLoginPrompt = false;
      }
    }}
    role="button"
    tabindex="0"
    aria-label="Dismiss login prompt"
  >
    <div
      class="bg-white rounded-xl max-w-md w-full p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Login required"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <h3 class="text-xl font-bold text-gray-900 mb-4">Login Required</h3>
      <p class="text-gray-600 mb-6">Please login to apply for this job position.</p>

      <div class="flex gap-3">
        <button
          onclick={() => (showLoginPrompt = false)}
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button
          onclick={() => goto('/login')}
          class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Login
        </button>
      </div>
    </div>
  </div>
{/if}
