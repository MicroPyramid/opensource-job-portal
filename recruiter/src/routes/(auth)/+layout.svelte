<script lang="ts">
	import { Building2 } from '@lucide/svelte';
	import { setContext } from 'svelte';

	const layoutState = $state({
		containerClass: 'max-w-md',
		mainClass: 'flex-1 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8'
	});

	setContext('authLayout', layoutState);

	let { children } = $props();
</script>

<div class="min-h-screen bg-surface flex flex-col">
	<!-- Header -->
	<header class="bg-white border-b border-border">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<a href="/" class="flex items-center gap-2">
				<Building2 class="w-8 h-8 text-primary" />
				<span class="text-xl font-bold text-black">PeelJobs</span>
				<span class="text-sm text-muted ml-2">For Employers</span>
			</a>
		</div>
	</header>

	<!-- Main Content -->
	<main class={layoutState.mainClass}>
		<div class={`w-full ${layoutState.containerClass}`}>
			{@render children?.()}
		</div>
	</main>

	<!-- Footer -->
	<footer class="bg-white border-t border-border py-6">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted">
				<p>&copy; 2025 PeelJobs. All rights reserved.</p>
				<div class="flex gap-6">
					<a href="/about/" class="hover:text-black transition-colors">About</a>
					<a href="/privacy/" class="hover:text-black transition-colors">Privacy</a>
					<a href="/terms/" class="hover:text-black transition-colors">Terms</a>
					<a href="/contact/" class="hover:text-black transition-colors">Contact</a>
				</div>
			</div>
		</div>
	</footer>
</div>
