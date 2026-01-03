<script lang="ts">
	import { Lock, Eye, EyeOff, CheckCircle } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Button, Input, Card, FormField } from '$lib/components/ui';

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
	let isValid = $derived(validation.minLength && validation.hasUpper && validation.hasLower && validation.hasNumber && formData.password === formData.confirmPassword);
</script>

<svelte:head>
	<title>Reset Password - PeelJobs Recruiter</title>
	<meta name="description" content="Create a new password for your PeelJobs employer account." />
</svelte:head>

<Card padding="lg" class="shadow-lg">
	{#if !isSubmitted}
		<!-- Reset Password Form -->
		<div>
			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-2xl font-semibold text-black">Reset Password</h1>
				<p class="text-muted mt-2">Create a new password for your account</p>
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
					<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm">
						{error}
					</div>
				{/if}

				<FormField label="New Password">
					<div class="relative">
						<Input
							type={showPassword ? 'text' : 'password'}
							id="password"
							name="password"
							bind:value={formData.password}
							required
							disabled={loading}
							placeholder="Create a strong password"
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
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors"
							aria-label={showPassword ? 'Hide password' : 'Show password'}
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
							<p class="text-xs font-medium text-black">Password must contain:</p>
							<div class="space-y-1">
								<div class="flex items-center gap-2 text-xs {validation.minLength ? 'text-success' : 'text-muted'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.minLength ? 'border-success bg-success' : 'border-border'} flex items-center justify-center">
										{#if validation.minLength}
											<CheckCircle class="w-3 h-3 text-white" />
										{/if}
									</div>
									At least 8 characters
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasUpper ? 'text-success' : 'text-muted'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasUpper ? 'border-success bg-success' : 'border-border'} flex items-center justify-center">
										{#if validation.hasUpper}
											<CheckCircle class="w-3 h-3 text-white" />
										{/if}
									</div>
									One uppercase letter
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasLower ? 'text-success' : 'text-muted'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasLower ? 'border-success bg-success' : 'border-border'} flex items-center justify-center">
										{#if validation.hasLower}
											<CheckCircle class="w-3 h-3 text-white" />
										{/if}
									</div>
									One lowercase letter
								</div>
								<div class="flex items-center gap-2 text-xs {validation.hasNumber ? 'text-success' : 'text-muted'}">
									<div class="w-4 h-4 rounded-full border-2 {validation.hasNumber ? 'border-success bg-success' : 'border-border'} flex items-center justify-center">
										{#if validation.hasNumber}
											<CheckCircle class="w-3 h-3 text-white" />
										{/if}
									</div>
									One number
								</div>
							</div>
						</div>
					{/if}
				</FormField>

				<FormField label="Confirm Password" error={formData.confirmPassword && formData.password !== formData.confirmPassword ? 'Passwords do not match' : undefined}>
					<div class="relative">
						<Input
							type={showConfirmPassword ? 'text' : 'password'}
							id="confirmPassword"
							name="confirm_password"
							bind:value={formData.confirmPassword}
							required
							disabled={loading}
							placeholder="Re-enter your password"
							size="lg"
							error={formData.confirmPassword && formData.password !== formData.confirmPassword}
							class="pr-12"
						>
							{#snippet iconLeft()}
								<Lock class="w-5 h-5" />
							{/snippet}
						</Input>
						<button
							type="button"
							onclick={() => (showConfirmPassword = !showConfirmPassword)}
							class="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-black transition-colors"
							aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
						>
							{#if showConfirmPassword}
								<EyeOff class="w-5 h-5" />
							{:else}
								<Eye class="w-5 h-5" />
							{/if}
						</button>
					</div>
				</FormField>

				<Button type="submit" size="lg" {loading} disabled={loading || !isValid} class="w-full">
					{loading ? 'Resetting...' : 'Reset Password'}
				</Button>
			</form>
		</div>
	{:else}
		<!-- Success Message -->
		<div class="text-center">
			<div class="w-16 h-16 bg-success-light rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle class="w-8 h-8 text-success" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Password Reset Successful!</h1>
			<p class="text-muted mb-8">
				Your password has been successfully reset. You can now sign in with your new password.
			</p>

			<Button size="lg" class="w-full" onclick={() => window.location.href = '/login/'}>
				Sign In
			</Button>
		</div>
	{/if}
</Card>
