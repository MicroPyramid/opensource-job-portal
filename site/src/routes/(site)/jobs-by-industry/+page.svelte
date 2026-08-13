<script>
  import FacetDirectory from '$lib/components/jobs/FacetDirectory.svelte';

  /** @type {{ data: Record<string, any> }} */
  let { data } = $props();

  /** @param {string} slug */
  const hrefFor = (slug) => `/${slug}-industry-jobs/`;
</script>

<FacetDirectory
  seo={data.seo}
  groups={data.groups}
  total={data.total}
  canonical={data.canonical}
  breadcrumb={data.breadcrumb}
  {hrefFor}
/>
