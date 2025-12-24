<script lang="ts">
	import { Code } from '@lucide/svelte';
	import SkillsSection from '$lib/components/profile/SkillsSection.svelte';
</script>

<svelte:head>
	<title>Technical Skills - Profile - PeelJobs</title>
	<meta name="description" content="Manage your technical skills and expertise" />
</svelte:head>

<!-- Header -->
<div class="mb-6 animate-fade-in-up" style="opacity: 0;">
	<div class="flex items-center gap-3 mb-2">
		<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
			<Code size={20} class="text-primary-600" />
		</div>
		<div>
			<h2 class="text-xl lg:text-2xl font-bold text-gray-900">Technical Skills</h2>
			<p class="text-sm text-gray-600">Manage your technical skills and expertise</p>
		</div>
	</div>
</div>

<div
	class="bg-white rounded-2xl elevation-1 border border-gray-100 overflow-hidden animate-fade-in-up"
	style="opacity: 0; animation-delay: 100ms;"
>
	<SkillsSection />
</div>
