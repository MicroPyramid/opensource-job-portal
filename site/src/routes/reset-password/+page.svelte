<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Lock, Eye, EyeOff, CheckCircle, XCircle, ShieldCheck } from '@lucide/svelte';

  let password = '';
  let confirmPassword = '';
  /** @type {Record<string, string>} */
  let errors = {};
  let isLoading = false;
  let showPassword = false;
  let showConfirmPassword = false;
  let resetSuccess = false;
  let tokenValid = true;

  $: token = $page.url.searchParams.get('token');

  $: {
    if (!token) {
      tokenValid = false;
    } else {
      validateToken(token);
    }
  }

  /**
   * @param {string} token
   */
  async function validateToken(token) {
    try {
      console.log('Validating token:', token);
      await new Promise(resolve => setTimeout(resolve, 500));
      tokenValid = true;
    } catch (error) {
      console.error('Token validation error:', error);
      tokenValid = false;
    }
  }

  /**
   * @param {string} password
   */
  function validatePassword(password) {
    return password.length >= 8 &&
           /[A-Z]/.test(password) &&
           /[a-z]/.test(password) &&
           /[0-9]/.test(password);
  }

  function validateForm() {
    errors = {};
    let isValid = true;

    if (!password) {
      errors.password = 'Password is required';
      isValid = false;
    } else if (!validatePassword(password)) {
      errors.password = 'Password must be at least 8 characters with uppercase, lowercase, and number';
      isValid = false;
    }

    if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
      isValid = false;
    }

    return isValid;
  }

  async function handleSubmit() {
    if (!validateForm()) {
      return;
    }

    isLoading = true;

    try {
      console.log('Resetting password with token:', token);
      await new Promise(resolve => setTimeout(resolve, 1500));
      resetSuccess = true;

      setTimeout(() => {
        goto('/login');
      }, 3000);
    } catch (error) {
      console.error('Password reset error:', error);
      errors.submit = 'Failed to reset password. Please try again or request a new reset link.';
    } finally {
      isLoading = false;
    }
  }

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

  $: passwordStrength = password.length === 0 ? 0 :
    password.length < 8 ? 1 :
    !validatePassword(password) ? 2 :
    3;

  $: passwordStrengthText = ['', 'Weak', 'Fair', 'Strong'][passwordStrength];
  $: passwordStrengthColor = ['bg-border', 'bg-error', 'bg-warning', 'bg-success'][passwordStrength];
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

        <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
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
                type={showPassword ? 'text' : 'password'}
                bind:value={password}
                placeholder="Create a strong password"
                class="w-full pl-11 pr-12 py-3 border rounded-lg bg-surface text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.password ? 'border-error' : 'border-border'}"
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

            {#if errors.password}
              <p class="mt-1.5 text-sm text-error">{errors.password}</p>
            {:else}
              <p class="mt-1.5 text-xs text-muted">
                At least 8 characters with uppercase, lowercase, and number
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
                type={showConfirmPassword ? 'text' : 'password'}
                bind:value={confirmPassword}
                placeholder="Confirm your password"
                class="w-full pl-11 pr-12 py-3 border rounded-lg bg-surface text-black placeholder-muted focus:bg-white focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.confirmPassword ? 'border-error' : 'border-border'}"
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
            {#if errors.confirmPassword}
              <p class="mt-1.5 text-sm text-error">{errors.confirmPassword}</p>
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
