<script lang="ts">
  import {
    MapPin,
    Users,
    Calendar,
    Briefcase,
    Heart,
    ExternalLink,
    Globe,
    Mail,
    Phone,
    Building2,
    TrendingUp,
    Award,
    CheckCircle,
    ChevronRight,
    ArrowLeft,
    Share2,
    Factory,
    Clock,
    DollarSign,
    Target,
    FileText,
    Sparkles
  } from '@lucide/svelte';
  import { goto } from '$app/navigation';
  import { toast } from '$lib/stores/toast';
  import type { PageData } from './$types';

  let { data }: { data: PageData } = $props();
  const company = $derived(data.company);
  const jobs = $derived(data.jobs || []);

  let isFollowing = $state(false);

  function toggleFollow() {
    isFollowing = !isFollowing;
    if (isFollowing) {
      toast.success('Following ' + company.name);
    } else {
      toast.info('Unfollowed ' + company.name);
    }
    // TODO: Implement API call to follow/unfollow company
  }

  function goBack(): void {
    if (typeof window !== 'undefined' && window.history.length > 1) {
      history.back();
    } else {
      goto('/companies/');
    }
  }

  function handleShare(): void {
    if (typeof navigator === 'undefined' || typeof window === 'undefined') {
      return;
    }

    const shareData = {
      title: `${company.name} - Company Profile`,
      text: `Check out ${company.name} on PeelJobs`,
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

  // Company stats
  const stats = $derived([
    { label: 'Open Positions', value: jobs.length.toString(), icon: Briefcase },
    { label: 'Company Type', value: company.company_type || 'N/A', icon: Building2 },
    { label: 'Company Size', value: company.size || 'N/A', icon: Users },
    { label: 'Industry', value: company.industry?.name || 'N/A', icon: Factory }
  ]);
</script>

<svelte:head>
  <title>{company.name} - Company Profile | PeelJobs</title>
  <meta name="description" content="{company.profile || `Explore ${company.name} and discover job opportunities. View company profile, open positions, and more on PeelJobs.`}" />

  <!-- Open Graph -->
  <meta property="og:title" content="{company.name} - Company Profile" />
  <meta property="og:description" content="{company.profile || `Explore ${company.name} and discover job opportunities.`}" />
  {#if company.logo}
    <meta property="og:image" content="{company.logo}" />
  {/if}
  <meta property="og:type" content="website" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="{company.name} - Company Profile" />
  <meta name="twitter:description" content="{company.profile || `Explore ${company.name} and discover job opportunities.`}" />
  {#if company.logo}
    <meta name="twitter:image" content="{company.logo}" />
  {/if}

  <!-- JSON-LD Structured Data -->
  {@html `<script type="application/ld+json">${JSON.stringify({
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: company.name,
    description: company.profile,
    url: company.website || undefined,
    logo: company.logo || undefined,
    address: company.address ? {
      '@type': 'PostalAddress',
      streetAddress: company.address
    } : undefined,
    email: company.email || undefined,
    telephone: company.phone || undefined,
    industry: company.industry?.name || undefined,
    numberOfEmployees: company.size ? {
      '@type': 'QuantitativeValue',
      value: company.size
    } : undefined
  })}</script>`}
</svelte:head>

<div class="min-h-screen bg-surface-50">
  <!-- Breadcrumb Navigation -->
  <div class="bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-4">
      <div class="flex items-center justify-between">
        <button
          onclick={goBack}
          class="inline-flex items-center gap-2 text-gray-600 hover:text-primary-600 font-medium transition-colors group"
        >
          <ArrowLeft class="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
          <span>Back to Companies</span>
        </button>

        <!-- Desktop Share Button -->
        <button
          onclick={handleShare}
          class="hidden md:flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-full font-medium transition-all"
        >
          <Share2 class="w-5 h-5" />
          <span>Share</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Company Header -->
  <section class="bg-gray-900 relative overflow-hidden">
    <!-- Decorative Elements -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-24 -right-24 w-96 h-96 bg-primary-500/20 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-24 -left-24 w-96 h-96 bg-primary-600/10 rounded-full blur-3xl"></div>
    </div>

    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-12 lg:py-16 relative">
      <div class="flex flex-col md:flex-row gap-6 items-start md:items-center">
        <!-- Company Logo -->
        {#if company.logo}
          <div class="w-24 h-24 lg:w-28 lg:h-28 bg-white rounded-2xl p-3 elevation-2 flex items-center justify-center animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
            <img src={company.logo} alt="{company.name} logo" class="w-full h-full object-contain" />
          </div>
        {:else}
          <div class="w-24 h-24 lg:w-28 lg:h-28 bg-primary-500/20 rounded-2xl flex items-center justify-center border-2 border-white/20 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
            <Building2 class="w-12 h-12 text-primary-300" />
          </div>
        {/if}

        <!-- Company Info -->
        <div class="flex-1 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms;">
          <div class="flex items-start justify-between flex-wrap gap-4">
            <div>
              <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-white tracking-tight mb-3">
                {company.name}
              </h1>

              <div class="flex flex-wrap gap-3 text-sm md:text-base">
                {#if company.industry?.name}
                  <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-primary-200">
                    <Factory class="w-4 h-4" />
                    <span>{company.industry.name}</span>
                  </div>
                {/if}
                {#if company.company_type}
                  <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-gray-300">
                    <Building2 class="w-4 h-4" />
                    <span>{company.company_type}</span>
                  </div>
                {/if}
                {#if company.address}
                  <div class="flex items-center gap-2 px-3 py-1.5 bg-white/10 rounded-full text-gray-300">
                    <MapPin class="w-4 h-4" />
                    <span class="line-clamp-1">{company.address}</span>
                  </div>
                {/if}
              </div>
            </div>

            <!-- Action Buttons -->
            <div class="flex gap-3 animate-fade-in-up" style="opacity: 0; animation-delay: 300ms;">
              <button
                onclick={toggleFollow}
                class="flex items-center gap-2 px-6 py-3 rounded-full font-medium transition-all duration-200 elevation-1 hover:elevation-2 {isFollowing
                  ? 'bg-white text-primary-600'
                  : 'bg-primary-600 text-white hover:bg-primary-700'}"
              >
                <Heart class="w-5 h-5 {isFollowing ? 'fill-current' : ''}" />
                {isFollowing ? 'Following' : 'Follow'}
              </button>
              <button
                onclick={handleShare}
                class="md:hidden flex items-center justify-center w-12 h-12 rounded-full bg-white/10 text-white hover:bg-white/20 transition-all"
              >
                <Share2 class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Company Stats -->
  <section class="py-6 bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4 lg:px-8">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-6">
        {#each stats as stat, index}
          <div
            class="text-center p-4 animate-fade-in-up"
            style="opacity: 0; animation-delay: {100 + index * 50}ms;"
          >
            <div class="flex justify-center mb-3">
              <div class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                <stat.icon class="w-6 h-6 text-primary-600" />
              </div>
            </div>
            <div class="text-xl lg:text-2xl font-bold text-gray-900 mb-1">{stat.value}</div>
            <div class="text-sm text-gray-500">{stat.label}</div>
          </div>
        {/each}
      </div>
    </div>
  </section>

  <!-- Main Content -->
  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
    <div class="grid lg:grid-cols-3 gap-8">
      <!-- Left Column - Company Details -->
      <div class="lg:col-span-2 space-y-6">
        <!-- About Company -->
        {#if company.profile}
          <div
            class="bg-white rounded-2xl elevation-1 border border-gray-100 p-6 animate-fade-in-up"
            style="opacity: 0; animation-delay: 100ms;"
          >
            <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <FileText class="w-5 h-5 text-primary-600" />
              About {company.name}
            </h2>
            <p class="text-gray-700 leading-relaxed whitespace-pre-line">
              {company.profile}
            </p>
          </div>
        {/if}

        <!-- Nature of Business -->
        {#if company.nature_of_business && company.nature_of_business.length > 0}
          <div
            class="bg-white rounded-2xl elevation-1 border border-gray-100 p-6 animate-fade-in-up"
            style="opacity: 0; animation-delay: 150ms;"
          >
            <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Target class="w-5 h-5 text-primary-600" />
              Nature of Business
            </h2>
            <div class="flex flex-wrap gap-2">
              {#each company.nature_of_business as business}
                <span class="px-4 py-2 bg-primary-50 text-primary-700 rounded-full text-sm font-medium border border-primary-100">
                  {business}
                </span>
              {/each}
            </div>
          </div>
        {/if}

        <!-- Open Positions -->
        <div
          class="bg-white rounded-2xl elevation-1 border border-gray-100 p-6 animate-fade-in-up"
          style="opacity: 0; animation-delay: 200ms;"
        >
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
              <Sparkles class="w-5 h-5 text-primary-600" />
              Open Positions
            </h2>
            {#if jobs.length > 0}
              <span class="px-3 py-1 bg-primary-50 text-primary-700 text-sm font-medium rounded-full">
                {jobs.length} {jobs.length === 1 ? 'Job' : 'Jobs'}
              </span>
            {/if}
          </div>

          {#if jobs.length > 0}
            <div class="space-y-4">
              {#each jobs as job, index}
                <a
                  href="/jobs/{job.slug.replace(/^\/+/, '')}/"
                  class="group block p-5 border border-gray-100 rounded-xl hover:border-primary-200 hover:elevation-2 transition-all duration-200"
                  style="animation: fade-in-up 0.5s ease forwards; animation-delay: {250 + index * 50}ms; opacity: 0;"
                >
                  <div class="flex items-start justify-between mb-3">
                    <div class="flex-1">
                      <h3 class="text-base lg:text-lg font-semibold text-gray-900 mb-1 group-hover:text-primary-600 transition-colors">
                        {job.title}
                      </h3>
                      <div class="flex flex-wrap items-center gap-2 text-sm text-gray-500">
                        <span class="flex items-center gap-1">
                          <MapPin class="w-4 h-4" />
                          {job.location_display}
                        </span>
                        <span class="flex items-center gap-1">
                          <Briefcase class="w-4 h-4" />
                          {job.job_type}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div class="flex flex-wrap items-center gap-2 mb-3">
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-success-500/10 text-success-600 rounded-full text-xs font-medium">
                      <DollarSign class="w-3.5 h-3.5" />
                      {job.salary_display}
                    </span>
                    <span class="inline-flex items-center gap-1.5 px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">
                      <Target class="w-3.5 h-3.5" />
                      {job.experience_display}
                    </span>
                  </div>

                  <div class="flex items-center justify-between text-sm">
                    <span class="text-gray-400 flex items-center gap-1">
                      <Clock class="w-4 h-4" />
                      {job.time_ago}
                    </span>
                    <span class="text-primary-600 font-medium flex items-center gap-1 group-hover:gap-2 transition-all">
                      View Job
                      <ChevronRight class="w-4 h-4" />
                    </span>
                  </div>
                </a>
              {/each}
            </div>

            {#if jobs.length >= 10}
              <div class="mt-6 text-center">
                <a
                  href="/jobs/?company={company.slug}"
                  class="inline-flex items-center gap-2 px-6 py-3 bg-primary-50 text-primary-700 font-medium rounded-full hover:bg-primary-100 transition-colors"
                >
                  View All Open Positions
                  <ChevronRight class="w-5 h-5" />
                </a>
              </div>
            {/if}
          {:else}
            <div class="text-center py-12">
              <div class="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mx-auto mb-4">
                <Briefcase class="w-8 h-8 text-gray-400" />
              </div>
              <h3 class="text-lg font-semibold text-gray-900 mb-2">No Open Positions</h3>
              <p class="text-gray-600">
                This company doesn't have any open positions at the moment.
              </p>
            </div>
          {/if}
        </div>
      </div>

      <!-- Right Column - Sidebar -->
      <div class="lg:col-span-1">
        <div class="lg:sticky lg:top-24 space-y-6">
          <!-- Company Info Card -->
          <div
            class="bg-white rounded-2xl elevation-1 border border-gray-100 p-6 animate-fade-in-up"
            style="opacity: 0; animation-delay: 150ms;"
          >
            <h3 class="text-base font-semibold text-gray-900 mb-4">Company Information</h3>

            <div class="space-y-4">
              {#if company.industry?.name}
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center flex-shrink-0">
                    <Factory class="w-5 h-5 text-primary-600" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 font-medium mb-0.5">Industry</p>
                    <p class="text-sm text-gray-900 font-medium">{company.industry.name}</p>
                  </div>
                </div>
              {/if}

              {#if company.company_type}
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center flex-shrink-0">
                    <Building2 class="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 font-medium mb-0.5">Company Type</p>
                    <p class="text-sm text-gray-900 font-medium">{company.company_type}</p>
                  </div>
                </div>
              {/if}

              {#if company.size}
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center flex-shrink-0">
                    <Users class="w-5 h-5 text-purple-600" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 font-medium mb-0.5">Company Size</p>
                    <p class="text-sm text-gray-900 font-medium">{company.size} employees</p>
                  </div>
                </div>
              {/if}

              {#if company.address}
                <div class="flex items-start gap-3">
                  <div class="w-10 h-10 rounded-xl bg-warning-500/10 flex items-center justify-center flex-shrink-0">
                    <MapPin class="w-5 h-5 text-warning-600" />
                  </div>
                  <div>
                    <p class="text-xs text-gray-500 font-medium mb-0.5">Location</p>
                    <p class="text-sm text-gray-900">{company.address}</p>
                  </div>
                </div>
              {/if}
            </div>
          </div>

          <!-- Contact Card -->
          {#if company.website || company.email || company.phone}
            <div
              class="bg-white rounded-2xl elevation-1 border border-gray-100 p-6 animate-fade-in-up"
              style="opacity: 0; animation-delay: 200ms;"
            >
              <h3 class="text-base font-semibold text-gray-900 mb-4">Contact</h3>

              <div class="space-y-3">
                {#if company.website}
                  <a
                    href={company.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    class="flex items-center gap-3 p-3 rounded-xl bg-surface-50 hover:bg-primary-50 text-gray-700 hover:text-primary-600 transition-colors group"
                  >
                    <Globe class="w-5 h-5" />
                    <span class="text-sm font-medium flex-1 truncate">Visit Website</span>
                    <ExternalLink class="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </a>
                {/if}

                {#if company.email}
                  <a
                    href="mailto:{company.email}"
                    class="flex items-center gap-3 p-3 rounded-xl bg-surface-50 hover:bg-primary-50 text-gray-700 hover:text-primary-600 transition-colors"
                  >
                    <Mail class="w-5 h-5" />
                    <span class="text-sm truncate">{company.email}</span>
                  </a>
                {/if}

                {#if company.phone}
                  <a
                    href="tel:{company.phone}"
                    class="flex items-center gap-3 p-3 rounded-xl bg-surface-50 hover:bg-primary-50 text-gray-700 hover:text-primary-600 transition-colors"
                  >
                    <Phone class="w-5 h-5" />
                    <span class="text-sm">{company.phone}</span>
                  </a>
                {/if}
              </div>
            </div>
          {/if}

          <!-- Call to Action -->
          {#if jobs.length > 0}
            <div
              class="bg-gray-900 rounded-2xl elevation-2 p-6 relative overflow-hidden animate-fade-in-up"
              style="opacity: 0; animation-delay: 250ms;"
            >
              <div class="absolute inset-0 overflow-hidden pointer-events-none">
                <div class="absolute -top-12 -right-12 w-48 h-48 bg-primary-500/20 rounded-full blur-3xl"></div>
              </div>

              <div class="relative">
                <h3 class="text-lg font-bold text-white mb-2">Interested in joining?</h3>
                <p class="text-sm text-gray-400 mb-5">
                  Explore open positions and find your perfect role at {company.name}.
                </p>
                <a
                  href="#open-positions"
                  onclick={(e) => { e.preventDefault(); document.querySelector('.lg\\:col-span-2 > div:last-child')?.scrollIntoView({ behavior: 'smooth' }); }}
                  class="block w-full py-3 px-6 bg-white text-gray-900 font-medium rounded-full hover:bg-gray-100 transition-colors text-center elevation-1"
                >
                  View Open Positions
                </a>
              </div>
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
</div>
