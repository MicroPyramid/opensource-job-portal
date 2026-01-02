<script lang="ts">
  import { goto, invalidateAll } from '$app/navigation';
  import { authStore } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { jobsApi } from '$lib/api/jobs';
  import {
    MapPin,
    DollarSign,
    Clock,
    Building2,
    Bookmark,
    BookmarkCheck,
    Send,
    Calendar,
    Users,
    CheckCircle,
    XCircle,
    ArrowLeft,
    Share2,
    ExternalLink,
    Briefcase,
    GraduationCap,
    ChevronRight,
    Sparkles,
    Target,
    FileText,
    Globe,
    Mail,
    CalendarDays,
    Banknote,
    Award,
    Info
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
    if (!job.accepts_applications) {
      toast.error('This job is no longer accepting applications');
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
      goto('/jobs/');
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
    validThrough: job.published_on
      ? new Date(new Date(job.published_on).getTime() + 30*24*60*60*1000).toISOString()
      : undefined,
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

<div class="min-h-screen bg-surface-50">
  <!-- Breadcrumb Navigation -->
  <div class="bg-white border-b border-border">
    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <button
          onclick={goBack}
          class="inline-flex items-center gap-2 text-muted hover:text-primary-600 font-medium transition-colors group"
        >
          <ArrowLeft size={20} class="group-hover:-translate-x-1 transition-transform" />
          <span>Back to Jobs</span>
        </button>

        <!-- Desktop Share Button -->
        <button
          onclick={handleShare}
          class="hidden md:flex items-center gap-2 px-4 py-2 text-muted hover:text-primary-600 hover:bg-primary-50 rounded-full font-medium transition-all"
        >
          <Share2 size={18} />
          <span>Share</span>
        </button>
      </div>
    </div>
  </div>

  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-8">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-5">
        <!-- Job Header Card -->
        <div class="bg-white rounded-lg border border-border overflow-hidden shadow-card">
          <!-- Header with gradient -->
          <div class="bg-[#1D2226] px-6 py-8 relative overflow-hidden">
            <div class="absolute inset-0 overflow-hidden pointer-events-none">
              <div class="absolute -top-12 -right-12 w-64 h-64 bg-primary-600/20 rounded-full blur-3xl"></div>
            </div>

            <div class="flex flex-col sm:flex-row gap-5 relative">
              {#if job.company_logo}
                <img
                  src={job.company_logo}
                  alt="{job.company_name} logo"
                  class="w-16 h-16 rounded-lg object-cover bg-white border-2 border-white/20"
                />
              {:else}
                <div class="w-16 h-16 rounded-lg bg-primary-600/20 flex items-center justify-center border-2 border-white/20">
                  <Building2 size={32} class="text-primary-300" />
                </div>
              {/if}

              <div class="flex-1">
                <h1 class="text-2xl md:text-3xl font-semibold text-white mb-2">{job.title}</h1>
                <a
                  href="/companies/{job.company?.slug || ''}"
                  class="inline-flex items-center gap-2 text-lg font-medium text-primary-300 hover:text-primary-200 transition-colors"
                >
                  <Building2 size={18} />
                  {job.company_name}
                </a>
              </div>
            </div>
          </div>

          <!-- Job Meta -->
          <div class="p-5">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
              <div class="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <div class="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center">
                  <MapPin size={18} class="text-primary-600" />
                </div>
                <div>
                  <p class="text-xs text-muted">Location</p>
                  <p class="text-sm text-black font-medium">{job.location_display}</p>
                </div>
              </div>

              <div class="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <div class="w-9 h-9 rounded-lg bg-success-light flex items-center justify-center">
                  <DollarSign size={18} class="text-success-600" />
                </div>
                <div>
                  <p class="text-xs text-muted">Salary</p>
                  <p class="text-sm text-black font-medium">{job.salary_display}</p>
                </div>
              </div>

              <div class="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <div class="w-9 h-9 rounded-lg bg-warning-light flex items-center justify-center">
                  <Briefcase size={18} class="text-warning-600" />
                </div>
                <div>
                  <p class="text-xs text-muted">Job Type</p>
                  <p class="text-sm text-black font-medium">{job.job_type}</p>
                </div>
              </div>

              <div class="flex items-center gap-3 p-3 bg-surface rounded-lg">
                <div class="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center">
                  <Target size={18} class="text-purple-600" />
                </div>
                <div>
                  <p class="text-xs text-muted">Experience</p>
                  <p class="text-sm text-black font-medium">{job.experience_display}</p>
                </div>
              </div>
            </div>

            <!-- Quick Stats -->
            <div class="flex flex-wrap items-center gap-3 pt-4 border-t border-border">
              <div class="flex items-center gap-1.5 text-sm text-muted">
                <Clock size={14} />
                <span>Posted {job.time_ago}</span>
              </div>
              {#if job.vacancies > 0}
                <span class="w-1 h-1 rounded-full bg-border"></span>
                <div class="flex items-center gap-1.5 text-sm text-muted">
                  <Briefcase size={14} />
                  <span>{job.vacancies} opening{job.vacancies > 1 ? 's' : ''}</span>
                </div>
              {/if}
              {#if job.applicants_count > 0}
                <span class="w-1 h-1 rounded-full bg-border"></span>
                <div class="flex items-center gap-1.5 text-sm text-muted">
                  <Users size={14} />
                  <span>{job.applicants_count} applicant{job.applicants_count > 1 ? 's' : ''}</span>
                </div>
              {/if}
            </div>
          </div>

          <!-- Mobile Action Buttons -->
          <div class="flex gap-3 p-5 pt-0 lg:hidden">
            <button
              onclick={handleApply}
              disabled={isJobApplied || !job.accepts_applications}
              class="flex-1 h-11 px-6 rounded-full font-semibold transition-all flex items-center justify-center gap-2 {isJobApplied
                ? 'bg-success-light text-success-600 border border-success-500/20'
                : !job.accepts_applications
                  ? 'bg-surface text-muted border border-border cursor-not-allowed'
                  : 'bg-primary-600 text-white hover:bg-primary-700'}"
            >
              {#if isJobApplied}
                <CheckCircle size={18} />
                Applied
              {:else if !job.accepts_applications}
                <XCircle size={18} />
                Closed
              {:else}
                <Send size={18} />
                Apply Now
              {/if}
            </button>
            <button
              onclick={handleSaveJob}
              disabled={isSaving}
              class="h-11 px-4 rounded-full border transition-all flex items-center justify-center gap-2 {isJobSaved
                ? 'text-primary-600 border-primary-200 bg-primary-50'
                : 'text-muted border-border hover:border-primary-200 hover:bg-surface'} disabled:opacity-50"
            >
              {#if isSaving}
                <div class="w-4 h-4 border-2 border-muted border-t-transparent rounded-full animate-spin"></div>
              {:else if isJobSaved}
                <BookmarkCheck size={18} />
              {:else}
                <Bookmark size={18} />
              {/if}
            </button>
            <button
              onclick={handleShare}
              class="h-11 px-4 rounded-full border border-border hover:border-primary-200 hover:bg-surface transition-all flex items-center justify-center text-muted"
            >
              <Share2 size={18} />
            </button>
          </div>
        </div>

        <!-- Applications Closed Alert -->
        {#if !job.accepts_applications}
          <div class="bg-warning-light border border-warning-500/20 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <div class="w-9 h-9 rounded-lg bg-warning-500/20 flex items-center justify-center flex-shrink-0">
                <Info size={18} class="text-warning-600" />
              </div>
              <div>
                <h3 class="font-semibold text-black mb-1">Applications Closed</h3>
                <p class="text-sm text-muted">
                  This job posting is no longer accepting new applications.
                </p>
              </div>
            </div>
          </div>
        {/if}

        <!-- Required Skills -->
        {#if job.skills && job.skills.length > 0}
          <div class="bg-white rounded-lg border border-border p-5 shadow-card">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <Sparkles size={18} class="text-primary-600" />
              Required Skills
            </h2>
            <div class="flex flex-wrap gap-2">
              {#each job.skills as skill}
                <span class="px-3 py-1.5 bg-primary-50 text-primary-600 rounded text-sm font-medium">
                  {skill.name}
                </span>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Job Description -->
        {#if job.description}
          <div class="bg-white rounded-lg border border-border p-5 shadow-card">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <FileText size={18} class="text-primary-600" />
              Job Description
            </h2>
            <div class="text-muted leading-relaxed whitespace-pre-line">{job.description}</div>
          </div>
        {/if}

        <!-- Education Requirements -->
        {#if job.edu_qualification && job.edu_qualification.length > 0}
          <div class="bg-white rounded-lg border border-border p-5 shadow-card">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <GraduationCap size={18} class="text-primary-600" />
              Education Requirements
            </h2>
            <div class="flex flex-wrap gap-2">
              {#each job.edu_qualification as edu}
                <span class="px-3 py-1.5 bg-purple-50 text-purple-700 rounded text-sm font-medium">
                  {edu.name}
                </span>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Walk-in Details -->
        {#if job.job_type === 'walk-in' && (job.walkin_from_date || job.walkin_time)}
          <div class="bg-warning-light/50 border border-warning-500/20 rounded-lg p-5">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <CalendarDays size={18} class="text-warning-600" />
              Walk-in Interview Details
            </h2>
            <div class="space-y-3">
              {#if job.walkin_from_date || job.walkin_to_date}
                <div class="flex items-start gap-3">
                  <Calendar size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Date</p>
                    <p class="text-black font-medium">
                      {#if job.walkin_from_date}
                        {new Date(job.walkin_from_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                      {/if}
                      {#if job.walkin_to_date}
                        - {new Date(job.walkin_to_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                      {/if}
                    </p>
                  </div>
                </div>
              {/if}
              {#if job.walkin_time}
                <div class="flex items-start gap-3">
                  <Clock size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Time</p>
                    <p class="text-black font-medium">{job.walkin_time}</p>
                  </div>
                </div>
              {/if}
              {#if job.company_address}
                <div class="flex items-start gap-3">
                  <MapPin size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Venue</p>
                    <p class="text-black font-medium">{job.company_address}</p>
                  </div>
                </div>
              {/if}
              {#if job.walkin_show_contact_info && job.walkin_contactinfo}
                <div class="flex items-start gap-3">
                  <Mail size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Contact</p>
                    <p class="text-black font-medium">{job.walkin_contactinfo}</p>
                  </div>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Government Job Details -->
        {#if job.job_type === 'government'}
          <div class="bg-primary-50/50 border border-primary-200 rounded-lg p-5">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <Award size={18} class="text-primary-600" />
              Government Job Details
            </h2>
            <div class="space-y-3">
              {#if job.govt_job_type}
                <div class="flex items-center gap-3 p-3 bg-white rounded-lg">
                  <Briefcase size={18} class="text-muted" />
                  <div>
                    <p class="text-xs text-muted">Job Type</p>
                    <p class="text-black font-medium">{job.govt_job_type} Government</p>
                  </div>
                </div>
              {/if}
              {#if job.application_fee > 0}
                <div class="flex items-center gap-3 p-3 bg-white rounded-lg">
                  <Banknote size={18} class="text-muted" />
                  <div>
                    <p class="text-xs text-muted">Application Fee</p>
                    <p class="text-black font-medium">₹{job.application_fee}</p>
                  </div>
                </div>
              {/if}
              {#if job.govt_from_date || job.govt_to_date}
                <div class="flex items-center gap-3 p-3 bg-white rounded-lg">
                  <Calendar size={18} class="text-muted" />
                  <div>
                    <p class="text-xs text-muted">Application Period</p>
                    <p class="text-black font-medium">
                      {#if job.govt_from_date}
                        {new Date(job.govt_from_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                      {/if}
                      {#if job.govt_to_date}
                        - {new Date(job.govt_to_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                      {/if}
                    </p>
                  </div>
                </div>
              {/if}
              {#if job.govt_exam_date}
                <div class="flex items-center gap-3 p-3 bg-white rounded-lg">
                  <CalendarDays size={18} class="text-muted" />
                  <div>
                    <p class="text-xs text-muted">Exam Date</p>
                    <p class="text-black font-medium">
                      {new Date(job.govt_exam_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                    </p>
                  </div>
                </div>
              {/if}
              {#if job.selection_process}
                <div class="pt-3 border-t border-primary-200">
                  <h3 class="font-semibold text-black mb-2">Selection Process</h3>
                  <p class="text-muted whitespace-pre-line">{job.selection_process}</p>
                </div>
              {/if}
              {#if job.how_to_apply}
                <div class="pt-3 border-t border-primary-200">
                  <h3 class="font-semibold text-black mb-2">How to Apply</h3>
                  <p class="text-muted whitespace-pre-line">{job.how_to_apply}</p>
                </div>
              {/if}
              {#if job.important_dates}
                <div class="pt-3 border-t border-primary-200">
                  <h3 class="font-semibold text-black mb-2">Important Dates</h3>
                  <p class="text-muted whitespace-pre-line">{job.important_dates}</p>
                </div>
              {/if}
              {#if job.age_relaxation}
                <div class="pt-3 border-t border-primary-200">
                  <h3 class="font-semibold text-black mb-2">Age Relaxation</h3>
                  <p class="text-muted whitespace-pre-line">{job.age_relaxation}</p>
                </div>
              {/if}
            </div>
          </div>
        {/if}

        <!-- Company Information -->
        {#if job.company}
          <div class="bg-white rounded-lg border border-border p-5 shadow-card">
            <h2 class="text-base font-semibold text-black mb-4 flex items-center gap-2">
              <Building2 size={18} class="text-primary-600" />
              About {job.company.name}
            </h2>

            {#if job.company_description}
              <p class="text-muted leading-relaxed mb-5 whitespace-pre-line">
                {job.company_description}
              </p>
            {/if}

            <div class="space-y-3">
              {#if job.company_address}
                <div class="flex items-start gap-3">
                  <MapPin size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Address</p>
                    <p class="text-black">{job.company_address}</p>
                  </div>
                </div>
              {/if}
              {#if job.company_links}
                <div class="flex items-start gap-3">
                  <Globe size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Website</p>
                    <a
                      href={job.company_links}
                      target="_blank"
                      rel="noopener noreferrer"
                      class="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center gap-1"
                    >
                      {job.company_links}
                      <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              {/if}
              {#if job.company_emails}
                <div class="flex items-start gap-3">
                  <Mail size={18} class="text-muted mt-0.5" />
                  <div>
                    <p class="text-xs text-muted">Email</p>
                    <a href="mailto:{job.company_emails}" class="text-primary-600 hover:text-primary-700 font-medium">
                      {job.company_emails}
                    </a>
                  </div>
                </div>
              {/if}
            </div>
          </div>
        {/if}
      </div>

      <!-- Sidebar -->
      <div class="space-y-5">
        <!-- Quick Apply Card (Desktop) -->
        <div class="hidden lg:block bg-white rounded-lg border border-border p-5 shadow-card sticky top-20">
          {#if job.applicants_count > 0}
            <div class="flex items-center justify-center gap-2 text-sm text-muted mb-4 pb-4 border-b border-border">
              <Users size={16} />
              <span>{job.applicants_count} people have applied</span>
            </div>
          {/if}

          <button
            onclick={handleApply}
            disabled={isJobApplied || !job.accepts_applications}
            class="w-full h-11 px-6 rounded-full font-semibold transition-all flex items-center justify-center gap-2 mb-3 {isJobApplied
              ? 'bg-success-light text-success-600 border border-success-500/20'
              : !job.accepts_applications
                ? 'bg-surface text-muted border border-border cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'}"
          >
            {#if isJobApplied}
              <CheckCircle size={18} />
              Applied
            {:else if !job.accepts_applications}
              <XCircle size={18} />
              Applications Closed
            {:else}
              <Send size={18} />
              Quick Apply
            {/if}
          </button>

          <button
            onclick={handleSaveJob}
            disabled={isSaving}
            class="w-full h-10 px-6 rounded-full border transition-all flex items-center justify-center gap-2 {isJobSaved
              ? 'text-primary-600 border-primary-200 bg-primary-50'
              : 'text-muted border-border hover:border-primary-200 hover:bg-surface'} disabled:opacity-50"
          >
            {#if isSaving}
              <div class="w-4 h-4 border-2 border-muted border-t-transparent rounded-full animate-spin"></div>
              Saving...
            {:else if isJobSaved}
              <BookmarkCheck size={16} />
              Saved
            {:else}
              <Bookmark size={16} />
              Save for Later
            {/if}
          </button>

          {#if job.accepts_applications && !isJobApplied}
            <p class="text-xs text-muted text-center mt-4">
              Your profile will be shared with the employer
            </p>
          {/if}
        </div>

        <!-- Industries -->
        {#if job.industries && job.industries.length > 0}
          <div class="bg-white rounded-lg border border-border p-5 shadow-card">
            <h3 class="text-sm font-semibold text-black mb-3">Industries</h3>
            <div class="flex flex-wrap gap-2">
              {#each job.industries as industry}
                <span class="px-3 py-1 bg-surface text-muted rounded text-sm font-medium">
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
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-semibold text-black">Similar Jobs</h2>
          <a
            href="/jobs/"
            class="inline-flex items-center gap-2 text-primary-600 font-semibold hover:text-primary-700 transition-colors group"
          >
            View All Jobs
            <ChevronRight size={18} class="group-hover:translate-x-1 transition-transform" />
          </a>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {#each relatedJobs as relatedJob, index}
            <a
              href="/jobs/{relatedJob.slug.replace(/^\/+/, '')}"
              class="group bg-white rounded-lg border border-border overflow-hidden hover:shadow-card-hover hover:border-primary-200 transition-all"
              aria-label="View job {relatedJob.title} at {relatedJob.company_name}"
              style="animation: fade-in-up 0.4s ease forwards; animation-delay: {index * 50}ms; opacity: 0;"
            >
              <div class="p-4">
                <div class="flex items-start gap-3 mb-3">
                  {#if relatedJob.company_logo}
                    <img
                      src={relatedJob.company_logo}
                      alt="{relatedJob.company_name} logo"
                      class="w-10 h-10 rounded object-cover border border-border"
                    />
                  {:else}
                    <div class="w-10 h-10 rounded bg-primary-50 flex items-center justify-center">
                      <Building2 size={20} class="text-primary-600" />
                    </div>
                  {/if}
                  <div class="flex-1 min-w-0">
                    <h3 class="font-semibold text-black group-hover:text-primary-600 transition-colors line-clamp-2 text-sm">
                      {relatedJob.title}
                    </h3>
                    <p class="text-muted text-sm truncate">{relatedJob.company_name}</p>
                  </div>
                </div>

                <div class="space-y-1.5 text-sm text-muted">
                  <div class="flex items-center gap-2">
                    <MapPin size={14} class="flex-shrink-0" />
                    <span class="truncate">{relatedJob.location_display}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <DollarSign size={14} class="flex-shrink-0" />
                    <span>{relatedJob.salary_display}</span>
                  </div>
                </div>
              </div>

              <div class="px-4 py-2.5 bg-surface border-t border-border flex items-center justify-between">
                <span class="text-xs text-muted flex items-center gap-1">
                  <Clock size={12} />
                  {relatedJob.time_ago}
                </span>
                <span class="text-sm font-semibold text-primary-600 flex items-center gap-1 group-hover:gap-2 transition-all">
                  View
                  <ChevronRight size={14} />
                </span>
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
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in"
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
      class="bg-white rounded-lg max-w-md w-full overflow-hidden shadow-modal animate-scale-in"
      role="dialog"
      aria-modal="true"
      aria-label="Apply for job"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <div class="p-5 border-b border-border">
        <h3 class="text-lg font-semibold text-black">Apply for {job.title}</h3>
        <p class="text-muted mt-1 text-sm">at {job.company_name}</p>
      </div>

      <div class="p-5">
        <div class="flex items-start gap-3 p-4 bg-primary-50 rounded-lg mb-5">
          <Info size={18} class="text-primary-600 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-primary-700">
            Your profile and resume will be sent to the employer for review.
          </p>
        </div>

        <div class="flex gap-3">
          <button
            onclick={() => (showApplyModal = false)}
            class="flex-1 h-10 px-5 border border-border rounded-full text-muted hover:bg-surface transition-colors font-semibold"
            disabled={isApplying}
          >
            Cancel
          </button>
          <button
            onclick={submitApplication}
            class="flex-1 bg-primary-600 text-white h-10 px-5 rounded-full hover:bg-primary-700 transition-colors font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
            disabled={isApplying}
          >
            {#if isApplying}
              <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              Applying...
            {:else}
              <Send size={16} />
              Confirm
            {/if}
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}

<!-- Login Prompt Modal -->
{#if showLoginPrompt}
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fade-in"
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
      class="bg-white rounded-lg max-w-md w-full overflow-hidden shadow-modal animate-scale-in"
      role="dialog"
      aria-modal="true"
      aria-label="Login required"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <div class="p-6 text-center">
        <div class="w-14 h-14 rounded-lg bg-primary-50 flex items-center justify-center mx-auto mb-4">
          <Users size={28} class="text-primary-600" />
        </div>
        <h3 class="text-lg font-semibold text-black mb-2">Login Required</h3>
        <p class="text-muted mb-5">Please login to apply for this job position.</p>

        <div class="flex gap-3">
          <button
            onclick={() => (showLoginPrompt = false)}
            class="flex-1 h-10 px-5 border border-border rounded-full text-muted hover:bg-surface transition-colors font-semibold"
          >
            Cancel
          </button>
          <a
            href="/login/"
            class="flex-1 bg-primary-600 text-white h-10 px-5 rounded-full hover:bg-primary-700 transition-colors font-semibold flex items-center justify-center"
          >
            Login
          </a>
        </div>
      </div>
    </div>
  </div>
{/if}
