<script lang="ts">
	import { CheckCircle2, XCircle, Mail } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { enhance } from '$app/forms';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	let { data, form } = $props();

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let resending = $state(false);

	// Get status and data from server load
	let status = $derived(data.status);
	let email = $derived(data.email);
	let errorMessage = $derived(data.errorMessage);

	// Show success message from form action
	let resendSuccess = $derived(form?.success || false);
	let resendError = $derived(form?.error || '');
</script>

<svelte:head>
	<title>Verify Email - PeelJobs Recruiter</title>
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-8">
	{#if status === 'waiting'}
		<!-- Waiting for verification State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<Mail class="w-8 h-8 text-blue-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Check Your Email</h1>
			<p class="text-gray-600 mb-6">
				We've sent a verification link to {#if email}<strong class="text-gray-900">{email}</strong>{:else}your email address{/if}.
				Please click the link to verify your account.
			</p>

			{#if resendSuccess}
				<div class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-lg text-sm mb-4">
					Verification email sent! Please check your inbox.
				</div>
			{/if}

			{#if resendError}
				<div class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm mb-4">
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
					<button
						type="submit"
						disabled={resending}
						class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4"
					>
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-gray-600 hover:text-gray-900"
			>
				Back to login
			</a>
		</div>
	{:else if status === 'success'}
		<!-- Success State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle2 class="w-8 h-8 text-green-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Email Verified!</h1>
			<p class="text-gray-600 mb-8">
				Your email address has been successfully verified. You can now access all features of your employer account.
			</p>

			<a
				href="/onboarding/"
				class="inline-block w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors mb-4"
			>
				Complete Your Profile
			</a>

			<a
				href="/dashboard/"
				class="inline-block text-sm text-gray-600 hover:text-gray-900"
			>
				Skip for now and go to dashboard
			</a>
		</div>
	{:else if status === 'expired'}
		<!-- Expired Link State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<Mail class="w-8 h-8 text-orange-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Verification Link Expired</h1>
			<p class="text-gray-600 mb-8">
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
					<button
						type="submit"
						disabled={resending}
						class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4"
					>
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-gray-600 hover:text-gray-900"
			>
				Back to login
			</a>
		</div>
	{:else}
		<!-- Error State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<XCircle class="w-8 h-8 text-red-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Verification Failed</h1>
			<p class="text-gray-600 mb-8">
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
					<button
						type="submit"
						disabled={resending}
						class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4"
					>
						{resending ? 'Sending...' : 'Resend Verification Email'}
					</button>
				</form>
			{/if}

			<a
				href="/login/"
				class="inline-block text-sm text-gray-600 hover:text-gray-900"
			>
				Back to login
			</a>
		</div>
	{/if}
</div>
