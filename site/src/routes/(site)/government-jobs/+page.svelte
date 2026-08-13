<script>
  import JobLandingPage from '$lib/components/jobs/JobLandingPage.svelte';

  /** @type {{ data: Record<string, any> }} */
  let { data } = $props();
</script>

<JobLandingPage
  seo={data.seo}
  jobs={data.jobs}
  totalJobs={data.totalJobs}
  totalPages={data.totalPages}
  currentPage={data.currentPage}
  canonical={data.canonical}
  breadcrumb={data.breadcrumb}
/>
