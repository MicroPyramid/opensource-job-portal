<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Mail, CheckCircle, XCircle, Loader2, RefreshCw, Clock } from '@lucide/svelte';

  let verificationStatus = 'verifying';
  let email = '';
  let isResending = false;
  let resendSuccess = false;
  let errorMessage = '';

  $: token = $page.url.searchParams.get('token');
  $: email = $page.url.searchParams.get('email') || '';

  onMount(() => {
    if (token) {
      verifyEmail(token);
    } else {
      verificationStatus = 'error';
      errorMessage = 'No verification token provided';
    }
  });

  /**
   * @param {string} token
   */
  async function verifyEmail(token) {
    try {
      console.log('Verifying email with token:', token);
      await new Promise(resolve => setTimeout(resolve, 2000));

      const random = Math.random();
      if (random > 0.8) {
        verificationStatus = 'expired';
        errorMessage = 'This verification link has expired';
      } else if (random > 0.9) {
        verificationStatus = 'error';
        errorMessage = 'Invalid verification token';
      } else {
        verificationStatus = 'success';

        setTimeout(() => {
          goto('/jobseeker-dashboard');
        }, 3000);
      }
    } catch (error) {
      console.error('Email verification error:', error);
      verificationStatus = 'error';
      errorMessage = 'Failed to verify email. Please try again.';
    }
  }

  async function handleResend() {
    if (!email) {
      errorMessage = 'Email address not found. Please register again.';
      return;
    }

    isResending = true;
    resendSuccess = false;

    try {
      console.log('Resending verification email to:', email);
      await new Promise(resolve => setTimeout(resolve, 1500));
      resendSuccess = true;
      errorMessage = '';
    } catch (error) {
      console.error('Resend verification error:', error);
      errorMessage = 'Failed to resend verification email. Please try again.';
    } finally {
      isResending = false;
    }
  }
</script>

<svelte:head>
  <title>Verify Email - PeelJobs</title>
  <meta name="description" content="Verify your PeelJobs email address" />
</svelte:head>

