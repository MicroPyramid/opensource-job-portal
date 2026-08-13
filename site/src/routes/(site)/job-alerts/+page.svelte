<script lang="ts">
	import { BellRing, Loader, CheckCircle2 } from '@lucide/svelte';
	import { enhance } from '$app/forms';

	/** @type {{ data: Record<string, any>, form: Record<string, any> | null }} */
	let { data, form } = $props();

	let submitting = $state(false);
</script>

<svelte:head>
	<title>Job Alerts — get new jobs by email | PeelJobs</title>
	<meta
		name="description"
		content="Get an email when jobs matching your skills and preferred cities are posted on PeelJobs. Free, and unsubscribe any time."
	/>
	<link rel="canonical" href={data.canonical} />
</svelte:head>

<div class="min-h-screen bg-surface">
	<div class="mx-auto max-w-2xl px-4 py-10">
		<nav class="mb-5 text-sm text-muted" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2">
				<li><a href="/" class="hover:text-primary-600">Home</a></li>
				<li aria-hidden="true">/</li>
				<li class="text-gray-900">Job Alerts</li>
			</ol>
		</nav>

		<div class="mb-6 flex items-center gap-3">
			<div class="flex h-11 w-11 items-center justify-center rounded-xl bg-primary-50">
				<BellRing size={22} class="text-primary-600" />
			</div>
			<div>
				<h1 class="text-2xl font-semibold text-gray-900">Job alerts</h1>
				<p class="text-sm text-gray-600">New matching jobs, emailed to you every Monday.</p>
			</div>
		</div>

		{#if form?.success}
			<div class="rounded-lg border border-green-200 bg-green-50 p-6 text-center">
				<CheckCircle2 size={28} class="mx-auto mb-3 text-green-600" />
				<h2 class="mb-1 font-semibold text-gray-900">Almost there</h2>
				<p class="text-sm text-gray-700">
					We've sent a confirmation link to <span class="font-medium">{form.email}</span>. Click it
					to switch the alert on.
				</p>
			</div>
		{:else}
			<form
				method="POST"
				use:enhance={() => {
					submitting = true;
					return async ({ update }) => {
						await update();
						submitting = false;
					};
				}}
				class="space-y-5 rounded-lg border border-border bg-white p-6 shadow-sm"
			>
				{#if form?.message}
					<p class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-800">{form.message}</p>
				{/if}

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="email">
						Email address
					</label>
					<input
						id="email"
						name="email"
						type="email"
						required
						value={form?.values?.email ?? ''}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
					/>
				</div>

				<div>
					<label class="mb-1 block text-sm font-medium text-gray-700" for="name">
						Name this alert
					</label>
					<input
						id="name"
						name="name"
						type="text"
						required
						placeholder="e.g. Java jobs in Hyderabad"
						value={form?.values?.name ?? ''}
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
					/>
				</div>

				<div class="grid gap-4 sm:grid-cols-2">
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700" for="skills">Skills</label>
						<select
							id="skills"
							name="skills"
							multiple
							size="6"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
						>
							{#each data.skills as skill (skill.slug)}
								<option value={skill.slug}>{skill.name}</option>
							{/each}
						</select>
					</div>

					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700" for="locations">
							Locations
						</label>
						<select
							id="locations"
							name="locations"
							multiple
							size="6"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
						>
							{#each data.locations as location (location.slug)}
								<option value={location.slug}>{location.name}</option>
							{/each}
						</select>
					</div>
				</div>

				<p class="text-xs text-gray-500">Pick at least one skill or location.</p>

				<div class="grid gap-4 sm:grid-cols-2">
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700" for="min_year">
							Minimum experience (years)
						</label>
						<input
							id="min_year"
							name="min_year"
							type="number"
							min="0"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
						/>
					</div>
					<div>
						<label class="mb-1 block text-sm font-medium text-gray-700" for="max_year">
							Maximum experience (years)
						</label>
						<input
							id="max_year"
							name="max_year"
							type="number"
							min="0"
							class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
						/>
					</div>
				</div>

				<button
					type="submit"
					disabled={submitting}
					class="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3 text-sm font-medium text-white hover:bg-primary-hover disabled:opacity-60"
				>
					{#if submitting}
						<Loader size={16} class="animate-spin" />
					{/if}
					Create job alert
				</button>
			</form>
		{/if}
	</div>
</div>
