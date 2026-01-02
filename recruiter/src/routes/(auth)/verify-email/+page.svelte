<script lang="ts">
	import { CheckCircle, XCircle, Mail } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';
	import { Button, Card } from '$lib/components/ui';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let resending = $state(false);

	let status = $derived(data.status);
	let email = $derived(data.email);
	let errorMessage = $derived(data.errorMessage);

	let resendSuccess = $derived(form?.success || false);
	let resendError = $derived(form?.error || '');
</script>

<svelte:head>
	<title>Verify Email - PeelJobs Recruiter</title>
	<meta name="description" content="Verify your PeelJobs employer account email address." />
</svelte:head>

<Card padding="lg" class="shadow-lg">
	{#if status === 'waiting'}
		<!-- Waiting for verification State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
				<Mail class="w-8 h-8 text-primary" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Check Your Email</h1>
			<p class="text-muted mb-6">
				We've sent a verification link to {#if email}<strong class="text-black">{email}</strong>{:else}your email address{/if}.
				Please click the link to verify your account.
			</p>

			{#if resendSuccess}
				<div class="bg-success-light border border-success/20 text-success px-4 py-3 rounded-lg text-sm mb-4">
					Verification email sent! Please check your inbox.
				</div>
			{/if}

			{#if resendError}
				<div class="bg-error-light border border-error/20 text-error px-4 py-3 rounded-lg text-sm mb-4">
					{resendError}
				</div>
			{/if}

			{#if email}
				<form method="POST" action="?/resend" use:enhance={() => {
					resending = true;
					return async ({ update }) => {
						resending = false;
						await update();
					};
				}}>
					<input type="hidden" name="email" value={email} />
					<Button type="submit" size="lg" loading={resending} class="w-full mb-4">
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</Button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-muted hover:text-black transition-colors"
			>
				Back to login
			</a>
		</div>
	{:else if status === 'success'}
		<!-- Success State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-success-light rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle class="w-8 h-8 text-success" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Email Verified!</h1>
			<p class="text-muted mb-8">
				Your email address has been successfully verified. You can now access all features of your employer account.
			</p>

			<Button size="lg" class="w-full mb-4" onclick={() => window.location.href = '/onboarding/'}>
				Complete Your Profile
			</Button>

			<a
				href="/dashboard/"
				class="inline-block text-sm text-muted hover:text-black transition-colors"
			>
				Skip for now and go to dashboard
			</a>
		</div>
	{:else if status === 'expired'}
		<!-- Expired Link State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-warning-light rounded-full flex items-center justify-center mx-auto mb-6">
				<Mail class="w-8 h-8 text-warning" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Verification Link Expired</h1>
			<p class="text-muted mb-8">
				{errorMessage || 'This verification link has expired. Please request a new verification email.'}
			</p>

			{#if email}
				<form method="POST" action="?/resend" use:enhance={() => {
					resending = true;
					return async ({ update }) => {
						resending = false;
						await update();
					};
				}}>
					<input type="hidden" name="email" value={email} />
					<Button type="submit" size="lg" loading={resending} class="w-full mb-4">
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</Button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-muted hover:text-black transition-colors"
			>
				Back to login
			</a>
		</div>
	{:else}
		<!-- Error State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-error-light rounded-full flex items-center justify-center mx-auto mb-6">
				<XCircle class="w-8 h-8 text-error" />
			</div>

			<h1 class="text-2xl font-semibold text-black mb-3">Verification Failed</h1>
			<p class="text-muted mb-8">
				{errorMessage || "We couldn't verify your email address. The verification link may be invalid or has already been used."}
			</p>

			{#if email}
				<form method="POST" action="?/resend" use:enhance={() => {
					resending = true;
					return async ({ update }) => {
						resending = false;
						await update();
					};
				}}>
					<input type="hidden" name="email" value={email} />
					<Button type="submit" size="lg" loading={resending} class="w-full mb-4">
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</Button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-muted hover:text-black transition-colors"
			>
				Back to login
			</a>
		</div>
	{/if}
</Card>
