<script>
  import { Mail, ArrowLeft, CheckCircle, KeyRound } from '@lucide/svelte';

  let email = '';
  /** @type {Record<string, string>} */
  let errors = {};
  let isLoading = false;
  let emailSent = false;

  /**
   * @param {string} email
   */
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  }

  async function handleSubmit() {
    errors = {};

    if (!email.trim()) {
      errors.email = 'Email is required';
      return;
    }

    if (!validateEmail(email)) {
      errors.email = 'Please enter a valid email address';
      return;
    }

    isLoading = true;

    try {
      console.log('Password reset requested for:', email);
      await new Promise(resolve => setTimeout(resolve, 1500));
      emailSent = true;
    } catch (error) {
      console.error('Password reset error:', error);
      errors.submit = 'Failed to send reset email. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function handleResend() {
    emailSent = false;
    email = '';
    errors = {};
  }
</script>

<svelte:head>
  <title>Forgot Password - PeelJobs</title>
  <meta name="description" content="Reset your PeelJobs account password" />
</svelte:head>

<div class="min-h-screen bg-surface flex items-center justify-center p-6">
  <div class="w-full max-w-md">
    <!-- Logo -->
    <div class="text-center mb-8 animate-fade-in-down" style="opacity: 0; animation-fill-mode: forwards;">
      <a href="/" class="inline-flex items-center gap-3">
        <div class="w-12 h-12 rounded-lg bg-primary flex items-center justify-center">
          <span class="text-xl font-semibold text-white">P</span>
        </div>
        <span class="text-2xl font-semibold text-black">PeelJobs</span>
      </a>
    </div>

    <!-- Card -->
    <div class="bg-white rounded-lg p-8 shadow-sm animate-fade-in-up" style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;">
      {#if !emailSent}
        <!-- Request Reset Form -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <KeyRound size={32} class="text-primary" />
          </div>
          <h1 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-2">
            Forgot Password?
          </h1>
          <p class="text-muted">
            No worries! Enter your email and we'll send you reset instructions.
          </p>
        </div>

        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
          <div>
            <label for="email" class="block text-sm font-medium text-muted mb-2">
              Email Address
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Mail size={18} class="text-muted" />
              </span>
              <input
                id="email"
                type="email"
                bind:value={email}
                placeholder="you@example.com"
                class="w-full pl-11 pr-4 py-3 border rounded-lg bg-surface text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.email ? 'border-error' : 'border-border'}"
                disabled={isLoading}
              />
            </div>
            {#if errors.email}
              <p class="mt-1.5 text-sm text-error">{errors.email}</p>
            {/if}
          </div>

          {#if errors.submit}
            <div class="p-4 bg-error-light border border-error/20 rounded-lg">
              <p class="text-sm text-error">{errors.submit}</p>
            </div>
          {/if}

          <button
            type="submit"
            disabled={isLoading}
            class="w-full px-5 py-3.5 bg-primary hover:bg-primary-hover text-white font-medium rounded-full transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {#if isLoading}
              <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Sending...
            {:else}
              Send Reset Link
            {/if}
          </button>
        </form>

        <div class="mt-6 text-center">
          <a href="/login/" class="inline-flex items-center gap-2 text-primary hover:text-primary font-medium text-sm transition-colors">
            <ArrowLeft size={16} />
            Back to Sign In
          </a>
        </div>

      {:else}
        <!-- Success State -->
        <div class="text-center animate-scale-in">
          <div class="w-16 h-16 rounded-full bg-success-light flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={32} class="text-success" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-3">
            Check Your Email
          </h2>

          <p class="text-muted mb-2">
            We've sent password reset instructions to
          </p>
          <p class="text-primary font-medium mb-6">
            {email}
          </p>

          <div class="bg-primary/10 rounded-xl p-4 mb-6 text-left">
            <p class="text-sm font-medium text-black mb-2">
              Didn't receive the email?
            </p>
            <ul class="text-sm text-muted space-y-1">
              <li class="flex items-start gap-2">
                <span class="text-primary">•</span>
                Check your spam/junk folder
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary">•</span>
                Make sure the email address is correct
              </li>
              <li class="flex items-start gap-2">
                <span class="text-primary">•</span>
                Wait a few minutes and check again
              </li>
            </ul>
          </div>

          <button
            type="button"
            onclick={handleResend}
            class="w-full px-5 py-3 border border-primary text-primary font-medium rounded-full hover:bg-primary/10 transition-all mb-4"
          >
            Try Another Email
          </button>

          <a
            href="/login/"
            class="inline-flex items-center gap-2 text-muted hover:text-primary font-medium text-sm transition-colors"
          >
            <ArrowLeft size={16} />
            Back to Sign In
          </a>
        </div>
      {/if}
    </div>

    <!-- Help Link -->
    <div class="mt-8 text-center animate-fade-in" style="opacity: 0; animation-delay: 200ms; animation-fill-mode: forwards;">
      <p class="text-sm text-muted">
        Need help?{' '}
        <a href="/contact/" class="text-primary hover:text-primary font-medium">Contact Support</a>
      </p>
    </div>
  </div>
</div>
