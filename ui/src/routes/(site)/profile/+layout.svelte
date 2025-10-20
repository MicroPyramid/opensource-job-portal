<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		User,
		GraduationCap,
		Briefcase,
		Award,
		FileText,
		Code
	} from '@lucide/svelte';

	// Define profile tabs
	const tabs = [
		{
			name: 'Profile',
			href: '/profile',
			icon: User,
			description: 'Personal information'
		},
		{
			name: 'Education',
			href: '/profile/education',
			icon: GraduationCap,
			description: 'Educational background'
		},
		{
			name: 'Skills',
			href: '/profile/skills',
			icon: Code,
			description: 'Technical skills'
		},
		{
			name: 'Employment',
			href: '/profile/employment',
			icon: Briefcase,
			description: 'Work history'
		},
		{
			name: 'Projects',
			href: '/profile/projects',
			icon: Briefcase,
			description: 'Project portfolio'
		},
		{
			name: 'Certifications',
			href: '/profile/certifications',
			icon: Award,
			description: 'Professional certifications'
		},
		{
			name: 'Resume',
			href: '/profile/resume',
			icon: FileText,
			description: 'Resume management'
		}
	];

	// Check if current path matches tab
	function isActive(href: string) {
		return $page.url.pathname === href;
	}

	// Handle tab change in mobile dropdown
	function handleTabChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		goto(target.value);
	}
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Profile Navigation Tabs -->
	<div class="bg-white border-b border-gray-200 sticky top-0 z-10 shadow-sm">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<!-- Mobile: Dropdown -->
			<div class="block lg:hidden py-4">
				<label for="profile-tab-select" class="sr-only">Select a tab</label>
				<select
					id="profile-tab-select"
					onchange={handleTabChange}
					class="block w-full rounded-md border-gray-300 focus:border-blue-500 focus:ring-blue-500"
				>
					{#each tabs as tab}
						<option value={tab.href} selected={isActive(tab.href)}>
							{tab.name}
						</option>
					{/each}
				</select>
			</div>

			<!-- Desktop: Horizontal Tabs -->
			<nav class="hidden lg:flex space-x-8 overflow-x-auto" aria-label="Profile sections">
				{#each tabs as tab}
				{@const active = isActive(tab.href)}
				<a
					href={tab.href}
					class="group inline-flex items-center gap-2 px-1 py-4 border-b-2 font-medium text-sm whitespace-nowrap transition-colors {active
						? 'border-blue-600 text-blue-600'
						: 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}"
					aria-current={active ? 'page' : undefined}
				>
					<tab.icon class="w-5 h-5 {active ? 'text-blue-600' : 'text-gray-400 group-hover:text-gray-500'}" />
					{tab.name}
				</a>
			{/each}
			</nav>
		</div>
	</div>

	<!-- Page Content -->
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
		<slot />
	</div>
</div>
