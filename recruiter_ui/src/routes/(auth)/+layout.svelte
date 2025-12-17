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

<div class="min-h-screen bg-gray-50 flex flex-col">
	<!-- Header -->
	<header class="bg-white border-b border-gray-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
			<a href="/" class="flex items-center gap-2">
				<Building2 class="w-8 h-8 text-blue-600" />
				<span class="text-xl font-bold text-gray-900">PeelJobs</span>
				<span class="text-sm text-gray-500 ml-2">For Employers</span>
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
	<footer class="bg-white border-t border-gray-200 py-6">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-600">
				<p>&copy; 2025 PeelJobs. All rights reserved.</p>
				<div class="flex gap-6">
					<a href="/about/" class="hover:text-gray-900">About</a>
					<a href="/privacy/" class="hover:text-gray-900">Privacy</a>
					<a href="/terms/" class="hover:text-gray-900">Terms</a>
					<a href="/contact/" class="hover:text-gray-900">Contact</a>
				</div>
			</div>
		</div>
	</footer>
</div>
