<script>
  import { Lock, Eye, EyeOff, ChevronLeft, Save, Check, AlertCircle } from '@lucide/svelte';

  let currentPassword = '';
  let newPassword = '';
  let confirmPassword = '';
  /** @type {{currentPassword?: string, newPassword?: string, confirmPassword?: string, submit?: string}} */
  let errors = {};
  let isLoading = false;
  let showCurrentPassword = false;
  let showNewPassword = false;
  let showConfirmPassword = false;
  let saveSuccess = false;

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

    if (!currentPassword) {
      errors.currentPassword = 'Current password is required';
      isValid = false;
    }

    if (!newPassword) {
      errors.newPassword = 'New password is required';
      isValid = false;
    } else if (!validatePassword(newPassword)) {
      errors.newPassword = 'Password must be at least 8 characters with uppercase, lowercase, and number';
      isValid = false;
    } else if (newPassword === currentPassword) {
      errors.newPassword = 'New password must be different from current password';
      isValid = false;
    }

    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your new password';
      isValid = false;
    } else if (newPassword !== confirmPassword) {
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
    saveSuccess = false;

    try {
      // TODO: Replace with actual API call
      console.log('Changing password...');

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Simulate success
      saveSuccess = true;
      currentPassword = '';
      newPassword = '';
      confirmPassword = '';

      setTimeout(() => {
        saveSuccess = false;
      }, 5000);
    } catch (error) {
      console.error('Password change error:', error);
      errors.submit = 'Failed to change password. Please check your current password and try again.';
    } finally {
      isLoading = false;
    }
  }

  function togglePasswordVisibility(field) {
    if (field === 'current') {
      showCurrentPassword = !showCurrentPassword;
    } else if (field === 'new') {
      showNewPassword = !showNewPassword;
    } else if (field === 'confirm') {
      showConfirmPassword = !showConfirmPassword;
    }
  }

  // Password strength indicator
  $: passwordStrength = newPassword.length === 0 ? 0 :
    newPassword.length < 8 ? 1 :
    !validatePassword(newPassword) ? 2 :
    3;

  $: passwordStrengthText = ['', 'Weak', 'Fair', 'Strong'][passwordStrength];
  $: passwordStrengthColor = ['', 'bg-red-500', 'bg-yellow-500', 'bg-green-500'][passwordStrength];

  // Password requirements
  $: requirements = [
    { text: 'At least 8 characters', met: newPassword.length >= 8 },
    { text: 'Contains uppercase letter', met: /[A-Z]/.test(newPassword) },
    { text: 'Contains lowercase letter', met: /[a-z]/.test(newPassword) },
    { text: 'Contains number', met: /[0-9]/.test(newPassword) },
    { text: 'Different from current password', met: newPassword && newPassword !== currentPassword }
  ];
</script>

