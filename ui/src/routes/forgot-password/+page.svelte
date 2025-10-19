<script>
  import { Mail, ArrowLeft, CheckCircle } from '@lucide/svelte';

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
      // TODO: Replace with actual API call
      console.log('Password reset requested for:', email);

      // Simulate API call
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
  <title>Forgot Password - HirePulse.in</title>
  <meta name="description" content="Reset your HirePulse.in account password" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
  <div class="max-w-md w-full">
    <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-gray-100">

      {#if !emailSent}
        <!-- Request Reset Form -->
        <div>
          <!-- Header -->
          <div class="text-center mb-8">
            <div class="flex justify-center mb-4">
              <div class="p-3 bg-blue-100 rounded-full">
                <Mail class="text-blue-600" size={32} />
              </div>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
              Forgot Password?
            </h1>
            <p class="text-gray-600">
              No worries! Enter your email and we'll send you reset instructions.
            </p>
          </div>

          <!-- Form -->
          <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail class="text-gray-400" size={20} />
                </div>
                <input
                  id="email"
                  type="email"
                  bind:value={email}
                  placeholder="you@example.com"
                  class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.email}
                  disabled={isLoading}
                />
              </div>
              {#if errors.email}
                <p class="mt-1 text-sm text-red-600">{errors.email}</p>
              {/if}
            </div>

            <!-- Submit Error -->
            {#if errors.submit}
              <div class="bg-red-50 border border-red-200 rounded-lg p-3">
                <p class="text-sm text-red-600">{errors.submit}</p>
              </div>
            {/if}

            <!-- Submit Button -->
            <button
              type="submit"
              disabled={isLoading}
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {#if isLoading}
                <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              {:else}
                Send Reset Link
              {/if}
            </button>
          </form>

          <!-- Back to Login -->
          <div class="mt-6 text-center">
            <a href="/login" class="inline-flex items-center text-blue-600 hover:text-blue-700 font-medium">
              <ArrowLeft size={16} class="mr-1" />
              Back to Sign In
            </a>
          </div>
        </div>

      {:else}
        <!-- Success Message -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-green-100 rounded-full">
              <CheckCircle class="text-green-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Check Your Email
          </h2>

          <p class="text-gray-600 mb-2">
            We've sent password reset instructions to
          </p>
          <p class="text-blue-600 font-medium mb-6">
            {email}
          </p>

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p class="text-sm text-gray-700 mb-2">
              <strong>Didn't receive the email?</strong>
            </p>
            <ul class="text-sm text-gray-600 space-y-1 text-left list-disc list-inside">
              <li>Check your spam/junk folder</li>
              <li>Make sure the email address is correct</li>
              <li>Wait a few minutes and check again</li>
            </ul>
          </div>

          <button
            type="button"
            onclick={handleResend}
            class="w-full bg-white hover:bg-gray-50 text-blue-600 border-2 border-blue-600 font-semibold py-3 px-6 rounded-lg transition-colors duration-200 mb-4"
          >
            Try Another Email
          </button>

          <a
            href="/login"
            class="inline-flex items-center text-gray-600 hover:text-blue-600 font-medium text-sm"
          >
            <ArrowLeft size={16} class="mr-1" />
            Back to Sign In
          </a>
        </div>
      {/if}

    </div>

    <!-- Additional Help -->
    <div class="mt-8 text-center">
      <p class="text-sm text-gray-600">
        Need more help?
        <a href="/contact" class="text-blue-600 hover:text-blue-700 font-medium">
          Contact Support
        </a>
      </p>
    </div>
  </div>
</div>
