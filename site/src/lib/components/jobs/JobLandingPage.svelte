<script>
  import { Building2, MapPin, DollarSign, Briefcase, Users, Clock, ChevronRight } from '@lucide/svelte';

  /**
   * @type {{
   *   seo: { title: string, description: string, heading: string, intro: string },
   *   jobs: Array<Record<string, any>>,
   *   totalJobs: number,
   *   totalPages: number,
   *   currentPage: number,
   *   canonical: string,
   *   breadcrumb: { label: string, href: string }
   * }}
   */
  let { seo, jobs, totalJobs, totalPages, currentPage, canonical, breadcrumb } = $props();

  // Pagination is plain <a> hrefs, not goto() — a crawler has to be able to
  // follow it, which is the entire point of these pages.
  const pageHref = (/** @type {number} */ n) => (n <= 1 ? canonical : `${canonical}?page=${n}`);

  // A short window around the current page; enough to crawl, not so much that
  // it becomes a link farm.
  let pageWindow = $derived.by(() => {
    const start = Math.max(1, currentPage - 2);
    const end = Math.min(totalPages, start + 4);
    return Array.from({ length: Math.max(0, end - start + 1) }, (_, i) => start + i);
  });
</script>

<svelte:head>
  <title>{seo.title}</title>
  <meta name="description" content={seo.description} />
  <!--
    Self-referential, NOT pinned to page 1. Pointing every page of a series at
    page 1 declares pages 2..N duplicates, and the jobs that appear only on
    those pages then have no crawlable path in from this route — which on a
    facet like /java-jobs-in-bangalore/ (184 jobs, 10 pages) hides 90% of them.
  -->
  <link rel="canonical" href={pageHref(currentPage)} />
  {#if currentPage > 1}
    <link rel="prev" href={pageHref(currentPage - 1)} />
  {/if}
  {#if currentPage < totalPages}
    <link rel="next" href={pageHref(currentPage + 1)} />
  {/if}
  <meta property="og:title" content={seo.title} />
  <meta property="og:description" content={seo.description} />
  <meta property="og:type" content="website" />
</svelte:head>

<div class="min-h-screen bg-surface">
  <div class="max-w-5xl mx-auto px-4 py-8 lg:py-12">
    <!-- Breadcrumb -->
    <nav aria-label="Breadcrumb" class="mb-6 text-sm text-muted">
      <ol class="flex flex-wrap items-center gap-2">
        <li><a href="/" class="hover:text-primary-600">Home</a></li>
        <li aria-hidden="true">/</li>
        <li><a href="/jobs/" class="hover:text-primary-600">Jobs</a></li>
        <li aria-hidden="true">/</li>
        <li><span class="text-black font-medium">{breadcrumb.label}</span></li>
      </ol>
    </nav>

    <header class="mb-8">
      <h1 class="text-3xl lg:text-4xl font-semibold text-black tracking-tight mb-2">
        {seo.heading}
      </h1>
      <p class="text-muted">{seo.intro}</p>
    </header>

    {#if jobs.length === 0}
      <div class="bg-white rounded-lg border border-border p-10 text-center">
        <div class="w-14 h-14 rounded-full bg-surface flex items-center justify-center mx-auto mb-4">
          <Briefcase size={26} class="text-muted" />
        </div>
        <h2 class="text-lg font-semibold text-black mb-2">No openings right now</h2>
        <p class="text-muted mb-6">New jobs are posted daily. Try browsing all jobs in the meantime.</p>
        <a
          href="/jobs/"
          class="inline-flex items-center gap-2 px-5 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-full transition-all"
        >
          Browse all jobs
          <ChevronRight size={16} />
        </a>
      </div>
    {:else}
      <div class="space-y-3">
        {#each jobs as job (job.id)}
          <article class="group bg-white rounded-lg border border-border transition-all hover:shadow-card-hover hover:border-primary-200">
            <a
              href="/jobs/{String(job.slug ?? job.id).replace(/^\/+/, '')}"
              class="block p-4 lg:p-5"
              aria-label="View details for {job.title} at {job.company_name}"
            >
              <div class="flex gap-4">
                <div class="flex-shrink-0">
                  {#if job.company_logo}
                    <img src={job.company_logo} alt="{job.company_name} logo" class="w-12 h-12 rounded object-cover bg-surface" />
                  {:else}
                    <div class="w-12 h-12 rounded bg-primary-50 flex items-center justify-center">
                      <Building2 size={24} class="text-primary-600" />
                    </div>
                  {/if}
                </div>

                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-3 mb-1">
                    <h2 class="text-base font-semibold text-black group-hover:text-primary-600 transition-colors line-clamp-1">
                      {job.title}
                    </h2>
                    {#if job.accepts_applications === false}
                      <span class="flex-shrink-0 px-2 py-0.5 text-xs font-medium bg-surface text-muted rounded">Closed</span>
                    {/if}
                  </div>

                  <div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted mb-2">
                    <span class="font-medium text-black">{job.company_name}</span>
                    {#if job.location_display}
                      <span class="flex items-center gap-1">
                        <MapPin size={14} />
                        {job.location_display}
                      </span>
                    {/if}
                  </div>

                  <div class="flex flex-wrap items-center gap-2 mb-3">
                    {#if job.salary_display}
                      <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-success-light text-success-600 rounded text-xs font-medium">
                        <DollarSign size={12} />
                        {job.salary_display}
                      </span>
                    {/if}
                    {#if job.job_type}
                      <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-50 text-primary-600 rounded text-xs font-medium">
                        <Briefcase size={12} />
                        {job.job_type}
                      </span>
                    {/if}
                    {#if job.experience_display}
                      <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-surface text-muted rounded text-xs font-medium">
                        <Users size={12} />
                        {job.experience_display}
                      </span>
                    {/if}
                  </div>

                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4 text-xs text-muted">
                      {#if job.time_ago}
                        <span class="flex items-center gap-1">
                          <Clock size={12} />
                          {job.time_ago}
                        </span>
                      {/if}
                      <span class="flex items-center gap-1">
                        <Users size={12} />
                        {job.applicants_count ?? 0} applicants
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
          </article>
        {/each}
      </div>

      {#if totalPages > 1}
        <nav aria-label="Pagination" class="mt-8 flex justify-center">
          <ul class="inline-flex items-center gap-1 bg-white rounded-lg border border-border p-1">
            {#if currentPage > 1}
              <li>
                <a href={pageHref(currentPage - 1)} rel="prev" class="px-3 py-2 text-sm font-medium text-muted hover:text-primary-600 rounded">
                  Previous
                </a>
              </li>
            {/if}
            {#each pageWindow as n (n)}
              <li>
                <a
                  href={pageHref(n)}
                  aria-current={n === currentPage ? 'page' : undefined}
                  class="px-3 py-2 text-sm font-medium rounded {n === currentPage
                    ? 'bg-primary-600 text-white'
                    : 'text-muted hover:text-primary-600'}"
                >
                  {n}
                </a>
              </li>
            {/each}
            {#if currentPage < totalPages}
              <li>
                <a href={pageHref(currentPage + 1)} rel="next" class="px-3 py-2 text-sm font-medium text-muted hover:text-primary-600 rounded">
                  Next
                </a>
              </li>
            {/if}
          </ul>
        </nav>
      {/if}
    {/if}
  </div>
</div>
