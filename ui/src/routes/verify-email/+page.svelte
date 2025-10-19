<script>
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Mail, CheckCircle, XCircle, Loader, RefreshCw } from '@lucide/svelte';

  let verificationStatus = 'verifying'; // 'verifying', 'success', 'error', 'expired'
  let email = '';
  let isResending = false;
  let resendSuccess = false;
  let errorMessage = '';

  // Get token from URL query params
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
      // TODO: Replace with actual API call
      console.log('Verifying email with token:', token);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Simulate different outcomes for testing
      // In production, this would be based on actual API response
      const random = Math.random();
      if (random > 0.8) {
        verificationStatus = 'expired';
        errorMessage = 'This verification link has expired';
      } else if (random > 0.9) {
        verificationStatus = 'error';
        errorMessage = 'Invalid verification token';
      } else {
        verificationStatus = 'success';

        // Redirect to dashboard after 3 seconds
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
      // TODO: Replace with actual API call
      console.log('Resending verification email to:', email);

      // Simulate API call
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
  <title>Verify Email - HirePulse.in</title>
  <meta name="description" content="Verify your HirePulse.in email address" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
  <div class="max-w-md w-full">
    <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-gray-100">

      {#if verificationStatus === 'verifying'}
        <!-- Verifying -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-blue-100 rounded-full animate-pulse">
              <Loader class="text-blue-600 animate-spin" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Verifying Your Email
          </h2>

          <p class="text-gray-600 mb-6">
            Please wait while we verify your email address...
          </p>

          <div class="flex justify-center">
            <div class="animate-pulse flex space-x-2">
              <div class="w-2 h-2 bg-blue-600 rounded-full"></div>
              <div class="w-2 h-2 bg-blue-600 rounded-full animation-delay-200"></div>
              <div class="w-2 h-2 bg-blue-600 rounded-full animation-delay-400"></div>
            </div>
          </div>
        </div>

      {:else if verificationStatus === 'success'}
        <!-- Success -->
        <div class="text-center">
          <div class="flex justify-center mb-6 animate-bounce-once">
            <div class="p-4 bg-green-100 rounded-full">
              <CheckCircle class="text-green-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Email Verified Successfully!
          </h2>

          <p class="text-gray-600 mb-6">
            Your email has been verified. You can now access all features of HirePulse.in.
          </p>

          <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p class="text-sm text-gray-700 mb-2">
              <strong>Welcome to HirePulse.in!</strong>
            </p>
            <p class="text-sm text-gray-600">
              Redirecting you to your dashboard in a few seconds...
            </p>
          </div>

          <a
            href="/jobseeker-dashboard"
            class="inline-block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg text-center"
          >
            Continue to Dashboard
          </a>
        </div>

      {:else if verificationStatus === 'expired'}
        <!-- Expired Link -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-yellow-100 rounded-full">
              <Mail class="text-yellow-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Link Expired
          </h2>

          <p class="text-gray-600 mb-6">
            This verification link has expired. Don't worry, we can send you a new one!
          </p>

          {#if email}
            <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
              <p class="text-sm text-gray-700 mb-1">
                Sending verification email to:
              </p>
              <p class="text-blue-600 font-medium">
                {email}
              </p>
            </div>
          {/if}

          {#if resendSuccess}
            <div class="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
              <p class="text-sm text-green-700">
                <CheckCircle class="inline mr-1" size={16} />
                Verification email sent! Please check your inbox.
              </p>
            </div>
          {/if}

          {#if errorMessage}
            <div class="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p class="text-sm text-red-600">{errorMessage}</p>
            </div>
          {/if}

          <button
            type="button"
            onclick={handleResend}
            disabled={isResending || !email}
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mb-4"
          >
            {#if isResending}
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            {:else}
              <RefreshCw size={20} class="mr-2" />
              Resend Verification Email
            {/if}
          </button>

          <a href="/login" class="text-gray-600 hover:text-blue-600 font-medium text-sm">
            Back to Sign In
          </a>
        </div>

      {:else}
        <!-- Error -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-red-100 rounded-full">
              <XCircle class="text-red-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Verification Failed
          </h2>

          <p class="text-gray-600 mb-2">
            We couldn't verify your email address.
          </p>

          {#if errorMessage}
            <div class="bg-red-50 border border-red-200 rounded-lg p-3 mb-6">
              <p class="text-sm text-red-600">{errorMessage}</p>
            </div>
          {/if}

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p class="text-sm text-gray-700 mb-2">
              <strong>What you can do:</strong>
            </p>
            <ul class="text-sm text-gray-600 space-y-1 text-left list-disc list-inside">
              <li>Request a new verification email</li>
              <li>Check if you already verified your email</li>
              <li>Contact support if the problem persists</li>
            </ul>
          </div>

          {#if email}
            <button
              type="button"
              onclick={handleResend}
              disabled={isResending}
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center mb-3"
            >
              {#if isResending}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              {:else}
                <RefreshCw size={20} class="mr-2" />
                Request New Verification Email
              {/if}
            </button>
          {/if}

          <div class="space-y-2">
            <a
              href="/login"
              class="block text-blue-600 hover:text-blue-700 font-medium text-sm"
            >
              Try Signing In
            </a>
            <a
              href="/contact"
              class="block text-gray-600 hover:text-blue-600 font-medium text-sm"
            >
              Contact Support
            </a>
          </div>
        </div>
      {/if}

    </div>
  </div>
</div>

<style>
  @keyframes bounce-once {
    0%, 100% {
      transform: translateY(0);
    }
    50% {
      transform: translateY(-10px);
    }
  }

  .animate-bounce-once {
    animation: bounce-once 0.6s ease-out;
  }

  .animation-delay-200 {
    animation-delay: 200ms;
  }

  .animation-delay-400 {
    animation-delay: 400ms;
  }
</style>
