<script>
  import { goto } from '$app/navigation';
  import { enhance } from '$app/forms';
  import { RECRUITER_URL } from '$lib/config/env';
  import {
    User,
    Mail,
    Lock,
    Eye,
    EyeOff,
    Building2,
    UserCircle,
    ArrowLeft,
    Briefcase,
    Users,
    TrendingUp,
    Target,
    ExternalLink
  } from '@lucide/svelte';

  /** @type {{ form?: { message?: string; email?: string; success?: boolean } }} */
  let { form } = $props();

  let step = $state(1);
  let userType = $state('');
  let email = $state(form?.email || '');
  let password = $state('');
  let confirmPassword = $state('');
  let fullName = $state('');
  let acceptTerms = $state(false);
  let showPassword = $state(false);
  let showConfirmPassword = $state(false);
  let isLoading = $state(false);

  /** @type {Record<string, string>} */
  let errors = $state({});

  // Handle form result
  $effect(() => {
    if (form?.success && form?.email) {
      goto(`/verify-email/?email=${encodeURIComponent(form.email)}`);
    } else if (form?.message) {
      errors = { submit: form.message };
      isLoading = false;
    }
  });

  const userTypes = [
    {
      id: 'jobseeker',
      title: 'Job Seeker',
      description: 'Looking for your next career opportunity',
      icon: UserCircle,
      color: 'primary',
      benefits: [
        { icon: Briefcase, text: 'Browse thousands of jobs' },
        { icon: Target, text: 'Get personalized recommendations' },
        { icon: TrendingUp, text: 'Track your applications' }
      ]
    },
    {
      id: 'recruiter',
      title: 'Recruiter',
      description: 'Hire top talent for your organization',
      icon: Building2,
      color: 'success',
      benefits: [
        { icon: Users, text: 'Access qualified candidates' },
        { icon: Target, text: 'Post unlimited listings' },
        { icon: TrendingUp, text: 'Build employer brand' }
      ],
      externalUrl: `${RECRUITER_URL}/signup/`
    }
  ];

  /**
   * @param {string} type
   */
  function selectUserType(type) {
    // Recruiters go to the dedicated recruiter portal
    const selectedType = userTypes.find(t => t.id === type);
    if (selectedType?.externalUrl) {
      window.location.href = selectedType.externalUrl;
      return;
    }
    userType = type;
    step = 2;
  }

  function goBackToUserType() {
    step = 1;
    errors = {};
  }

  /**
   * @param {string} email
   */
  function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
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

    if (!fullName.trim()) {
      errors.fullName = 'Full name is required';
      isValid = false;
    }

    if (!email.trim()) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!validateEmail(email)) {
      errors.email = 'Please enter a valid email address';
      isValid = false;
    }

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

    if (!acceptTerms) {
      errors.terms = 'You must accept the terms and conditions';
      isValid = false;
    }

    return isValid;
  }

  function handleSubmit() {
    if (!validateForm()) {
      return false;
    }
    isLoading = true;
    errors = {};
    return true;
  }

  /**
   * @param {string} provider
   */
  async function handleOAuthLogin(provider) {
    isLoading = true;
    try {
      console.log(`OAuth login with ${provider} for ${userType}`);
      window.location.href = `/auth/${provider}?userType=${userType}`;
    } catch (error) {
      console.error('OAuth error:', error);
      errors.submit = 'OAuth login failed. Please try again.';
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

  let passwordStrength = $derived(
    password.length === 0 ? 0 :
    password.length < 8 ? 1 :
    !validatePassword(password) ? 2 :
    3
  );

  let passwordStrengthText = $derived(['', 'Weak', 'Fair', 'Strong'][passwordStrength]);
  let passwordStrengthColor = $derived(['bg-gray-200', 'bg-error-500', 'bg-warning-500', 'bg-success-500'][passwordStrength]);
</script>

<svelte:head>
  <title>Sign Up - PeelJobs</title>
  <meta name="description" content="Create your PeelJobs account and start your journey to finding the perfect job or hiring top talent." />
</svelte:head>

<div class="min-h-screen bg-surface-50">
  <!-- Header -->
  <header class="bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-4 lg:px-8 h-16 flex items-center justify-between">
      <a href="/" class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
          <span class="text-lg font-bold text-white">P</span>
        </div>
        <span class="text-xl font-bold text-gray-900">PeelJobs</span>
      </a>
      <div class="text-sm text-gray-600">
        Already have an account?{' '}
        <a href="/login/" class="text-primary-600 hover:text-primary-700 font-medium">Sign in</a>
      </div>
    </div>
  </header>

  <div class="max-w-7xl mx-auto px-4 lg:px-8 py-12 lg:py-16">
    {#if step === 1}
      <!-- Step 1: User Type Selection -->
      <div class="max-w-4xl mx-auto">
        <div class="text-center mb-12 animate-fade-in-up" style="opacity: 0; animation-fill-mode: forwards;">
          <h1 class="text-3xl lg:text-4xl font-bold text-gray-900 tracking-tight mb-3">
            Join PeelJobs Today
          </h1>
          <p class="text-lg text-gray-600">
            Choose how you'd like to get started
          </p>
        </div>

        <div class="grid md:grid-cols-2 gap-6 lg:gap-8">
          {#each userTypes as type, i}
            <button
              type="button"
              onclick={() => selectUserType(type.id)}
              class="group bg-white rounded-2xl p-6 lg:p-8 border border-gray-100 hover:border-primary-200 elevation-1 hover:elevation-3 transition-all text-left animate-fade-in-up"
              style="opacity: 0; animation-delay: {100 + i * 100}ms; animation-fill-mode: forwards;"
            >
              <div class="flex items-start gap-4 mb-6">
                <div class="w-14 h-14 rounded-2xl bg-primary-50 group-hover:bg-primary-100 flex items-center justify-center transition-colors">
                  <type.icon size={28} class="text-primary-600" />
                </div>
                <div class="flex-1">
                  <h2 class="text-xl font-bold text-gray-900 group-hover:text-primary-600 transition-colors">
                    {type.title}
                  </h2>
                  <p class="text-gray-600 text-sm mt-1">
                    {type.description}
                  </p>
                </div>
              </div>

              <div class="space-y-3">
                {#each type.benefits as benefit}
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-lg bg-success-500/10 flex items-center justify-center">
                      <benefit.icon size={16} class="text-success-600" />
                    </div>
                    <span class="text-sm text-gray-700">{benefit.text}</span>
                  </div>
                {/each}
              </div>

              <div class="mt-6 pt-6 border-t border-gray-100">
                <span class="inline-flex items-center gap-2 text-primary-600 font-medium group-hover:gap-3 transition-all">
                  {#if type.externalUrl}
                    Go to Recruiter Portal
                    <ExternalLink size={16} />
                  {:else}
                    Get Started
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  {/if}
                </span>
              </div>
            </button>
          {/each}
        </div>
      </div>

    {:else}
      <!-- Step 2: Registration Form -->
      <div class="max-w-md mx-auto">
        <div class="bg-white rounded-2xl p-6 lg:p-8 elevation-1 animate-fade-in-up" style="opacity: 0; animation-fill-mode: forwards;">
          <!-- Header -->
          <div class="mb-8">
            <button
              type="button"
              onclick={goBackToUserType}
              class="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-primary-600 font-medium mb-6 transition-colors"
            >
              <ArrowLeft size={16} />
              Change account type
            </button>

            <div class="flex items-center gap-4">
              <div class="w-12 h-12 rounded-xl bg-primary-50 flex items-center justify-center">
                {#if userType === 'jobseeker'}
                  <UserCircle size={24} class="text-primary-600" />
                {:else}
                  <Building2 size={24} class="text-primary-600" />
                {/if}
              </div>
              <div>
                <h2 class="text-2xl font-bold text-gray-900 tracking-tight">
                  Create Account
                </h2>
                <p class="text-gray-600 text-sm">
                  {userType === 'jobseeker' ? 'Start your job search' : 'Begin hiring talent'}
                </p>
              </div>
            </div>
          </div>

          <!-- OAuth Options -->
          <div class="space-y-3 mb-6">
            <button
              type="button"
              onclick={() => handleOAuthLogin('google')}
              disabled={isLoading}
              class="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-200 rounded-xl bg-white text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-300 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continue with Google</span>
            </button>

            <button
              type="button"
              onclick={() => handleOAuthLogin('facebook')}
              disabled={isLoading}
              class="w-full flex items-center justify-center gap-3 px-4 py-3 bg-[#1877F2] hover:bg-[#166fe5] text-white font-medium rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <span>Continue with Facebook</span>
            </button>
          </div>

          <div class="relative mb-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-200"></div>
            </div>
            <div class="relative flex justify-center">
              <span class="px-4 bg-white text-sm text-gray-500">Or register with email</span>
            </div>
          </div>

          <!-- Registration Form -->
          <form
            method="POST"
            action="?/register"
            use:enhance={() => {
              if (!handleSubmit()) {
                return () => {};
              }
              return async ({ result, update }) => {
                isLoading = false;
                if (result.type === 'success' && result.data?.success) {
                  goto(`/verify-email/?email=${encodeURIComponent(email)}`);
                } else {
                  await update();
                }
              };
            }}
            class="space-y-5"
          >
            <!-- Hidden fields for form action -->
            <input type="hidden" name="full_name" value={fullName} />
            <input type="hidden" name="email" value={email} />
            <input type="hidden" name="password" value={password} />
            <input type="hidden" name="confirm_password" value={confirmPassword} />
            <!-- Full Name -->
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <User size={18} class="text-gray-400" />
                </span>
                <input
                  id="fullName"
                  type="text"
                  bind:value={fullName}
                  placeholder="John Doe"
                  class="w-full pl-11 pr-4 py-3 border rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none {errors.fullName ? 'border-error-500' : 'border-gray-200'}"
                />
              </div>
              {#if errors.fullName}
                <p class="mt-1.5 text-sm text-error-600">{errors.fullName}</p>
              {/if}
            </div>

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Mail size={18} class="text-gray-400" />
                </span>
                <input
                  id="email"
                  type="email"
                  bind:value={email}
                  placeholder="you@example.com"
                  class="w-full pl-11 pr-4 py-3 border rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none {errors.email ? 'border-error-500' : 'border-gray-200'}"
                />
              </div>
              {#if errors.email}
                <p class="mt-1.5 text-sm text-error-600">{errors.email}</p>
              {/if}
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} class="text-gray-400" />
                </span>
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  bind:value={password}
                  placeholder="Create a strong password"
                  class="w-full pl-11 pr-12 py-3 border rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none {errors.password ? 'border-error-500' : 'border-gray-200'}"
                />
                <button
                  type="button"
                  onclick={() => togglePasswordVisibility('password')}
                  class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
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
                    <span class="text-xs text-gray-600">Password strength</span>
                    <span class="text-xs font-medium {passwordStrength === 1 ? 'text-error-600' : passwordStrength === 2 ? 'text-warning-600' : passwordStrength === 3 ? 'text-success-600' : 'text-gray-400'}">
                      {passwordStrengthText}
                    </span>
                  </div>
                  <div class="flex gap-1">
                    {#each [1, 2, 3] as level}
                      <div class="flex-1 h-1 rounded-full transition-colors {passwordStrength >= level ? passwordStrengthColor : 'bg-gray-200'}"></div>
                    {/each}
                  </div>
                </div>
              {/if}

              {#if errors.password}
                <p class="mt-1.5 text-sm text-error-600">{errors.password}</p>
              {:else}
                <p class="mt-1.5 text-xs text-gray-500">
                  At least 8 characters with uppercase, lowercase, and number
                </p>
              {/if}
            </div>

            <!-- Confirm Password -->
            <div>
              <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <div class="relative">
                <span class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Lock size={18} class="text-gray-400" />
                </span>
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  bind:value={confirmPassword}
                  placeholder="Confirm your password"
                  class="w-full pl-11 pr-12 py-3 border rounded-xl bg-gray-50 text-gray-900 placeholder-gray-500 focus:bg-white focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all outline-none {errors.confirmPassword ? 'border-error-500' : 'border-gray-200'}"
                />
                <button
                  type="button"
                  onclick={() => togglePasswordVisibility('confirm')}
                  class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
                >
                  {#if showConfirmPassword}
                    <EyeOff size={18} />
                  {:else}
                    <Eye size={18} />
                  {/if}
                </button>
              </div>
              {#if errors.confirmPassword}
                <p class="mt-1.5 text-sm text-error-600">{errors.confirmPassword}</p>
              {/if}
            </div>

            <!-- Terms -->
            <div class="pt-2">
              <label class="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={acceptTerms}
                  class="mt-0.5 w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span class="text-sm text-gray-600">
                  I agree to the{' '}
                  <a href="/terms/" target="_blank" class="text-primary-600 hover:text-primary-700 font-medium">Terms of Service</a>
                  {' '}and{' '}
                  <a href="/privacy/" target="_blank" class="text-primary-600 hover:text-primary-700 font-medium">Privacy Policy</a>
                </span>
              </label>
              {#if errors.terms}
                <p class="mt-1.5 text-sm text-error-600">{errors.terms}</p>
              {/if}
            </div>

            <!-- Submit Error -->
            {#if errors.submit}
              <div class="p-4 bg-error-500/10 border border-error-500/20 rounded-xl">
                <p class="text-sm text-error-600">{errors.submit}</p>
              </div>
            {/if}

            <!-- Submit Button -->
            <button
              type="submit"
              disabled={isLoading}
              class="w-full px-5 py-3.5 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-all elevation-1 hover:elevation-2 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {#if isLoading}
                <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creating Account...
              {:else}
                Create Account
              {/if}
            </button>
          </form>

          <!-- Sign In Link -->
          <div class="mt-6 text-center">
            <p class="text-sm text-gray-600">
              Already have an account?{' '}
              <a href="/login/" class="text-primary-600 hover:text-primary-700 font-medium">Sign in</a>
            </p>
          </div>
        </div>
      </div>
    {/if}
  </div>
</div>
