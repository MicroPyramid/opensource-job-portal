<script>
  import '../../app.css';

  import { untrack } from 'svelte';
  import { enhance } from '$app/forms';
  import { AlertCircle, Loader2, Briefcase, Shield, Zap } from '@lucide/svelte';

  /** @type {{ data: { googleAuthUrl: string | null, error: string | null }, form: { message?: string, email?: string } | null }} */
  let { data, form } = $props();

  // The auth URL is resolved server-side, so signing in is a plain link —
  // no token handling, and nothing to hydrate before the button works.
  let isLoading = $state(false);
  let loadingProvider = $state('');
  let error = $state(untrack(() => data.error ?? ''));

  // A failed POST re-renders with `form` set; surface that in the same banner
  // the OAuth errors use.
  $effect(() => {
    if (form?.message) error = form.message;
  });

  /**
   * Password sign-in. Reset the button whatever the outcome.
   * @type {import('@sveltejs/kit').SubmitFunction}
   */
  function submitLogin() {
    isLoading = true;
    loadingProvider = 'password';
    error = '';

    return async ({ update }) => {
      await update({ reset: false });
      isLoading = false;
      loadingProvider = '';
    };
  }

  function startGoogleLogin() {
    if (!data.googleAuthUrl) {
      error = 'Google sign-in is unavailable right now. Please try again shortly.';
      return;
    }
    isLoading = true;
    loadingProvider = 'google';
  }

  function showFacebookNotice() {
    error = 'Facebook login coming soon!';
  }

  function clearError() {
    error = '';
  }

  const features = [
    { icon: Briefcase, title: 'Find Your Dream Job', description: 'Access thousands of opportunities' },
    { icon: Shield, title: 'Secure & Private', description: 'Your data is always protected' },
    { icon: Zap, title: 'Fast & Easy', description: 'One-click application process' }
  ];
</script>

<svelte:head>
  <title>Sign in - PeelJobs</title>
  <meta name="description" content="Sign in to PeelJobs - Your gateway to career opportunities" />
</svelte:head>

