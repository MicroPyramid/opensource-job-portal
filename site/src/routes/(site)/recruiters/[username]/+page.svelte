<script>
  import JobLandingPage from '$lib/components/jobs/JobLandingPage.svelte';

  /** @type {{ data: Record<string, any> }} */
  let { data } = $props();

  // JobLandingPage renders an H1 plus a job list with crawlable pagination,
  // which is exactly what the legacy recruiter profile was. `intro` carries
  // the profile blurb the directory rows do not show.
  const seo = $derived({
    ...data.seo,
    intro:
      data.recruiter.profile_description ||
      (data.totalJobs
        ? `${data.totalJobs.toLocaleString('en-IN')} live ${data.totalJobs === 1 ? 'opening' : 'openings'}, updated daily.`
        : 'No live openings right now.')
  });
</script>

<JobLandingPage
  {seo}
  jobs={data.jobs}
  totalJobs={data.totalJobs}
  totalPages={data.totalPages}
  currentPage={data.currentPage}
  canonical={data.canonical}
  breadcrumb={{ label: data.seo.heading, href: `/recruiters/${data.recruiter.username}/` }}
/>
