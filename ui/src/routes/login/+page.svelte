<script>
  import '../../app.css';

  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { Chrome, Facebook, AlertCircle, Loader2 } from '@lucide/svelte';

  let isLoading = false;
  let loadingProvider = '';
  let error = '';

  // Check for error messages from URL params
  onMount(() => {
    const urlError = $page.url.searchParams.get('error');
    if (urlError) {
      error = getErrorMessage(urlError);
    }
  });

  /**
   * @param {string} errorCode
   */
  function getErrorMessage(errorCode) {
    /** @type {Record<string, string>} */
    const errorMessages = {
      'access_denied': 'Login was cancelled. Please try again.',
      'invalid_request': 'Something went wrong. Please try again.',
      'server_error': 'Server error occurred. Please try again later.',
      'temporarily_unavailable': 'Service temporarily unavailable. Please try again later.'
    };
    return errorMessages[errorCode] || 'An error occurred during login. Please try again.';
  }

  /**
   * @param {string} provider
   */
  async function handleSocialLogin(provider) {
    if (isLoading) return;

    isLoading = true;
    loadingProvider = provider;
    error = '';

    try {
      if (provider === 'google') {
        // Import auth API
        const { getGoogleAuthUrl } = await import('$lib/api/auth');

        // Get Google OAuth URL from backend
        const redirectUri = window.location.origin + '/auth/google/callback';
        const response = await getGoogleAuthUrl(redirectUri);

        // Redirect to Google
        window.location.href = response.auth_url;
      } else if (provider === 'facebook') {
        // Facebook login - coming soon
        error = 'Facebook login coming soon!';
        isLoading = false;
        loadingProvider = '';
      }
    } catch (err) {
      error = err instanceof Error ? err.message : 'Failed to initiate login. Please try again.';
      isLoading = false;
      loadingProvider = '';
    }
  }

  function clearError() {
    error = '';
  }
</script>

<svelte:head>
  <title>Login - PeelJobs</title>
  <meta name="description" content="Sign in to PeelJobs - Your gateway to career opportunities" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center p-4">
  <div class="w-full max-w-md">
    <!-- Logo and Welcome Message -->
    <div class="text-center mb-8">
      <div class="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl mb-6 shadow-lg">
        <span class="text-2xl font-bold text-white">H</span>
      </div>
      <h1 class="text-3xl font-bold text-gray-900 mb-2">Welcome to PeelJobs</h1>
      <p class="text-gray-600">Your gateway to career opportunities</p>
    </div>

    <!-- Login Card -->
    <div class="bg-white rounded-2xl shadow-xl p-8 border border-gray-100">
      <h2 class="text-2xl font-semibold text-gray-900 text-center mb-6">Sign In</h2>
      
      <!-- Error Message -->
      {#if error}
        <div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle class="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" />
          <div>
            <p class="text-red-800 text-sm">{error}</p>
            <button
              onclick={clearError}
              class="text-red-600 hover:text-red-800 text-xs underline mt-1"
            >
              Dismiss
            </button>
          </div>
        </div>
      {/if}

      <!-- Social Login Buttons -->
      <div class="space-y-3">
        <!-- Google Login -->
        <button
          onclick={() => handleSocialLogin('google')}
          disabled={isLoading}
          class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          {#if loadingProvider === 'google'}
            <Loader2 class="w-5 h-5 animate-spin" />
          {:else}
            <Chrome class="w-5 h-5 group-hover:scale-110 transition-transform" />
          {/if}
          <span>Continue with Google</span>
        </button>

        <!-- Facebook Login -->
        <button
          onclick={() => handleSocialLogin('facebook')}
          disabled={isLoading}
          class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-blue-600 rounded-lg font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
        >
          {#if loadingProvider === 'facebook'}
            <Loader2 class="w-5 h-5 animate-spin" />
          {:else}
            <Facebook class="w-5 h-5 group-hover:scale-110 transition-transform" />
          {/if}
          <span>Continue with Facebook</span>
        </button>
      </div>

      <!-- Divider -->
      <div class="my-6 relative">
        <div class="absolute inset-0 flex items-center">
          <div class="w-full border-t border-gray-200"></div>
        </div>
        <div class="relative flex justify-center text-sm">
          <span class="px-4 bg-white text-gray-500">Secure & Fast Login</span>
        </div>
      </div>

      <!-- Security Note -->
      <div class="text-center text-sm text-gray-500">
        <p>Your data is protected with enterprise-grade security</p>
      </div>
    </div>

    <!-- Terms and Privacy -->
    <div class="mt-6 text-center text-sm text-gray-600">
      <p>
        By signing in, you agree to our 
        <a href="/terms" class="text-blue-600 hover:text-blue-800 underline">Terms of Service</a>
        and 
        <a href="/privacy" class="text-blue-600 hover:text-blue-800 underline">Privacy Policy</a>
      </p>
    </div>

    <!-- Additional Links -->
    <div class="mt-8 text-center">
      <div class="flex justify-center space-x-6 text-sm text-gray-500">
        <a href="/about" class="hover:text-gray-700 transition-colors">About</a>
        <a href="/help" class="hover:text-gray-700 transition-colors">Help</a>
        <a href="/contact" class="hover:text-gray-700 transition-colors">Contact</a>
      </div>
    </div>
  </div>
</div>

<style>
  /* Custom animations */
  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }
  
  .bg-white {
    animation: fadeIn 0.6s ease-out;
  }
</style>