<div class="min-h-screen bg-surface-50 flex items-center justify-center p-6">
  <div class="w-full max-w-md">
    <!-- Logo -->
    <div class="text-center mb-8 animate-fade-in-down" style="opacity: 0; animation-fill-mode: forwards;">
      <a href="/" class="inline-flex items-center gap-3">
        <div class="w-12 h-12 rounded-2xl bg-primary-600 flex items-center justify-center">
          <span class="text-xl font-bold text-white">P</span>
        </div>
        <span class="text-2xl font-bold text-gray-900">PeelJobs</span>
      </a>
    </div>

    <!-- Card -->
    <div class="bg-white rounded-2xl p-8 elevation-1 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;">
      {#if verificationStatus === 'verifying'}
        <!-- Verifying State -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-6">
            <Loader2 size={32} class="text-primary-600 animate-spin" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-3">
            Verifying Your Email
          </h2>

          <p class="text-gray-600 mb-6">
            Please wait while we verify your email address...
          </p>

          <div class="flex justify-center gap-1">
            {#each [0, 1, 2] as i}
              <div
                class="w-2 h-2 bg-primary-600 rounded-full animate-pulse"
                style="animation-delay: {i * 200}ms"
              ></div>
            {/each}
          </div>
        </div>

      {:else if verificationStatus === 'success'}
        <!-- Success State -->
        <div class="text-center animate-scale-in">
          <div class="w-16 h-16 rounded-full bg-success-500/10 flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={32} class="text-success-600" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-3">
            Email Verified!
          </h2>

          <p class="text-gray-600 mb-6">
            Your email has been verified. You can now access all features of PeelJobs.
          </p>

          <div class="bg-success-500/10 rounded-xl p-4 mb-6">
            <p class="text-sm font-medium text-success-700 mb-1">
              Welcome to PeelJobs!
            </p>
            <p class="text-sm text-gray-600">
              Redirecting you to your dashboard...
            </p>
          </div>

          <a
            href="/jobseeker-dashboard/"
            class="inline-block w-full px-5 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-all elevation-1 hover:elevation-2 text-center"
          >
            Continue to Dashboard
          </a>
        </div>

      {:else if verificationStatus === 'expired'}
        <!-- Expired State -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-warning-500/10 flex items-center justify-center mx-auto mb-6">
            <Clock size={32} class="text-warning-600" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-3">
            Link Expired
          </h2>

          <p class="text-gray-600 mb-6">
            This verification link has expired. Don't worry, we can send you a new one!
          </p>

          {#if email}
            <div class="bg-primary-50 rounded-xl p-4 mb-6 text-left">
              <p class="text-sm text-gray-700 mb-1">
                Sending verification email to:
              </p>
              <p class="text-primary-600 font-medium">
                {email}
              </p>
            </div>
          {/if}

          {#if resendSuccess}
            <div class="p-4 bg-success-500/10 border border-success-500/20 rounded-xl mb-4 animate-scale-in">
              <div class="flex items-center gap-2 text-success-700">
                <CheckCircle size={16} />
                <span class="text-sm font-medium">Verification email sent! Check your inbox.</span>
              </div>
            </div>
          {/if}

          {#if errorMessage && !resendSuccess}
            <div class="p-4 bg-error-500/10 border border-error-500/20 rounded-xl mb-4">
              <p class="text-sm text-error-600">{errorMessage}</p>
            </div>
          {/if}

          <button
            type="button"
            onclick={handleResend}
            disabled={isResending || !email}
            class="w-full px-5 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-all elevation-1 hover:elevation-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mb-4"
          >
            {#if isResending}
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            {:else}
              <RefreshCw size={18} />
              Resend Verification Email
            {/if}
          </button>

          <a href="/login/" class="text-gray-600 hover:text-primary-600 font-medium text-sm transition-colors">
            Back to Sign In
          </a>
        </div>

      {:else}
        <!-- Error State -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-error-500/10 flex items-center justify-center mx-auto mb-6">
            <XCircle size={32} class="text-error-600" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-3">
            Verification Failed
          </h2>

          <p class="text-gray-600 mb-2">
            We couldn't verify your email address.
          </p>

          {#if errorMessage}
            <div class="p-4 bg-error-500/10 border border-error-500/20 rounded-xl mb-6">
              <p class="text-sm text-error-600">{errorMessage}</p>
            </div>
          {/if}

          <div class="bg-primary-50 rounded-xl p-4 mb-6 text-left">
            <p class="text-sm font-medium text-gray-900 mb-2">
              What you can do:
            </p>
            <ul class="text-sm text-gray-600 space-y-1">
              <li class="flex items-start gap-2">
                <span class="text-primary-600">•</span>
                Request a new verification email
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary-600">•</span>
                Check if you already verified your email
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary-600">•</span>
                Contact support if the problem persists
              </li>
            </ul>
          </div>

          {#if resendSuccess}
            <div class="p-4 bg-success-500/10 border border-success-500/20 rounded-xl mb-4 animate-scale-in">
              <div class="flex items-center gap-2 text-success-700">
                <CheckCircle size={16} />
                <span class="text-sm font-medium">Verification email sent! Check your inbox.</span>
              </div>
            </div>
          {/if}

          {#if email}
            <button
              type="button"
              onclick={handleResend}
              disabled={isResending}
              class="w-full px-5 py-3 border border-primary-600 text-primary-600 font-medium rounded-full hover:bg-primary-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 mb-4"
            >
              {#if isResending}
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              {:else}
                <RefreshCw size={18} />
                Request New Verification Email
              {/if}
            </button>
          {/if}

          <div class="flex flex-col gap-2">
            <a
              href="/login/"
              class="text-primary-600 hover:text-primary-700 font-medium text-sm transition-colors"
            >
              Try Signing In
            </a>
            <a
              href="/contact/"
              class="text-gray-600 hover:text-primary-600 font-medium text-sm transition-colors"
            >
              Contact Support
            </a>
          </div>
        </div>
      {/if}
    </div>
  </div>
</div>
