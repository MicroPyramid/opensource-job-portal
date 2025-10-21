<script lang="ts">
	import {
		LayoutDashboard,
		Briefcase,
		Users,
		Building2,
		BarChart3,
		User,
		Menu,
		X
	} from '@lucide/svelte';

	let { children } = $props();
	let sidebarOpen = $state(false);

	const navItems = [
		{ href: '/dashboard/', icon: LayoutDashboard, label: 'Dashboard' },
		{ href: '/dashboard/jobs/', icon: Briefcase, label: 'Jobs' },
		{ href: '/dashboard/applicants/', icon: Users, label: 'Applicants' },
		{ href: '/dashboard/company/', icon: Building2, label: 'Company' },
		{ href: '/dashboard/analytics/', icon: BarChart3, label: 'Analytics' },
		{ href: '/dashboard/account/', icon: User, label: 'Account' }
	];
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
					{#each navItems as item}
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
				<div class="flex items-center gap-3">
					<div class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
						<User class="w-5 h-5 text-gray-600" />
					</div>
					<div class="flex-1 min-w-0">
						<p class="text-sm font-medium text-gray-900 truncate">Recruiter Name</p>
						<p class="text-xs text-gray-500 truncate">Company Admin</p>
					</div>
				</div>
			</div>
		</div>
	</aside>

	<!-- Overlay for mobile -->
	{#if sidebarOpen}
		<div
			class="fixed inset-0 bg-black bg-opacity-50 z-20 lg:hidden"
			onclick={() => (sidebarOpen = false)}
		></div>
	{/if}

	<!-- Main content -->
	<main class="lg:pl-64 pt-16 lg:pt-0">
		<div class="p-6 md:p-8">
			{@render children?.()}
		</div>
	</main>
</div>
