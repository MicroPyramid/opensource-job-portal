<script lang="ts">
	import { CheckCircle2, XCircle } from '@lucide/svelte';
	import { enhance } from '$app/forms';

	/** @type {{ data: Record<string, any>, form: Record<string, any> | null }} */
	let { data, form } = $props();
</script>

<svelte:head>
	<title>Unsubscribe | PeelJobs</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<div class="flex min-h-screen items-center justify-center bg-surface px-4">
	<div class="w-full max-w-md rounded-2xl border border-border bg-white p-8 text-center shadow-sm">
		{#if data.status === 'success'}
			<div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-50">
				<CheckCircle2 size={28} class="text-green-600" />
			</div>
			<h1 class="mb-2 text-xl font-semibold text-gray-900">You're unsubscribed</h1>
			<p class="mb-6 text-sm text-gray-600">{data.message}</p>

			{#if form?.reasonSaved}
				<p class="text-sm text-gray-600">Thanks — that helps.</p>
			{:else}
				<form method="POST" action="?/reason" use:enhance class="space-y-3 text-left">
					<input type="hidden" name="type" value={data.type} />
					<input type="hidden" name="code" value={data.code} />

					<label class="block text-sm font-medium text-gray-700" for="reason">
						Mind telling us why? (optional)
					</label>
					<select
						id="reason"
						name="reason"
						class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
					>
						<option value="Too many emails">Too many emails</option>
						<option value="Not relevant">The jobs weren't relevant</option>
						<option value="Found a job">I found a job</option>
						<option value="Never signed up">I never signed up</option>
					</select>

					<button
						type="submit"
						class="w-full rounded-full bg-primary px-6 py-3 text-sm font-medium text-white hover:bg-primary-hover"
					>
						Send feedback
					</button>
				</form>
			{/if}
		{:else}
			<div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
				<XCircle size={28} class="text-red-600" />
			</div>
			<h1 class="mb-2 text-xl font-semibold text-gray-900">Something went wrong</h1>
			<p class="mb-6 text-sm text-gray-600">{data.message}</p>
			<a
				href="/"
				class="inline-flex items-center justify-center rounded-full bg-primary px-6 py-3 text-sm font-medium text-white hover:bg-primary-hover"
			>
				Go to PeelJobs
			</a>
		{/if}
	</div>
</div>
