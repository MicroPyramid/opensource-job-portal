<script lang="ts">
	import {
		LayoutDashboard,
		Briefcase,
		Users,
		Building2,
		BarChart3,
		User,
		Menu,
		X,
		LogOut,
		ChevronDown
	} from '@lucide/svelte';
	import { authStore } from '$lib/stores/auth';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import type { LayoutData } from './$types';

	let { children, data }: { children: any; data: LayoutData } = $props();
	let sidebarOpen = $state(false);
	let userMenuOpen = $state(false);

	// Get user info from server data (SSR-safe) or fallback to store
	let user = $derived(data.user || $authStore.user);

	// Base navigation items available to all users
	const baseNavItems = [
		{ href: '/dashboard/', icon: LayoutDashboard, label: 'Dashboard' },
		{ href: '/dashboard/jobs/', icon: Briefcase, label: 'Jobs' },
		{ href: '/dashboard/applicants/', icon: Users, label: 'Applicants' },
		{ href: '/dashboard/analytics/', icon: BarChart3, label: 'Analytics' },
		{ href: '/dashboard/account/', icon: User, label: 'Account' }
	];

	// Company nav item (only for users with a company)
	const companyNavItem = { href: '/dashboard/company/', icon: Building2, label: 'Company' };

	// Compute final nav items based on user's company status
	let navItems = $derived(
		user?.company ? [
			baseNavItems[0], // Dashboard
			baseNavItems[1], // Jobs
			baseNavItems[2], // Applicants
			companyNavItem,  // Company (only if user has a company)
			baseNavItems[3], // Analytics
			baseNavItems[4]  // Account
		] : baseNavItems
	);

	async function handleLogout() {
		await authStore.logout();
		goto('/login/');
	}

	// Sync server-loaded user data with auth store on mount
	onMount(() => {
		if (data.user) {
			// Update store with server-loaded user data
			// This keeps localStorage in sync with the actual authenticated state
			authStore.updateUser(data.user);
		}
	});
</script>

<div class="min-h-screen bg-gray-50">
	<!-- Mobile menu button -->
	<div class="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-40 px-4 py-3">
		<button
			onclick={() => (sidebarOpen = !sidebarOpen)}
			class="p-2 rounded-md text-gray-600 hover:bg-gray-100"
			aria-label="Toggle menu"
		>
			{#if sidebarOpen}
				<X class="w-6 h-6" />
			{:else}
				<Menu class="w-6 h-6" />
			{/if}
		</button>
	</div>

	<!-- Sidebar -->
	<aside
		class="fixed top-0 left-0 bottom-0 w-64 bg-white border-r border-gray-200 z-30 transform transition-transform duration-200 {sidebarOpen
			? 'translate-x-0'
			: '-translate-x-full lg:translate-x-0'}"
	>
		<div class="h-full flex flex-col">
			<!-- Logo -->
			<div class="h-16 flex items-center px-6 border-b border-gray-200">
				<h1 class="text-xl font-bold text-gray-900">PeelJobs</h1>
			</div>

			<!-- Navigation -->
			<nav class="flex-1 overflow-y-auto py-4">
				<ul class="space-y-1 px-3">
					{#each navItems as item (item.href)}
						<li>
							<a
								href={item.href}
								class="flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-700 rounded-md hover:bg-gray-100 hover:text-gray-900 transition-colors"
							>
								<item.icon class="w-5 h-5" />
								{item.label}
							</a>
						</li>
					{/each}
				</ul>
			</nav>

			<!-- User section -->
			<div class="border-t border-gray-200 p-4">
				<div class="relative">
					<button
						onclick={() => (userMenuOpen = !userMenuOpen)}
						class="w-full flex items-center gap-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
					>
						<div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
							<User class="w-5 h-5 text-blue-600" />
						</div>
						<div class="flex-1 min-w-0 text-left">
							<p class="text-sm font-medium text-gray-900 truncate">
								{user?.first_name || 'User'} {user?.last_name || ''}
							</p>
							<p class="text-xs text-gray-500 truncate">
								{user?.company?.name || 'Independent Recruiter'}
							</p>
						</div>
						<ChevronDown class="w-4 h-4 text-gray-400 flex-shrink-0 transition-transform {userMenuOpen ? 'rotate-180' : ''}" />
					</button>

					<!-- Dropdown menu -->
					{#if userMenuOpen}
						<div class="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-lg border border-gray-200 py-1">
							<a
								href="/dashboard/account/"
								class="flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
							>
								<User class="w-4 h-4" />
								Account Settings
							</a>
							<button
								onclick={handleLogout}
								class="w-full flex items-center gap-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50"
							>
								<LogOut class="w-4 h-4" />
								Logout
							</button>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</aside>

	<!-- Overlay for mobile -->
	{#if sidebarOpen}
		<div
			class="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
			role="button"
			tabindex="0"
			onclick={() => (sidebarOpen = false)}
			onkeydown={(e) => e.key === 'Enter' && (sidebarOpen = false)}
		></div>
	{/if}

	<!-- Main content -->
	<main class="lg:pl-64 pt-16 lg:pt-0">
		<div class="p-6 md:p-8">
			{@render children?.()}
		</div>
	</main>
</div>
