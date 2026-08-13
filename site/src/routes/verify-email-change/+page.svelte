<script lang="ts">
	import { CheckCircle2, XCircle } from '@lucide/svelte';

	/** @type {{ data: { status: 'success' | 'error', message: string } }} */
	export let data;
</script>

<svelte:head>
	<title>Confirm email change | PeelJobs</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<div class="min-h-screen flex items-center justify-center bg-surface px-4">
	<div class="w-full max-w-md rounded-2xl border border-border bg-white p-8 text-center shadow-sm">
		{#if data.status === 'success'}
			<div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-green-50">
				<CheckCircle2 size={28} class="text-green-600" />
			</div>
			<h1 class="mb-2 text-xl font-semibold text-gray-900">Email address updated</h1>
			<p class="mb-6 text-sm text-gray-600">{data.message}</p>
			<a
				href="/profile/"
				class="inline-flex items-center justify-center rounded-full bg-primary px-6 py-3 text-sm font-medium text-white hover:bg-primary-hover"
			>
				Back to your profile
			</a>
		{:else}
			<div class="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-red-50">
				<XCircle size={28} class="text-red-600" />
			</div>
			<h1 class="mb-2 text-xl font-semibold text-gray-900">We couldn't confirm that change</h1>
			<p class="mb-6 text-sm text-gray-600">{data.message}</p>
			<a
				href="/profile/"
				class="inline-flex items-center justify-center rounded-full bg-primary px-6 py-3 text-sm font-medium text-white hover:bg-primary-hover"
			>
				Go to your profile
			</a>
		{/if}
	</div>
</div>
