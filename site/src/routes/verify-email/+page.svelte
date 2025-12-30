<script>
  import { goto } from '$app/navigation';
  import { Mail, CheckCircle, XCircle, Loader2, RefreshCw, Clock } from '@lucide/svelte';
  import { enhance } from '$app/forms';

  /** @type {{ data?: { status?: string; message?: string; email?: string }; form?: { success?: boolean; message?: string } }} */
  let { data, form } = $props();

  let verificationStatus = $state(data?.status || 'pending');
  let email = $state(data?.email || '');
  let isResending = $state(false);
  let resendSuccess = $state(false);
  let errorMessage = $state(data?.message || '');

  // Update state when data changes
  $effect(() => {
    if (data?.status) {
      verificationStatus = data.status;
    }
    if (data?.email) {
      email = data.email;
    }
    if (data?.message && data.status !== 'success') {
      errorMessage = data.message;
    }
  });

  // Handle resend form result
  $effect(() => {
    if (form?.success) {
      resendSuccess = true;
      errorMessage = '';
    } else if (form?.message) {
      errorMessage = form.message;
    }
    isResending = false;
  });

  // Redirect on success after delay
  $effect(() => {
    if (verificationStatus === 'success') {
      setTimeout(() => {
        goto('/');
      }, 3000);
    }
  });
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

      {:else if verificationStatus === 'pending'}
        <!-- Pending - Waiting for user to check email -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-primary-50 flex items-center justify-center mx-auto mb-6">
            <Mail size={32} class="text-primary-600" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-3">
            Check Your Email
          </h2>

          <p class="text-gray-600 mb-6">
            We've sent a verification link to your email address. Please click the link to verify your account.
          </p>

          {#if email}
            <div class="bg-primary-50 rounded-xl p-4 mb-6">
              <p class="text-sm text-gray-700 mb-1">
                Verification email sent to:
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

          {#if errorMessage}
            <div class="p-4 bg-error-500/10 border border-error-500/20 rounded-xl mb-4">
              <p class="text-sm text-error-600">{errorMessage}</p>
            </div>
          {/if}

          <form
            method="POST"
            action="?/resend"
            use:enhance={() => {
              isResending = true;
              resendSuccess = false;
              return async ({ update }) => {
                await update();
              };
            }}
          >
            <input type="hidden" name="email" value={email} />
            <button
              type="submit"
              disabled={isResending || !email}
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
                Resend Verification Email
              {/if}
            </button>
          </form>

          <p class="text-sm text-gray-500">
            Didn't receive the email? Check your spam folder or request a new verification link above.
          </p>
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
              Redirecting you to home page...
            </p>
          </div>

          <a
            href="/"
            class="inline-block w-full px-5 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-all elevation-1 hover:elevation-2 text-center"
          >
            Go to Home
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

          <form
            method="POST"
            action="?/resend"
            use:enhance={() => {
              isResending = true;
              resendSuccess = false;
              return async ({ update }) => {
                await update();
              };
            }}
          >
            <input type="hidden" name="email" value={email} />
            <button
              type="submit"
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
          </form>

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
            <form
              method="POST"
              action="?/resend"
              use:enhance={() => {
                isResending = true;
                resendSuccess = false;
                return async ({ update }) => {
                  await update();
                };
              }}
            >
              <input type="hidden" name="email" value={email} />
              <button
                type="submit"
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
            </form>
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
