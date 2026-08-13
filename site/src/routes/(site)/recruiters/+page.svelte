<script lang="ts">
	import { Users, Building2, Briefcase } from '@lucide/svelte';

	/** @type {{ data: Record<string, any> }} */
	let { data } = $props();

	// Pagination and letter links are plain <a> hrefs, not goto() — a crawler
	// has to be able to follow them.
	const hrefFor = (page: number, letter: string) => {
		const params = new URLSearchParams();
		if (letter) params.set('letter', letter);
		if (page > 1) params.set('page', String(page));
		const query = params.toString();
		return query ? `/recruiters/?${query}` : '/recruiters/';
	};

	let pageWindow = $derived.by(() => {
		const start = Math.max(1, data.currentPage - 2);
		const end = Math.min(data.totalPages, start + 4);
		return Array.from({ length: Math.max(0, end - start + 1) }, (_, i) => start + i);
	});
</script>

<svelte:head>
	<title>{data.seo.title}</title>
	<meta name="description" content={data.seo.description} />
	<link rel="canonical" href={data.canonical} />
	{#if data.currentPage > 1}
		<link rel="prev" href={hrefFor(data.currentPage - 1, data.letter)} />
	{/if}
	{#if data.currentPage < data.totalPages}
		<link rel="next" href={hrefFor(data.currentPage + 1, data.letter)} />
	{/if}
</svelte:head>

<div class="min-h-screen bg-surface">
	<div class="mx-auto max-w-6xl px-4 py-8">
		<nav class="mb-5 text-sm text-muted" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2">
				<li><a href="/" class="hover:text-primary-600">Home</a></li>
				<li aria-hidden="true">/</li>
				<li class="text-gray-900">Recruiters</li>
			</ol>
		</nav>

		<div class="mb-6 flex items-center gap-3">
			<div class="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50">
				<Users size={22} class="text-primary-600" />
			</div>
			<div>
				<h1 class="text-2xl font-semibold text-gray-900">
					Recruiters{data.letter ? ` — ${data.letter}` : ''}
				</h1>
				<p class="text-sm text-gray-600">
					{data.total.toLocaleString('en-IN')}
					{data.total === 1 ? 'recruiter' : 'recruiters'} with live openings
				</p>
			</div>
		</div>

		<!-- A–Z filter. Each letter is its own URL so crawlers can reach the tail. -->
		<nav class="mb-6 flex flex-wrap gap-1" aria-label="Filter recruiters by letter">
			<a
				href="/recruiters/"
				class="rounded-lg px-3 py-1.5 text-sm font-medium {data.letter
					? 'text-gray-600 hover:bg-white'
					: 'bg-primary-600 text-white'}"
			>
				All
			</a>
			{#each data.letters as letter (letter)}
				<a
					href={hrefFor(1, letter)}
					class="rounded-lg px-3 py-1.5 text-sm font-medium {data.letter === letter
						? 'bg-primary-600 text-white'
						: 'text-gray-600 hover:bg-white'}"
				>
					{letter}
				</a>
			{/each}
		</nav>

		{#if data.recruiters.length === 0}
			<p class="rounded-lg border border-border bg-white px-5 py-10 text-center text-sm text-gray-600">
				No recruiters found{data.letter ? ` starting with ${data.letter}` : ''}.
			</p>
		{:else}
			<ul class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
				{#each data.recruiters as recruiter (recruiter.username)}
					<li>
						<a
							href="/recruiters/{recruiter.username}/"
							class="flex h-full flex-col gap-2 rounded-lg border border-border bg-white p-4 transition-shadow hover:shadow-md"
						>
							<span class="font-medium text-gray-900">{recruiter.name}</span>

							{#if recruiter.company_name}
								<span class="flex items-center gap-1.5 text-sm text-gray-600">
									<Building2 size={14} />
									{recruiter.company_name}
								</span>
							{/if}

							<span class="mt-auto flex items-center gap-1.5 text-sm text-primary-600">
								<Briefcase size={14} />
								{recruiter.job_count}
								{recruiter.job_count === 1 ? 'opening' : 'openings'}
							</span>
						</a>
					</li>
				{/each}
			</ul>
		{/if}

		{#if data.totalPages > 1}
			<nav class="mt-8 flex flex-wrap items-center justify-center gap-1" aria-label="Pagination">
				{#if data.currentPage > 1}
					<a
						href={hrefFor(data.currentPage - 1, data.letter)}
						rel="prev"
						class="rounded px-3 py-2 text-sm font-medium text-muted hover:text-primary-600"
					>
						Previous
					</a>
				{/if}

				{#each pageWindow as n (n)}
					<a
						href={hrefFor(n, data.letter)}
						aria-current={n === data.currentPage ? 'page' : undefined}
						class="rounded px-3 py-2 text-sm font-medium {n === data.currentPage
							? 'bg-primary-600 text-white'
							: 'text-muted hover:text-primary-600'}"
					>
						{n}
					</a>
				{/each}

				{#if data.currentPage < data.totalPages}
					<a
						href={hrefFor(data.currentPage + 1, data.letter)}
						rel="next"
						class="rounded px-3 py-2 text-sm font-medium text-muted hover:text-primary-600"
					>
						Next
					</a>
				{/if}
			</nav>
		{/if}
	</div>
</div>
