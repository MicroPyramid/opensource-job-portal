<script lang="ts">
	import { Mail, Lock, Eye, EyeOff, Briefcase, Users, BarChart3, MessageSquare, Shield, Clock, CheckCircle } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Button, Input, Card, FormField } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-6xl';
	layout.mainClass = 'flex justify-center items-start py-8 px-4 sm:px-6 lg:px-8';

	let showPassword = $state(false);
	let rememberMe = $state(false);
	let loading = $state(false);

	let error = $derived(form?.error || '');
	let emailValue = $state(form?.email || '');
</script>

<svelte:head>
	<title>Login - PeelJobs Recruiter</title>
	<meta name="description" content="Sign in to your PeelJobs employer account to manage job postings and connect with top talent." />
</svelte:head>

<div class="w-full">
	<div class="grid lg:grid-cols-2 gap-12 items-start">
		<!-- Left Column: Marketing Content -->
		<div class="space-y-8 lg:sticky lg:top-8 hidden lg:block">
			<!-- Hero Section -->
			<div>
				<h1 class="text-3xl xl:text-4xl font-semibold text-black mb-4 leading-tight">
					Welcome Back to PeelJobs
				</h1>
				<p class="text-base xl:text-lg text-muted leading-relaxed">
					Continue managing your job postings and connecting with top talent across India.
				</p>
			</div>

			<!-- Key Statistics -->
			<div class="grid grid-cols-2 gap-4">
				<div class="bg-primary/5 border border-primary/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-primary mb-1">100k+</div>
					<p class="text-sm text-muted font-medium">Active Job Seekers</p>
				</div>
				<div class="bg-success-light border border-success/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-success mb-1">1000+</div>
					<p class="text-sm text-muted font-medium">Daily Applications</p>
				</div>
				<div class="bg-primary/5 border border-primary/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-primary mb-1">500+</div>
					<p class="text-sm text-muted font-medium">Companies Trust Us</p>
				</div>
				<div class="bg-warning-light border border-warning/20 rounded-lg p-5 text-center">
					<div class="text-2xl font-semibold text-warning mb-1">24/7</div>
					<p class="text-sm text-muted font-medium">Expert Support</p>
				</div>
			</div>

			<!-- Dashboard Features -->
			<Card padding="lg" class="shadow-md">
				<h3 class="text-xl font-semibold text-black mb-6 flex items-center gap-2">
					<BarChart3 class="w-5 h-5 text-primary" />
					Your Dashboard Awaits
				</h3>
				<div class="space-y-5">
					<div class="flex items-start gap-4">
						<div class="bg-primary/10 rounded-full p-2.5 flex-shrink-0">
							<Briefcase class="w-5 h-5 text-primary" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Manage Your Jobs</h4>
							<p class="text-sm text-muted leading-relaxed">View and manage all your active job postings in one place</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-success-light rounded-full p-2.5 flex-shrink-0">
							<Users class="w-5 h-5 text-success" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Review Applicants</h4>
							<p class="text-sm text-muted leading-relaxed">Access qualified candidates and their detailed profiles</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-primary/10 rounded-full p-2.5 flex-shrink-0">
							<BarChart3 class="w-5 h-5 text-primary" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Track Performance</h4>
							<p class="text-sm text-muted leading-relaxed">Monitor job views, applications, and hiring metrics</p>
						</div>
					</div>
					<div class="flex items-start gap-4">
						<div class="bg-warning-light rounded-full p-2.5 flex-shrink-0">
							<MessageSquare class="w-5 h-5 text-warning" />
						</div>
						<div>
							<h4 class="font-medium text-black text-sm mb-0.5">Connect with Talent</h4>
							<p class="text-sm text-muted leading-relaxed">Message and schedule interviews with candidates</p>
						</div>
					</div>
				</div>
			</Card>
		</div>

		<!-- Right Column: Login Form -->
		<Card padding="lg" class="shadow-lg">
			<!-- Header -->
			<div class="text-center mb-8">
				<h2 class="text-2xl font-semibold text-black">Welcome Back</h2>
				<p class="text-muted mt-2">Sign in to your employer account</p>
			</div>

			<!-- Login Form -->
			<form method="POST" use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					loading = false;
					await update();
				};
			}} class="space-y-5">
				<!-- Hidden field for redirect URL -->
				<input type="hidden" name="redirect_to" value={data.redirectTo} />

				<!-- Error Message -->
				{#if error}
					<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm whitespace-pre-line">
						{error}
					</div>
				{/if}

				<FormField label="Email Address">
					<Input
						type="email"
						id="email"
						name="email"
						value={emailValue}
						required
						disabled={loading}
						placeholder="you@company.com"
						size="lg"
					>
						{#snippet iconLeft()}
							<Mail class="w-5 h-5" />
						{/snippet}
					</Input>
				</FormField>

				<FormField label="Password">
					<div class="relative">
						<Input
							type={showPassword ? 'text' : 'password'}
							id="password"
							name="password"
							required
							disabled={loading}
							placeholder="Enter your password"
							size="lg"
							class="pr-12"
						>
							{#snippet iconLeft()}
								<Lock class="w-5 h-5" />
							{/snippet}
						</Input>
						<button
							type="button"
							onclick={() => (showPassword = !showPassword)}
							disabled={loading}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors disabled:opacity-50"
							aria-label={showPassword ? 'Hide password' : 'Show password'}
						>
							{#if showPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
				</FormField>

				<div class="flex items-center justify-between">
					<label class="flex items-center gap-2 cursor-pointer group">
						<input
							type="checkbox"
							name="remember_me"
							bind:checked={rememberMe}
							class="w-4 h-4 text-primary border-border rounded focus:ring-primary/20 focus:ring-2"
						/>
						<span class="text-sm text-muted group-hover:text-black transition-colors">Remember me</span>
					</label>

					<a href="/forgot-password/" class="text-sm font-medium text-primary hover:text-primary-hover transition-colors">
						Forgot password?
					</a>
				</div>

				<Button type="submit" size="lg" {loading} class="w-full">
					{#if loading}
						Signing in...
					{:else}
						Sign In
					{/if}
				</Button>
			</form>

			<!-- Sign Up Link -->
			<p class="mt-6 text-center text-sm text-muted">
				Don't have an account?
				<a href="/signup/" class="font-medium text-primary hover:text-primary-hover transition-colors">Sign up for free</a>
			</p>

			<!-- Job Seeker Link -->
			<div class="mt-5 pt-5 border-t border-border">
				<p class="text-center text-sm text-muted">
					Looking for a job?
					<a href="https://peeljobs.com/login/" class="font-medium text-primary hover:text-primary-hover transition-colors">
						Job Seeker Login
					</a>
				</p>
			</div>

			<!-- Trust Indicators -->
			<div class="mt-5 pt-5 border-t border-border">
				<div class="flex justify-center flex-wrap gap-4 text-xs text-muted">
					<div class="flex items-center gap-1.5">
						<Shield class="w-3.5 h-3.5" />
						<span>SSL Encrypted</span>
					</div>
					<div class="flex items-center gap-1.5">
						<CheckCircle class="w-3.5 h-3.5" />
						<span>GDPR Compliant</span>
					</div>
					<div class="flex items-center gap-1.5">
						<Clock class="w-3.5 h-3.5" />
						<span>24/7 Support</span>
					</div>
				</div>
			</div>
		</Card>
	</div>
</div>
