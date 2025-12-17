<script lang="ts">
	import { Mail, ArrowLeft, CheckCircle2 } from '@lucide/svelte';
	import { getContext } from 'svelte';

	type AuthLayoutContext = {
		containerClass: string;
		mainClass: string;
	};

	const layout = getContext<AuthLayoutContext>('authLayout');
	layout.containerClass = 'max-w-lg';

	let email = $state('');
	let isSubmitted = $state(false);

	function handleSubmit(e: Event) {
		e.preventDefault();
		console.log('Sending reset link to:', email);
		// API call here
		isSubmitted = true;
	}

	function resendEmail() {
		console.log('Resending email to:', email);
		// API call here
	}
</script>

<svelte:head>
	<title>Forgot Password - PeelJobs Recruiter</title>
</svelte:head>

<div class="bg-white rounded-lg shadow-lg p-8">
	{#if !isSubmitted}
		<!-- Request Reset Form -->
		<div>
			<!-- Back Button -->
			<a
				href="/login/"
				class="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6"
			>
				<ArrowLeft class="w-4 h-4" />
				Back to login
			</a>

			<!-- Header -->
			<div class="mb-8">
				<h1 class="text-2xl font-bold text-gray-900">Forgot Password?</h1>
				<p class="text-gray-600 mt-2">
					No worries! Enter your email address and we'll send you a link to reset your password.
				</p>
			</div>

			<!-- Form -->
			<form onsubmit={handleSubmit} class="space-y-6">
				<div>
					<label for="email" class="block text-sm font-medium text-gray-700 mb-2">
						Email Address
					</label>
					<div class="relative">
						<Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
						<input
							type="email"
							id="email"
							bind:value={email}
							required
							placeholder="you@company.com"
							class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
						/>
					</div>
				</div>

				<button
					type="submit"
					class="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
				>
					Send Reset Link
				</button>
			</form>
		</div>
	{:else}
		<!-- Success Message -->
		<div class="text-center">
			<div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
				<CheckCircle2 class="w-8 h-8 text-green-600" />
			</div>

			<h1 class="text-2xl font-bold text-gray-900 mb-3">Check Your Email</h1>
			<p class="text-gray-600 mb-6">
				We've sent a password reset link to <strong class="text-gray-900">{email}</strong>
			</p>

			<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
				<p class="text-sm text-blue-800">
					Didn't receive the email? Check your spam folder or
					<button onclick={resendEmail} class="font-medium underline hover:no-underline">
						resend the link
					</button>
				</p>
			</div>

			<a
				href="/login/"
				class="inline-flex items-center gap-2 text-sm text-blue-600 hover:text-blue-700 font-medium"
			>
				<ArrowLeft class="w-4 h-4" />
				Back to login
			</a>
		</div>
	{/if}
</div>
