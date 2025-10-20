<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { Lock, Eye, EyeOff, CheckCircle, XCircle } from '@lucide/svelte';

  let password = '';
  let confirmPassword = '';
  /** @type {Record<string, string>} */
  let errors = {};
  let isLoading = false;
  let showPassword = false;
  let showConfirmPassword = false;
  let resetSuccess = false;
  let tokenValid = true;

  // Get token from URL query params
  $: token = $page.url.searchParams.get('token');

  // Validate token on mount
  $: {
    if (!token) {
      tokenValid = false;
    } else {
      // TODO: Validate token with API
      validateToken(token);
    }
  }

  /**
   * @param {string} token
   */
  async function validateToken(token) {
    try {
      // TODO: Replace with actual API call
      console.log('Validating token:', token);
      // Simulate API call
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
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
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
      // TODO: Replace with actual API call
      console.log('Resetting password with token:', token);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      resetSuccess = true;

      // Redirect to login after 3 seconds
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

  // Password strength indicator
  $: passwordStrength = password.length === 0 ? 0 :
    password.length < 8 ? 1 :
    !validatePassword(password) ? 2 :
    3;

  $: passwordStrengthText = ['', 'Weak', 'Fair', 'Strong'][passwordStrength];
  $: passwordStrengthColor = ['', 'bg-red-500', 'bg-yellow-500', 'bg-green-500'][passwordStrength];
</script>

<svelte:head>
  <title>Reset Password - HirePulse.in</title>
  <meta name="description" content="Reset your HirePulse.in account password" />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
  <div class="max-w-md w-full">
    <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-gray-100">

      {#if !tokenValid}
        <!-- Invalid/Expired Token -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-red-100 rounded-full">
              <XCircle class="text-red-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Invalid or Expired Link
          </h2>

          <p class="text-gray-600 mb-6">
            This password reset link is invalid or has expired. Please request a new one.
          </p>

          <a
            href="/forgot-password/"
            class="inline-block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg text-center"
          >
            Request New Link
          </a>

          <div class="mt-6">
            <a href="/login/" class="text-gray-600 hover:text-blue-600 font-medium">
              Back to Sign In
            </a>
          </div>
        </div>

      {:else if resetSuccess}
        <!-- Success Message -->
        <div class="text-center">
          <div class="flex justify-center mb-6">
            <div class="p-4 bg-green-100 rounded-full">
              <CheckCircle class="text-green-600" size={48} />
            </div>
          </div>

          <h2 class="text-3xl font-bold text-gray-900 mb-3">
            Password Reset Successful!
          </h2>

          <p class="text-gray-600 mb-6">
            Your password has been successfully reset. You can now sign in with your new password.
          </p>

          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <p class="text-sm text-gray-600">
              Redirecting you to sign in page in a few seconds...
            </p>
          </div>

          <a
            href="/login/"
            class="inline-block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg text-center"
          >
            Continue to Sign In
          </a>
        </div>

      {:else}
        <!-- Reset Password Form -->
        <div>
          <!-- Header -->
          <div class="text-center mb-8">
            <div class="flex justify-center mb-4">
              <div class="p-3 bg-blue-100 rounded-full">
                <Lock class="text-blue-600" size={32} />
              </div>
            </div>
            <h1 class="text-3xl font-bold text-gray-900 mb-2">
              Reset Your Password
            </h1>
            <p class="text-gray-600">
              Enter your new password below
            </p>
          </div>

          <!-- Form -->
          <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
            <!-- New Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                New Password *
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock class="text-gray-400" size={20} />
                </div>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  bind:value={password}
                  placeholder="••••••••"
                  class="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.password}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onclick={() => togglePasswordVisibility('password')}
                  class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {#if showPassword}
                    <EyeOff class="text-gray-400 hover:text-gray-600" size={20} />
                  {:else}
                    <Eye class="text-gray-400 hover:text-gray-600" size={20} />
                  {/if}
                </button>
              </div>

              {#if password.length > 0}
                <div class="mt-2">
                  <div class="flex items-center justify-between mb-1">
                    <span class="text-xs text-gray-600">Password strength:</span>
                    <span class="text-xs font-medium" class:text-red-600={passwordStrength === 1} class:text-yellow-600={passwordStrength === 2} class:text-green-600={passwordStrength === 3}>
                      {passwordStrengthText}
                    </span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-1.5">
                    <div class="h-1.5 rounded-full transition-all duration-300 {passwordStrengthColor}" style="width: {passwordStrength * 33.33}%"></div>
                  </div>
                </div>
              {/if}

              {#if errors.password}
                <p class="mt-1 text-sm text-red-600">{errors.password}</p>
              {:else}
                <p class="mt-1 text-xs text-gray-500">
                  Must be at least 8 characters with uppercase, lowercase, and number
                </p>
              {/if}
            </div>

            <!-- Confirm Password -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm New Password *
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock class="text-gray-400" size={20} />
                </div>
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  bind:value={confirmPassword}
                  placeholder="••••••••"
                  class="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.confirmPassword}
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onclick={() => togglePasswordVisibility('confirm')}
                  class="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {#if showConfirmPassword}
                    <EyeOff class="text-gray-400 hover:text-gray-600" size={20} />
                  {:else}
                    <Eye class="text-gray-400 hover:text-gray-600" size={20} />
                  {/if}
                </button>
              </div>
              {#if errors.confirmPassword}
                <p class="mt-1 text-sm text-red-600">{errors.confirmPassword}</p>
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
                Resetting Password...
              {:else}
                Reset Password
              {/if}
            </button>
          </form>

          <!-- Back to Login -->
          <div class="mt-6 text-center">
            <a href="/login/" class="text-gray-600 hover:text-blue-600 font-medium text-sm">
              Remember your password? Sign In
            </a>
          </div>
        </div>
      {/if}

    </div>
  </div>
</div>