<div class="min-h-screen bg-white flex">
  <!-- Left Panel - Branding (Desktop Only) -->
  <div class="hidden lg:flex lg:w-1/2 bg-[#1D2226] relative overflow-hidden">
    <!-- Decorative Elements -->
    <div class="absolute inset-0">
      <div class="absolute top-0 right-0 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
    </div>

    <div class="relative z-10 flex flex-col justify-center px-12 xl:px-16 w-full">
      <!-- Logo -->
      <div class="mb-10 animate-fade-in-up" style="opacity: 0; animation-fill-mode: forwards;">
        <a href="/" class="inline-flex items-center gap-2">
          <img src="/logo.png" alt="PeelJobs" class="h-10 w-auto" />
          <span class="text-2xl font-semibold text-white">PeelJobs</span>
        </a>
      </div>

      <!-- Hero Text -->
      <div class="mb-10">
        <h1 class="text-3xl xl:text-4xl font-semibold text-white tracking-tight mb-4 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;">
          Welcome back
        </h1>
        <p class="text-lg text-gray-400 max-w-md animate-fade-in-up" style="opacity: 0; animation-delay: 150ms; animation-fill-mode: forwards;">
          Sign in to continue your job search and connect with top employers.
        </p>
      </div>

      <!-- Features -->
      <div class="space-y-5">
        {#each features as feature, i}
          <div
            class="flex items-start gap-4 animate-fade-in-up"
            style="opacity: 0; animation-delay: {200 + i * 50}ms; animation-fill-mode: forwards;"
          >
            <div class="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
              <feature.icon size={20} class="text-primary-400" />
            </div>
            <div>
              <h3 class="font-medium text-white mb-0.5">{feature.title}</h3>
              <p class="text-sm text-gray-400">{feature.description}</p>
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>

  <!-- Right Panel - Login Form -->
  <div class="flex-1 flex items-center justify-center p-6 lg:p-12">
    <div class="w-full max-w-sm">
      <!-- Mobile Logo -->
      <div class="lg:hidden text-center mb-8 animate-fade-in-down" style="opacity: 0; animation-fill-mode: forwards;">
        <a href="/" class="inline-flex items-center gap-2">
          <img src="/logo.png" alt="PeelJobs" class="h-10 w-auto" />
          <span class="text-2xl font-semibold text-black">PeelJobs</span>
        </a>
      </div>

      <!-- Login Card -->
      <div class="animate-fade-in-up" style="opacity: 0; animation-delay: 100ms; animation-fill-mode: forwards;">
        <div class="text-center mb-8">
          <h2 class="text-2xl font-semibold text-black mb-2">Sign in</h2>
          <p class="text-muted">Stay updated on your professional world</p>
        </div>

        <!-- Error Message -->
        {#if error}
          <div class="mb-6 p-4 bg-error-light border border-error-500/20 rounded-lg flex items-start gap-3 animate-scale-in">
            <AlertCircle size={20} class="text-error-600 mt-0.5 flex-shrink-0" />
            <div class="flex-1">
              <p class="text-error-600 text-sm">{error}</p>
              <button
                onclick={clearError}
                class="text-error-600 hover:text-error-700 text-xs font-medium mt-1 hover:underline"
              >
                Dismiss
              </button>
            </div>
          </div>
        {/if}

        <!-- Email / Password -->
        <form method="POST" action="?/login" use:enhance={submitLogin} class="space-y-4 mb-6">
          <div>
            <label for="email" class="block text-sm font-medium text-black mb-1.5">Email</label>
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              value={form?.email ?? ''}
              disabled={isLoading}
              class="w-full h-12 px-4 border border-border rounded-lg text-black placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600 transition-all disabled:opacity-50"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label for="password" class="block text-sm font-medium text-black">Password</label>
              <a
                href="/forgot-password/"
                class="text-sm text-primary-600 hover:text-primary-700 font-semibold hover:underline"
              >
                Forgot password?
              </a>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              autocomplete="current-password"
              required
              disabled={isLoading}
              class="w-full h-12 px-4 border border-border rounded-lg text-black placeholder:text-muted focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600 transition-all disabled:opacity-50"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            class="w-full flex items-center justify-center gap-2 h-12 px-5 bg-primary-600 hover:bg-primary-700 text-white font-semibold rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if loadingProvider === 'password'}
              <Loader2 size={20} class="animate-spin" />
            {/if}
            <span>Sign in</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="my-6 relative">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-border"></div>
          </div>
          <div class="relative flex justify-center">
            <span class="px-4 bg-white text-sm text-muted">or continue with</span>
          </div>
        </div>

        <!-- Social Login Buttons -->
        <div class="space-y-3">
          <!-- Google Login -->
          <a
            href={data.googleAuthUrl ?? '/login/'}
            onclick={startGoogleLogin}
            aria-disabled={!data.googleAuthUrl || isLoading}
            class="w-full flex items-center justify-center gap-3 h-12 px-5 border border-border rounded-full bg-white text-black font-semibold hover:bg-surface hover:shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500/20 focus:border-primary-600 transition-all {!data.googleAuthUrl ||
            isLoading
              ? 'opacity-50 cursor-not-allowed pointer-events-none'
              : ''}"
          >
            {#if loadingProvider === 'google'}
              <Loader2 size={20} class="animate-spin" />
            {:else}
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            {/if}
            <span>Sign in with Google</span>
          </a>

          <!-- Facebook Login -->
          <button
            onclick={showFacebookNotice}
            disabled={isLoading}
            class="w-full flex items-center justify-center gap-3 h-12 px-5 bg-[#1877F2] hover:bg-[#166fe5] text-white font-semibold rounded-full transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {#if loadingProvider === 'facebook'}
              <Loader2 size={20} class="animate-spin" />
            {:else}
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
            {/if}
            <span>Sign in with Facebook</span>
          </button>
        </div>

        <!-- Security Note -->
        <div class="mt-6 flex items-center justify-center gap-2 text-sm text-muted">
          <Shield size={16} class="text-success-500" />
          <span>Protected with enterprise-grade security</span>
        </div>
      </div>

      <!-- Terms and Register -->
      <div class="mt-8 text-center space-y-4 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms; animation-fill-mode: forwards;">
        <p class="text-sm text-muted">
          By signing in, you agree to our
          <a href="/terms/" class="text-primary-600 hover:text-primary-700 font-semibold hover:underline">Terms</a>
          and
          <a href="/privacy/" class="text-primary-600 hover:text-primary-700 font-semibold hover:underline">Privacy Policy</a>
        </p>

        <p class="text-sm text-muted">
          New to PeelJobs?
          <a href="/register/" class="text-primary-600 hover:text-primary-700 font-semibold hover:underline">Join now</a>
        </p>
      </div>

      <!-- Footer Links -->
      <div class="mt-8 flex justify-center gap-6 text-sm text-muted animate-fade-in" style="opacity: 0; animation-delay: 300ms; animation-fill-mode: forwards;">
        <a href="/about/" class="hover:text-black transition-colors">About</a>
        <a href="/help/" class="hover:text-black transition-colors">Help</a>
        <a href="/contact/" class="hover:text-black transition-colors">Contact</a>
      </div>
    </div>
  </div>
</div>
