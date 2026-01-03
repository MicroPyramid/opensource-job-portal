<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import {
		User,
		GraduationCap,
		Briefcase,
		Award,
		FileText,
		Code,
		FolderOpen,
		ChevronRight
	} from '@lucide/svelte';

	interface Tab {
		name: string;
		href: string;
		icon: typeof User;
		description: string;
	}

	const tabs: Tab[] = [
		{
			name: 'Profile',
			href: '/profile/',
			icon: User,
			description: 'Personal information'
		},
		{
			name: 'Education',
			href: '/profile/education/',
			icon: GraduationCap,
			description: 'Educational background'
		},
		{
			name: 'Skills',
			href: '/profile/skills/',
			icon: Code,
			description: 'Technical skills'
		},
		{
			name: 'Employment',
			href: '/profile/employment/',
			icon: Briefcase,
			description: 'Work history'
		},
		{
			name: 'Projects',
			href: '/profile/projects/',
			icon: FolderOpen,
			description: 'Project portfolio'
		},
		{
			name: 'Certifications',
			href: '/profile/certifications/',
			icon: Award,
			description: 'Professional certifications'
		}
	];

	function isActive(href: string): boolean {
		const pathname = $page.url.pathname;
		return pathname === href || pathname === href.slice(0, -1);
	}

	function handleTabChange(event: Event) {
		const target = event.target as HTMLSelectElement;
		goto(target.value);
	}

	function getCurrentTab(): Tab | undefined {
		return tabs.find((tab) => isActive(tab.href));
	}
</script>

<!-- Hero Section -->
<section class="bg-[#1D2226] text-white py-10 lg:py-12 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<!-- Breadcrumb -->
		<nav class="mb-5" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2 text-sm text-gray-400">
				<li>
					<a href="/jobseeker-dashboard/" class="hover:text-white transition-colors">Dashboard</a>
				</li>
				<li class="flex items-center gap-2">
					<ChevronRight size={14} />
					<span class="text-white font-medium">Profile</span>
				</li>
			</ol>
		</nav>

		<div class="flex items-center gap-4">
			<div
				class="w-14 h-14 rounded-lg bg-white/10 flex items-center justify-center animate-fade-in-up"
				style="opacity: 0; animation-fill-mode: forwards;"
			>
				<User size={28} class="text-white/80" />
			</div>
			<div>
				<h1
					class="text-2xl lg:text-3xl font-semibold tracking-tight mb-1 animate-fade-in-up"
					style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;"
				>
					My Profile
				</h1>
				<p class="text-gray-400 animate-fade-in-up" style="opacity: 0; animation-delay: 150ms; animation-fill-mode: forwards;">
					Manage your profile and professional information
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Navigation Tabs -->
<div class="bg-white border-b border-border sticky top-0 z-10 shadow-sm">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<!-- Mobile: Dropdown -->
		<div class="block lg:hidden py-4">
			<label for="profile-tab-select" class="sr-only">Select a tab</label>
			<select
				id="profile-tab-select"
				onchange={handleTabChange}
				value={getCurrentTab()?.href || ''}
				class="block w-full rounded-lg border border-border bg-surface py-3 px-4 text-black focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
			>
				{#each tabs as tab}
					<option value={tab.href} selected={isActive(tab.href)}>
						{tab.name}
					</option>
				{/each}
			</select>
		</div>

		<!-- Desktop: Horizontal Tabs -->
		<nav class="hidden lg:flex items-center gap-1 overflow-x-auto py-1" aria-label="Profile sections">
			{#each tabs as tab}
				{@const active = isActive(tab.href)}
				<a
					href={tab.href}
					class="group inline-flex items-center gap-2 px-4 py-3 rounded-lg font-medium text-sm whitespace-nowrap transition-all my-1 {active
						? 'bg-primary/10 text-primary'
						: 'text-muted hover:bg-surface hover:text-black'}"
					aria-current={active ? 'page' : undefined}
				>
					<tab.icon
						class="w-5 h-5 {active ? 'text-primary' : 'text-muted group-hover:text-black'}"
					/>
					{tab.name}
				</a>
			{/each}
		</nav>
	</div>
</div>

<!-- Page Content -->
<section class="py-6 lg:py-8 bg-surface min-h-[60vh]">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<slot />
	</div>
</section>
