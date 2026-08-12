<script lang="ts">
	import { Loader2 } from '@lucide/svelte';
</script>

<svelte:head>
	<title>Signing you in - PeelJobs</title>
	<meta name="robots" content="noindex" />
</svelte:head>

<!--
	The server load handles the whole exchange and always redirects, so this
	only ever flashes if the browser is mid-navigation.
-->
<div class="min-h-screen bg-surface flex items-center justify-center p-4">
	<div class="text-center">
		<div
			class="inline-flex items-center justify-center w-16 h-16 bg-primary/10 rounded-full mb-6"
		>
			<Loader2 class="w-8 h-8 text-primary animate-spin" />
		</div>
		<h1 class="text-2xl font-semibold text-black mb-2">Signing you in…</h1>
		<p class="text-muted">Please wait while we complete your Google sign-in.</p>
	</div>
</div>
