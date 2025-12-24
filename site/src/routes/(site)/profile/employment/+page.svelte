<script lang="ts">
	import { Briefcase } from '@lucide/svelte';
	import EmploymentHistorySection from '$lib/components/profile/EmploymentHistorySection.svelte';
</script>

<svelte:head>
	<title>Employment History - Profile - PeelJobs</title>
	<meta name="description" content="Track your professional work experience" />
</svelte:head>

<!-- Header -->
<div class="mb-6 animate-fade-in-up" style="opacity: 0;">
	<div class="flex items-center gap-3 mb-2">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<Briefcase size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-xl lg:text-2xl font-bold text-gray-900">Employment History</h2>
			<p class="text-sm text-gray-600">Track your professional work experience</p>
		</div>
	</div>
</div>

<div
	class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
	style="opacity: 0; animation-delay: 100ms;"
>
	<EmploymentHistorySection />
</div>
