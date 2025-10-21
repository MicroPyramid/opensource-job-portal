<script lang="ts">
	import { Mail, Lock, Eye, EyeOff } from '@lucide/svelte';
	import { getContext } from 'svelte';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-[1400px]';
	layout.mainClass = 'flex justify-center items-start py-2 px-4 sm:px-5 lg:px-6';

	let showPassword = $state(false);
	let rememberMe = $state(false);

	let formData = $state({
		email: '',
		password: ''
	});

	function handleLogin(e: Event) {
		e.preventDefault();
		console.log('Logging in...', formData);
		// API call here
		// On success, redirect to /dashboard/
	}

	function signInWithGoogle() {
		console.log('Sign in with Google');
		// OAuth flow
	}
</script>

<svelte:head>
	<title>Login - PeelJobs Recruiter</title>
</svelte:head>

<div class="w-full">
	<div class="grid lg:grid-cols-2 gap-10 items-start">
		<!-- Left Column: Marketing Content -->
		<div class="space-y-6 lg:sticky lg:top-6">
			<!-- Hero Section -->
			<div>
				<h1 class="text-3xl xl:text-4xl font-bold text-gray-900 mb-4 leading-tight">
					Welcome Back to PeelJobs
				</h1>
				<p class="text-base xl:text-lg text-gray-600 leading-relaxed">
					Continue managing your job postings and connecting with top talent across India.
				</p>
			</div>

			<!-- Key Statistics -->
			<div class="grid grid-cols-2 gap-4">
				<div class="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
					<div class="text-3xl font-bold text-blue-600 mb-1">100k+</div>
					<p class="text-sm text-gray-700 font-medium">Active Job Seekers</p>
				</div>
				<div class="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
					<div class="text-3xl font-bold text-green-600 mb-1">1000+</div>
					<p class="text-sm text-gray-700 font-medium">Daily Applications</p>
				</div>
				<div class="bg-purple-50 border border-purple-200 rounded-xl p-6 text-center">
					<div class="text-3xl font-bold text-purple-600 mb-1">500+</div>
					<p class="text-sm text-gray-700 font-medium">Companies Trust Us</p>
				</div>
				<div class="bg-orange-50 border border-orange-200 rounded-xl p-6 text-center">
					<div class="text-3xl font-bold text-orange-600 mb-1">24/7</div>
					<p class="text-sm text-gray-700 font-medium">Expert Support</p>
				</div>
			</div>

			<!-- Quick Stats for Employers -->
			<div class="bg-white rounded-2xl shadow-lg border border-gray-200 p-7">
				<h3 class="text-xl font-bold text-gray-900 mb-6 flex items-center gap-2">
					<svg class="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
						<path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
					</svg>
					Your Dashboard Awaits
				</h3>
				<div class="space-y-6">
					<div class="flex items-start gap-4">
						<div class="bg-blue-100 rounded-full p-3 flex-shrink-0">
							<svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
							</svg>
						</div>
						<div>
							<h4 class="font-semibold text-gray-900 text-sm mb-1">Manage Your Jobs</h4>
							<p class="text-sm text-gray-600 leading-relaxed">View and manage all your active job postings in one place</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-green-100 rounded-full p-3 flex-shrink-0">
							<svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
							</svg>
						</div>
						<div>
							<h4 class="font-semibold text-gray-900 text-sm mb-1">Review Applicants</h4>
							<p class="text-sm text-gray-600 leading-relaxed">Access qualified candidates and their detailed profiles</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-purple-100 rounded-full p-3 flex-shrink-0">
							<svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
							</svg>
						</div>
						<div>
							<h4 class="font-semibold text-gray-900 text-sm mb-1">Track Performance</h4>
							<p class="text-sm text-gray-600 leading-relaxed">Monitor job views, applications, and hiring metrics</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-orange-100 rounded-full p-3 flex-shrink-0">
							<svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
							</svg>
						</div>
						<div>
							<h4 class="font-semibold text-gray-900 text-sm mb-1">Connect with Talent</h4>
							<p class="text-sm text-gray-600 leading-relaxed">Message and schedule interviews with candidates</p>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- Right Column: Login Form -->
		<div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
			<!-- Header -->
			<div class="text-center mb-6">
				<h1 class="text-2xl font-bold text-gray-900">Welcome Back</h1>
				<p class="text-gray-600 mt-2">Sign in to your employer account</p>
			</div>

			<!-- Login Form -->
			<form onsubmit={handleLogin} class="space-y-5">
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 mb-1">
						Email Address
					</label>
					<div class="relative">
						<Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="email"
							id="email"
							bind:value={formData.email}
							required
							placeholder="you@company.com"
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 mb-1">
						Password
					</label>
					<div class="relative">
						<Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type={showPassword ? 'text' : 'password'}
							id="password"
							bind:value={formData.password}
							required
							placeholder="Enter your password"
							class="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
						<button
							type="button"
							onclick={() => (showPassword = !showPassword)}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
						>
							{#if showPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
				</div>

				<div class="flex items-center justify-between">
					<label class="flex items-center gap-2 cursor-pointer">
						<input type="checkbox" bind:checked={rememberMe} class="w-4 h-4 text-blue-600 rounded" />
						<span class="text-sm text-gray-700">Remember me</span>
					</label>

					<a href="/forgot-password/" class="text-sm font-medium text-blue-600 hover:text-blue-700">
						Forgot password?
					</a>
				</div>

				<button
					type="submit"
					class="w-full py-2.5 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
				>
					Sign In
				</button>
			</form>

			<!-- Divider -->
			<div class="mt-5">
				<div class="relative">
					<div class="absolute inset-0 flex items-center">
						<div class="w-full border-t border-gray-300"></div>
					</div>
					<div class="relative flex justify-center text-sm">
						<span class="px-4 bg-white text-gray-500">Or continue with</span>
					</div>
				</div>

				<!-- Google Sign In -->
				<button
					type="button"
					onclick={signInWithGoogle}
					class="mt-4 w-full flex items-center justify-center gap-3 px-4 py-2.5 border-2 border-gray-300 rounded-lg text-sm font-semibold text-gray-700 bg-white hover:border-gray-400 hover:shadow-md transition-all"
				>
					<svg class="w-5 h-5" viewBox="0 0 24 24">
						<path
							fill="#4285F4"
							d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
						/>
						<path
							fill="#34A853"
							d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
						/>
						<path
							fill="#FBBC05"
							d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
						/>
						<path
							fill="#EA4335"
							d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
						/>
					</svg>
					Sign in with Google
				</button>
			</div>

			<!-- Sign Up Link -->
			<p class="mt-5 text-center text-sm text-gray-600">
				Don't have an account?
				<a href="/signup/" class="font-medium text-blue-600 hover:text-blue-700">Sign up for free</a>
			</p>

			<!-- Job Seeker Link -->
			<div class="mt-4 pt-4 border-t border-gray-200">
				<p class="text-center text-sm text-gray-600">
					Looking for a job?
					<a href="https://peeljobs.com/login/" class="font-medium text-blue-600 hover:text-blue-700">
						Job Seeker Login
					</a>
				</p>
			</div>

			<!-- Trust Indicators -->
			<div class="mt-4 pt-3 border-t border-gray-200">
				<div class="flex justify-center flex-wrap gap-3 text-xs text-gray-500">
					<div class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clip-rule="evenodd" />
						</svg>
						SSL Encrypted
					</div>
					<div class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
						</svg>
						GDPR Compliant
					</div>
					<div class="flex items-center gap-1">
						<svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
							<path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
						</svg>
						24/7 Support
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
