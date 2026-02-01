<script lang="ts">
	import { untrack } from 'svelte';
	import { Mail, ArrowLeft, CheckCircle } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Button, Input, Card, FormField } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let email = $state(untrack(() => form?.email || ''));
	let loading = $state(false);

	let isSubmitted = $derived(form?.success || false);
	let error = $derived(form?.error || '');
</script>

<svelte:head>
	<title>Forgot Password - PeelJobs Recruiter</title>
	<meta name="description" content="Reset your PeelJobs employer account password." />
</svelte:head>

<Card padding="lg" class="shadow-lg">
	{#if !isSubmitted}
		<!-- Request Reset Form -->
		<div>
			<!-- Back Button -->
			<a
				href="/login/"
				class="inline-flex items-center gap-2 text-sm text-muted hover:text-black transition-colors mb-6"
			>
				<ArrowLeft class="w-4 h-4" />
				Back to login
			</a>

			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-2xl font-semibold text-black">Forgot Password?</h1>
				<p class="text-muted mt-2">
					No worries! Enter your email address and we'll send you a link to reset your password.
				</p>
			</div>

			<!-- Form -->
			<form method="POST" use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					loading = false;
					await update();
				};
			}} class="space-y-6">
				{#if error}
					<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm">
						{error}
					</div>
				{/if}

				<FormField label="Email Address">
					<Input
						type="email"
						id="email"
						name="email"
						bind:value={email}
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

				<Button type="submit" size="lg" {loading} class="w-full">
					{loading ? 'Sending...' : 'Send Reset Link'}
				</Button>
			</form>
		</div>
	{:else}
		<!-- Success Message -->
		<div class="text-center">
			<div class="w-16 h-16 bg-success-light rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle class="w-8 h-8 text-success" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Check Your Email</h1>
			<p class="text-muted mb-6">
				We've sent a password reset link to <strong class="text-black">{email}</strong>
			</p>

			<div class="bg-primary/5 border border-primary/20 rounded-lg p-4 mb-6">
				<div class="text-sm text-primary">
					Didn't receive the email? Check your spam folder or
					<form method="POST" class="inline" use:enhance>
						<input type="hidden" name="email" value={email} />
						<button type="submit" class="font-medium underline hover:no-underline">
							resend the link
						</button>
					</form>
				</div>
			</div>

			<a
				href="/login/"
				class="inline-flex items-center gap-2 text-sm text-primary hover:text-primary-hover font-medium transition-colors"
			>
				<ArrowLeft class="w-4 h-4" />
				Back to login
			</a>
		</div>
	{/if}
</Card>
