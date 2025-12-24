<script lang="ts">
	import { Lock, Eye, EyeOff, CheckCircle2 } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let showPassword = $state(false);
	let showConfirmPassword = $state(false);
	let loading = $state(false);

	let formData = $state({
		password: '',
		confirmPassword: ''
	});

	// Get success state and error from form action
	let isSubmitted = $derived(form?.success || false);
	let error = $derived(form?.error || '');

	function validatePassword(password: string) {
		return {
			minLength: password.length >= 8,
			hasUpper: /[A-Z]/.test(password),
			hasLower: /[a-z]/.test(password),
			hasNumber: /\d/.test(password)
		};
	}

	let validation = $derived(validatePassword(formData.password));
</script>

<svelte:head>
	<title>Reset Password - PeelJobs Recruiter</title>
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-8">
	{#if !isSubmitted}
		<!-- Reset Password Form -->
		<div>
			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-2xl font-bold text-gray-900">Reset Password</h1>
				<p class="text-gray-600 mt-2">Create a new password for your account</p>
			</div>

			<!-- Form -->
			<form method="POST" use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					loading = false;
					await update();
				};
			}} class="space-y-6">
				<!-- Hidden field for token -->
				<input type="hidden" name="token" value={data.token} />

				{#if error}
					<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
						{error}
					</div>
				{/if}

				<div>
					<label for="password" class="block text-sm font-medium text-gray-700 mb-2">
						New Password
					</label>
					<div class="relative">
						<Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type={showPassword ? 'text' : 'password'}
							id="password"
							name="password"
							bind:value={formData.password}
							required
							disabled={loading}
							placeholder="Create a strong password"
							class="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
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

					<!-- Password Requirements -->
					{#if formData.password}
						<div class="mt-3 space-y-2">
							<p class="text-xs font-medium text-gray-700">Password must contain:</p>
							<div class="space-y-1">
								<div class="flex items-center gap-2 text-xs {validation.minLength ? 'text-green-600' : 'text-gray-600'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.minLength ? 'border-green-600 bg-green-600' : 'border-gray-300'} flex items-center justify-center">
										{#if validation.minLength}
											<svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
											</svg>
										{/if}
									</div>
									At least 8 characters
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasUpper ? 'text-green-600' : 'text-gray-600'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasUpper ? 'border-green-600 bg-green-600' : 'border-gray-300'} flex items-center justify-center">
										{#if validation.hasUpper}
											<svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
											</svg>
										{/if}
									</div>
									One uppercase letter
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasLower ? 'text-green-600' : 'text-gray-600'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasLower ? 'border-green-600 bg-green-600' : 'border-gray-300'} flex items-center justify-center">
										{#if validation.hasLower}
											<svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
											</svg>
										{/if}
									</div>
									One lowercase letter
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasNumber ? 'text-green-600' : 'text-gray-600'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasNumber ? 'border-green-600 bg-green-600' : 'border-gray-300'} flex items-center justify-center">
										{#if validation.hasNumber}
											<svg class="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
												<path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
											</svg>
										{/if}
									</div>
									One number
								</div>
							</div>
						</div>
					{/if}
				</div>

				<div>
					<label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
						Confirm Password
					</label>
					<div class="relative">
						<Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type={showConfirmPassword ? 'text' : 'password'}
							id="confirmPassword"
							name="confirm_password"
							bind:value={formData.confirmPassword}
							required
							disabled={loading}
							placeholder="Re-enter your password"
							class="w-full pl-10 pr-12 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:opacity-50"
						/>
						<button
							type="button"
							onclick={() => (showConfirmPassword = !showConfirmPassword)}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
						>
							{#if showConfirmPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
					{#if formData.confirmPassword && formData.password !== formData.confirmPassword}
						<p class="text-xs text-red-600 mt-1">Passwords do not match</p>
					{/if}
				</div>

				<button
					type="submit"
					disabled={loading || !validation.minLength || !validation.hasUpper || !validation.hasLower || !validation.hasNumber || formData.password !== formData.confirmPassword}
					class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
				>
					{loading ? 'Resetting...' : 'Reset Password'}
				</button>
			</form>
		</div>
	{:else}
		<!-- Success Message -->
		<div class="text-center">
			<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle2 class="w-8 h-8 text-green-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Password Reset Successful!</h1>
			<p class="text-gray-600 mb-8">
				Your password has been successfully reset. You can now sign in with your new password.
			</p>

			<a
				href="/login/"
				class="inline-block w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
			>
				Sign In
			</a>
		</div>
	{/if}
</div>
