<script>
  /**
   * A–Z directory of job categories.
   *
   * These pages exist for internal linking: they are how a crawler (and a
   * browsing user) reaches the several hundred landing pages. So every entry
   * is a plain server-rendered <a>, and nothing here is filtered or paginated
   * client-side — a hidden link is a link that does not count.
   *
   * @type {{
   *   seo: { title: string, description: string, heading: string, intro: string },
   *   groups: Array<{ letter: string, items: Array<{ id: number, name: string, slug: string, count: number }> }>,
   *   total: number,
   *   canonical: string,
   *   breadcrumb: { label: string },
   *   hrefFor: (slug: string) => string
   * }}
   */
  let { seo, groups, total, canonical, breadcrumb, hrefFor } = $props();
</script>

<svelte:head>
  <title>{seo.title}</title>
  <meta name="description" content={seo.description} />
  <link rel="canonical" href={canonical} />
  <meta property="og:title" content={seo.title} />
  <meta property="og:description" content={seo.description} />
  <meta property="og:type" content="website" />
</svelte:head>

<div class="min-h-screen bg-surface">
  <div class="max-w-5xl mx-auto px-4 py-8 lg:py-12">
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

    {#if total === 0}
      <div class="bg-white rounded-lg border border-border p-10 text-center">
        <h2 class="text-lg font-semibold text-black mb-2">Nothing to show yet</h2>
        <p class="text-muted mb-6">Categories appear here once jobs are posted against them.</p>
        <a href="/jobs/" class="inline-flex items-center gap-2 px-5 py-3 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-full transition-all">
          Browse all jobs
        </a>
      </div>
    {:else}
      <!-- Jump links. Anchors, so they work without JS. -->
      <nav aria-label="Jump to letter" class="mb-8 bg-white rounded-lg border border-border p-3">
        <ul class="flex flex-wrap gap-1">
          {#each groups as group (group.letter)}
            <li>
              <a
                href="#letter-{group.letter === '#' ? 'other' : group.letter}"
                class="inline-flex items-center justify-center w-8 h-8 rounded text-sm font-semibold text-muted hover:bg-primary-50 hover:text-primary-600 transition-colors"
              >
                {group.letter}
              </a>
            </li>
          {/each}
        </ul>
      </nav>

      <div class="space-y-8">
        {#each groups as group (group.letter)}
          <section id="letter-{group.letter === '#' ? 'other' : group.letter}" class="scroll-mt-4">
            <h2 class="text-xl font-semibold text-black mb-3 pb-2 border-b border-border">
              {group.letter}
            </h2>
            <ul class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-1">
              {#each group.items as item (item.id)}
                <li>
                  <a
                    href={hrefFor(item.slug)}
                    class="group flex items-baseline justify-between gap-2 py-1.5 text-sm hover:text-primary-600 transition-colors"
                  >
                    <span class="text-black group-hover:text-primary-600 truncate">{item.name}</span>
                    <span class="flex-shrink-0 text-xs text-muted tabular-nums">{item.count}</span>
                  </a>
                </li>
              {/each}
            </ul>
          </section>
        {/each}
      </div>
    {/if}
  </div>
</div>