<svelte:head>
  <title>Change Password - HirePulse.in</title>
  <meta name="description" content="Update your account password" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center gap-4 mb-4">
      <a
        href="/settings"
        class="p-2 hover:bg-white/10 rounded-lg transition-colors duration-200"
      >
        <ChevronLeft size={24} />
      </a>
      <div class="flex items-center gap-3">
        <div class="p-3 bg-white/10 rounded-lg">
          <Lock size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Change Password</h1>
          <p class="text-blue-100 mt-1">Update your account password</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6 max-w-2xl">

    {#if saveSuccess}
      <div class="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3 animate-fade-in">
        <Check class="text-green-600" size={20} />
        <div>
          <p class="text-green-700 font-medium">Password changed successfully!</p>
          <p class="text-sm text-green-600">Your password has been updated. Use your new password the next time you sign in.</p>
        </div>
      </div>
    {/if}

    <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
      <div class="mb-6 pb-6 border-b border-gray-200">
        <h2 class="text-2xl font-bold text-gray-800 mb-2">Update Your Password</h2>
        <p class="text-sm text-gray-600">
          Choose a strong password to keep your account secure
        </p>
      </div>

      <form onsubmit={handleSubmit} class="space-y-6">
        <!-- Current Password -->
        <div>
          <label for="currentPassword" class="block text-sm font-medium text-gray-700 mb-2">
            Current Password *
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock class="text-gray-400" size={20} />
            </div>
            <input
              id="currentPassword"
              type={showCurrentPassword ? 'text' : 'password'}
              bind:value={currentPassword}
              placeholder="••••••••"
              class="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              class:border-red-500={errors.currentPassword}
              disabled={isLoading}
            />
            <button
              type="button"
              onclick={() => togglePasswordVisibility('current')}
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {#if showCurrentPassword}
                <EyeOff class="text-gray-400 hover:text-gray-600" size={20} />
              {:else}
                <Eye class="text-gray-400 hover:text-gray-600" size={20} />
              {/if}
            </button>
          </div>
          {#if errors.currentPassword}
            <p class="mt-1 text-sm text-red-600">{errors.currentPassword}</p>
          {/if}
          <a href="/forgot-password" class="text-xs text-blue-600 hover:text-blue-700 mt-1 inline-block">
            Forgot your password?
          </a>
        </div>

        <!-- New Password -->
        <div>
          <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-2">
            New Password *
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock class="text-gray-400" size={20} />
            </div>
            <input
              id="newPassword"
              type={showNewPassword ? 'text' : 'password'}
              bind:value={newPassword}
              placeholder="••••••••"
              class="w-full pl-10 pr-12 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
              class:border-red-500={errors.newPassword}
              disabled={isLoading}
            />
            <button
              type="button"
              onclick={() => togglePasswordVisibility('new')}
              class="absolute inset-y-0 right-0 pr-3 flex items-center"
            >
              {#if showNewPassword}
                <EyeOff class="text-gray-400 hover:text-gray-600" size={20} />
              {:else}
                <Eye class="text-gray-400 hover:text-gray-600" size={20} />
              {/if}
            </button>
          </div>

          {#if newPassword.length > 0}
            <div class="mt-3">
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs text-gray-600">Password strength:</span>
                <span class="text-xs font-medium" class:text-red-600={passwordStrength === 1} class:text-yellow-600={passwordStrength === 2} class:text-green-600={passwordStrength === 3}>
                  {passwordStrengthText}
                </span>
              </div>
              <div class="w-full bg-gray-200 rounded-full h-2">
                <div class="h-2 rounded-full transition-all duration-300 {passwordStrengthColor}" style="width: {passwordStrength * 33.33}%"></div>
              </div>
            </div>
          {/if}

          {#if errors.newPassword}
            <p class="mt-2 text-sm text-red-600">{errors.newPassword}</p>
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

        <!-- Password Requirements -->
        {#if newPassword.length > 0}
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="text-sm font-semibold text-blue-900 mb-3">Password Requirements:</h3>
            <ul class="space-y-2">
              {#each requirements as requirement}
                <li class="flex items-center gap-2 text-sm">
                  {#if requirement.met}
                    <Check size={16} class="text-green-600 flex-shrink-0" />
                    <span class="text-green-700">{requirement.text}</span>
                  {:else}
                    <AlertCircle size={16} class="text-gray-400 flex-shrink-0" />
                    <span class="text-gray-600">{requirement.text}</span>
                  {/if}
                </li>
              {/each}
            </ul>
          </div>
        {/if}

        <!-- Submit Error -->
        {#if errors.submit}
          <div class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle class="text-red-600 flex-shrink-0" size={20} />
            <p class="text-sm text-red-600">{errors.submit}</p>
          </div>
        {/if}

        <!-- Submit Button -->
        <div class="flex justify-between items-center pt-4 border-t border-gray-200">
          <a
            href="/settings"
            class="text-gray-600 hover:text-blue-600 font-medium"
          >
            ← Back to Settings
          </a>

          <button
            type="submit"
            disabled={isLoading}
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {#if isLoading}
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Changing Password...
            {:else}
              <Save size={20} />
              Change Password
            {/if}
          </button>
        </div>
      </form>

      <!-- Security Tips -->
      <div class="mt-8 pt-6 border-t border-gray-200">
        <h3 class="font-semibold text-gray-800 mb-3">Password Security Tips</h3>
        <ul class="text-sm text-gray-600 space-y-2 list-disc list-inside">
          <li>Use a unique password that you don't use anywhere else</li>
          <li>Avoid common words, phrases, or personal information</li>
          <li>Consider using a password manager to generate and store strong passwords</li>
          <li>Change your password regularly, especially if you suspect it's been compromised</li>
          <li>Never share your password with anyone</li>
        </ul>
      </div>
    </div>

  </div>
</section>

<style>
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }
</style>
