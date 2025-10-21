<script lang="ts">
	import { onMount } from 'svelte';
	import { CheckCircle2, XCircle, Loader2, Mail } from '@lucide/svelte';
	import { getContext } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { verifyEmail, resendVerification as apiResendVerification } from '$lib/api/auth';
	import { authStore } from '$lib/stores/auth';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let status = $state<'verifying' | 'success' | 'error' | 'expired'>('verifying');
	let email = $state('');
	let errorMessage = $state('');
	let resending = $state(false);

	onMount(async () => {
		// Get token and email from URL query params
		const token = $page.url.searchParams.get('token');
		email = $page.url.searchParams.get('email') || '';

		if (!token) {
			status = 'error';
			errorMessage = 'No verification token provided';
			return;
		}

		// Call API to verify email
		try {
			const response = await verifyEmail({ token });

			// Store user and tokens
			await authStore.login(response.user, response.access, response.refresh);

			status = 'success';

			// Redirect to dashboard after 2 seconds
			setTimeout(() => {
				goto('/dashboard/');
			}, 2000);
		} catch (err: any) {
			console.error('Email verification error:', err);

			// Check if token is expired
			if (err.message?.includes('expired') || err.message?.includes('invalid')) {
				status = 'expired';
				errorMessage = err.message;
			} else {
				status = 'error';
				errorMessage = err.message || 'Verification failed';
			}
		}
	});

	async function resendVerificationEmail() {
		if (!email) {
			alert('Please provide an email address');
			return;
		}

		resending = true;

		try {
			await apiResendVerification(email);
			alert('Verification email sent! Please check your inbox.');
		} catch (err: any) {
			alert(err.message || 'Failed to resend verification email');
		} finally {
			resending = false;
		}
	}
</script>

<svelte:head>
	<title>Verify Email - PeelJobs Recruiter</title>
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-8">
	{#if status === 'verifying'}
		<!-- Verifying State -->
		<div class="text-center">
			<div class="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<Loader2 class="w-8 h-8 text-blue-600 animate-spin" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Verifying Your Email</h1>
			<p class="text-gray-600">Please wait while we verify your email address...</p>
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
				<button
					onclick={resendVerificationEmail}
					disabled={resending}
					class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4"
				>
					{resending ? 'Sending...' : 'Resend Verification Email'}
				</button>
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
				<button
					onclick={resendVerificationEmail}
					disabled={resending}
					class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors mb-4"
				>
					{resending ? 'Sending...' : 'Resend Verification Email'}
				</button>
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
