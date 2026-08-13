<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { enhance } from '$app/forms';
  import { Lock, Eye, EyeOff, CheckCircle, XCircle, ShieldCheck } from '@lucide/svelte';

  /**
   * @type {{
   *   data: { hasToken: boolean },
   *   form: { success?: boolean, tokenExpired?: boolean, message?: string,
   *           passwordError?: string, confirmPasswordError?: string } | null
   * }}
   */
  let { data, form } = $props();

  let password = $state('');
  let confirmPassword = $state('');
  let isLoading = $state(false);
  let showPassword = $state(false);
  let showConfirmPassword = $state(false);

  let token = $derived($page.url.searchParams.get('token') ?? '');
  let resetSuccess = $derived(Boolean(form?.success));

  // The server is the only thing that can judge a token, and it only does so
  // on submit. So: invalid when the link carried none, or when a submit came
  // back rejecting it.
  let tokenValid = $derived(data.hasToken && !form?.tokenExpired);

  /** @type {import('@sveltejs/kit').SubmitFunction} */
  function submitReset() {
    isLoading = true;

    return async ({ update }) => {
      await update({ reset: false });
      isLoading = false;
    };
  }

  $effect(() => {
    if (!resetSuccess) return;
    const timer = setTimeout(() => goto('/login/'), 3000);
    return () => clearTimeout(timer);
  });

  /**
   * @param {string} field
   */
  function togglePasswordVisibility(field) {
    if (field === 'password') {
      showPassword = !showPassword;
    } else {
      showConfirmPassword = !showConfirmPassword;
    }
  }

  // Advisory only — Django's AUTH_PASSWORD_VALIDATORS are the authority, and
  // they check different things (common-password and similarity lists). Doing
  // more than hint here would reject passwords the server would have accepted.
  let passwordStrength = $derived(
    password.length === 0 ? 0 :
    password.length < 8 ? 1 :
    /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password) ? 3 :
    2
  );

  let passwordStrengthText = $derived(['', 'Weak', 'Fair', 'Strong'][passwordStrength]);
  let passwordStrengthColor = $derived(['bg-border', 'bg-error', 'bg-warning', 'bg-success'][passwordStrength]);
</script>

<svelte:head>
  <title>Reset Password - PeelJobs</title>
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
      {#if !tokenValid}
        <!-- Invalid/Expired Token -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full bg-error-light flex items-center justify-center mx-auto mb-6">
            <XCircle size={32} class="text-error" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-3">
            Invalid or Expired Link
          </h2>

          <p class="text-muted mb-6">
            This password reset link is invalid or has expired. Please request a new one.
          </p>

          <a
            href="/forgot-password/"
            class="inline-block w-full px-5 py-3.5 bg-primary hover:bg-primary-hover text-white font-medium rounded-full transition-all shadow-sm hover:shadow-md text-center"
          >
            Request New Link
          </a>

          <div class="mt-6">
            <a href="/login/" class="text-muted hover:text-primary font-medium text-sm transition-colors">
              Back to Sign In
            </a>
          </div>
        </div>

      {:else if resetSuccess}
        <!-- Success State -->
        <div class="text-center animate-scale-in">
          <div class="w-16 h-16 rounded-full bg-success-light flex items-center justify-center mx-auto mb-6">
            <CheckCircle size={32} class="text-success" />
          </div>

          <h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-3">
            Password Reset Successful!
          </h2>

          <p class="text-muted mb-6">
            Your password has been successfully reset. You can now sign in with your new password.
          </p>

          <div class="bg-primary/10 rounded-xl p-4 mb-6">
            <p class="text-sm text-muted">
              Redirecting you to sign in page in a few seconds...
            </p>
          </div>

          <a
            href="/login/"
            class="inline-block w-full px-5 py-3.5 bg-primary hover:bg-primary-hover text-white font-medium rounded-full transition-all shadow-sm hover:shadow-md text-center"
          >
            Continue to Sign In
          </a>
        </div>

      {:else}
        <!-- Reset Password Form -->
        <div class="text-center mb-8">
          <div class="w-16 h-16 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
            <ShieldCheck size={32} class="text-primary" />
          </div>
          <h1 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-2">
            Reset Your Password
          </h1>
          <p class="text-muted">
            Enter your new password below
          </p>
        </div>

        <form method="POST" action="?/reset" use:enhance={submitReset} class="space-y-5">
          <input type="hidden" name="token" value={token} />
          <!-- New Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-muted mb-2">
              New Password
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock size={18} class="text-muted" />
              </span>
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autocomplete="new-password"
                required
                minlength="8"
                bind:value={password}
                placeholder="Create a strong password"
                class="w-full pl-11 pr-12 py-3 border rounded-lg bg-surface text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {form?.passwordError ? 'border-error' : 'border-border'}"
                disabled={isLoading}
              />
              <button
                type="button"
                onclick={() => togglePasswordVisibility('password')}
                class="absolute inset-y-0 right-0 pr-4 flex items-center text-muted hover:text-muted"
              >
                {#if showPassword}
                  <EyeOff size={18} />
                {:else}
                  <Eye size={18} />
                {/if}
              </button>
            </div>

            {#if password.length > 0}
              <div class="mt-3">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-xs text-muted">Password strength</span>
                  <span class="text-xs font-medium {passwordStrength === 1 ? 'text-error' : passwordStrength === 2 ? 'text-warning' : passwordStrength === 3 ? 'text-success' : 'text-muted'}">
                    {passwordStrengthText}
                  </span>
                </div>
                <div class="flex gap-1">
                  {#each [1, 2, 3] as level}
                    <div class="flex-1 h-1 rounded-full transition-colors {passwordStrength >= level ? passwordStrengthColor : 'bg-border'}"></div>
                  {/each}
                </div>
              </div>
            {/if}

            {#if form?.passwordError}
              <p class="mt-1.5 text-sm text-error">{form.passwordError}</p>
            {:else}
              <p class="mt-1.5 text-xs text-muted">
                At least 8 characters. Avoid common passwords and anything close to your name or email.
              </p>
            {/if}
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-muted mb-2">
              Confirm New Password
            </label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Lock size={18} class="text-muted" />
              </span>
              <input
                id="confirmPassword"
                name="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                autocomplete="new-password"
                required
                minlength="8"
                bind:value={confirmPassword}
                placeholder="Confirm your password"
                class="w-full pl-11 pr-12 py-3 border rounded-lg bg-surface text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {form?.confirmPasswordError ? 'border-error' : 'border-border'}"
                disabled={isLoading}
              />
              <button
                type="button"
                onclick={() => togglePasswordVisibility('confirm')}
                class="absolute inset-y-0 right-0 pr-4 flex items-center text-muted hover:text-muted"
              >
                {#if showConfirmPassword}
                  <EyeOff size={18} />
                {:else}
                  <Eye size={18} />
                {/if}
              </button>
            </div>
            {#if form?.confirmPasswordError}
              <p class="mt-1.5 text-sm text-error">{form.confirmPasswordError}</p>
            {/if}
          </div>

          {#if form?.message}
            <div class="p-4 bg-error-light border border-error/20 rounded-lg">
              <p class="text-sm text-error">{form.message}</p>
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
              Resetting Password...
            {:else}
              Reset Password
            {/if}
          </button>
        </form>

        <div class="mt-6 text-center">
          <a href="/login/" class="text-muted hover:text-primary font-medium text-sm transition-colors">
            Remember your password? Sign In
          </a>
        </div>
      {/if}
    </div>
  </div>
</div>
