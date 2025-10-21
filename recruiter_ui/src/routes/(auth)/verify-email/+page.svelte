<script lang="ts">
	import { onMount } from 'svelte';
	import { CheckCircle2, XCircle, Loader2, Mail } from '@lucide/svelte';

	let status = $state<'verifying' | 'success' | 'error' | 'expired'>('verifying');
	let email = $state('user@company.com'); // This would come from the verification token

	onMount(() => {
		// Simulate API call to verify email with token from URL
		setTimeout(() => {
			// For demo purposes, randomly show success or error
			const token = new URLSearchParams(window.location.search).get('token');

			if (token) {
				// Simulate verification
				console.log('Verifying token:', token);
				// API call here
				status = 'success'; // or 'error' / 'expired'
			} else {
				status = 'error';
			}
		}, 2000);
	});

	function resendVerification() {
		console.log('Resending verification email to:', email);
		status = 'verifying';
		// API call here
		setTimeout(() => {
			alert('Verification email sent! Check your inbox.');
			status = 'error'; // Go back to waiting state
		}, 1500);
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
				This verification link has expired. Please request a new verification email.
			</p>

			<button
				onclick={resendVerification}
				class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors mb-4"
			>
				Resend Verification Email
			</button>

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
				We couldn't verify your email address. The verification link may be invalid or has already been used.
			</p>

			<button
				onclick={resendVerification}
				class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors mb-4"
			>
				Resend Verification Email
			</button>

			<a
				href="/login/"
				class="inline-block text-sm text-gray-600 hover:text-gray-900"
			>
				Back to login
			</a>
		</div>
	{/if}
</div>
