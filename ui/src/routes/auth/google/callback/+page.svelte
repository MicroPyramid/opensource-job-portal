<script lang="ts">
	import { onMount } from 'svelte';
	import { goto } from '$app/navigation';
	import { page } from '$app/stores';
	import { Loader2, AlertCircle, CheckCircle2 } from '@lucide/svelte';
	import { googleAuthCallback } from '$lib/api/auth';
	import { authStore } from '$lib/stores/auth';

	let status: 'loading' | 'success' | 'error' = 'loading';
	let errorMessage = '';
	let redirectPath = '/';

	onMount(async () => {
		const code = $page.url.searchParams.get('code');
		const error = $page.url.searchParams.get('error');

		// Handle OAuth errors from Google
		if (error) {
			status = 'error';
			errorMessage = getOAuthErrorMessage(error);
			setTimeout(() => {
				goto('/login?error=' + error);
			}, 3000);
			return;
		}

		// No authorization code
		if (!code) {
			status = 'error';
			errorMessage = 'No authorization code received from Google.';
			setTimeout(() => {
				goto('/login?error=no_code');
			}, 3000);
			return;
		}

		// Exchange code for tokens
		try {
			const redirectUri = window.location.origin + '/auth/google/callback';

			const response = await googleAuthCallback(code, redirectUri);

			// Login user with tokens
			authStore.login(response.user, response.access, response.refresh);

			status = 'success';
			redirectPath = response.redirect_to || '/';

			// Show success message briefly then redirect
			setTimeout(() => {
				goto(redirectPath);
			}, 1500);
		} catch (err) {
			status = 'error';
			errorMessage = err instanceof Error ? err.message : 'Authentication failed. Please try again.';

			setTimeout(() => {
				goto('/login?error=auth_failed');
			}, 3000);
		}
	});

	function getOAuthErrorMessage(error: string): string {
		const errorMessages: Record<string, string> = {
			access_denied: 'You denied access. Please try again and authorize the application.',
			invalid_request: 'Invalid request. Please try again.',
			unauthorized_client: 'App is not authorized. Please contact support.',
			unsupported_response_type: 'Configuration error. Please contact support.',
			invalid_scope: 'Invalid permissions requested. Please contact support.',
			server_error: 'Google server error. Please try again later.',
			temporarily_unavailable: 'Service temporarily unavailable. Please try again later.'
		};

		return errorMessages[error] || 'Authentication error occurred. Please try again.';
	}
</script>

<svelte:head>
	<title>Authenticating - PeelJobs</title>
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
	<div class="max-w-md w-full">
		<div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
			{#if status === 'loading'}
				<!-- Loading State -->
				<div class="text-center">
					<div class="inline-flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-6">
						<Loader2 class="w-8 h-8 text-blue-600 animate-spin" />
					</div>
					<h2 class="text-2xl font-semibold text-gray-900 mb-2">Authenticating...</h2>
					<p class="text-gray-600">
						Please wait while we securely log you in with Google.
					</p>
					<div class="mt-6 flex justify-center">
						<div class="flex space-x-2">
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 0ms"></div>
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 150ms"></div>
							<div class="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style="animation-delay: 300ms"></div>
						</div>
					</div>
				</div>
			{:else if status === 'success'}
				<!-- Success State -->
				<div class="text-center">
					<div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-6">
						<CheckCircle2 class="w-8 h-8 text-green-600" />
					</div>
					<h2 class="text-2xl font-semibold text-gray-900 mb-2">Success!</h2>
					<p class="text-gray-600">
						You've been authenticated successfully.
					</p>
					<p class="text-sm text-gray-500 mt-4">
						Redirecting you to {redirectPath}...
					</p>
				</div>
			{:else}
				<!-- Error State -->
				<div class="text-center">
					<div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 rounded-full mb-6">
						<AlertCircle class="w-8 h-8 text-red-600" />
					</div>
					<h2 class="text-2xl font-semibold text-gray-900 mb-2">Authentication Failed</h2>
					<p class="text-gray-600 mb-4">
						{errorMessage}
					</p>
					<p class="text-sm text-gray-500">
						Redirecting you back to login page...
					</p>
				</div>
			{/if}
		</div>

		<!-- Security Note -->
		<div class="mt-6 text-center text-sm text-gray-500">
			<p>🔒 Secured with enterprise-grade encryption</p>
		</div>
	</div>
</div>

<style>
	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: translateY(20px);
		}
		to {
			opacity: 1;
			transform: translateY(0);
		}
	}

	.bg-white {
		animation: fadeIn 0.6s ease-out;
	}
</style>
