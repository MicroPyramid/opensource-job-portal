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
    ExternalLink,
    Check,
    Shield,
    Zap
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
  let passwordStrengthColor = $derived(['bg-border', 'bg-error', 'bg-warning', 'bg-success'][passwordStrength]);
</script>

<svelte:head>
  <title>Sign Up - PeelJobs</title>
  <meta name="description" content="Create your PeelJobs account and start your journey to finding the perfect job or hiring top talent." />
</svelte:head>

<div class="min-h-screen flex">
  <!-- Left Panel - Branding (hidden on mobile, shown on lg+) -->
  <div class="hidden lg:flex lg:w-1/2 bg-[#1D2226] relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0">
      <div class="absolute top-0 right-0 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
      <div class="absolute bottom-0 left-0 w-80 h-80 bg-primary/10 rounded-full blur-3xl"></div>
    </div>

    <div class="relative z-10 flex flex-col justify-center px-12 xl:px-16 w-full">
      <!-- Logo -->
      <a href="/" class="flex items-center gap-3 mb-12">
        <div class="w-12 h-12 rounded-lg bg-primary flex items-center justify-center">
          <span class="text-xl font-bold text-white">P</span>
        </div>
        <span class="text-2xl font-semibold text-white">PeelJobs</span>
      </a>

      <!-- Main Heading -->
      <h1 class="text-3xl xl:text-4xl font-semibold text-white leading-tight mb-4">
        Take the next step in your career journey
      </h1>
      <p class="text-lg text-gray-400 mb-12">
        Join millions of professionals finding their dream jobs every day.
      </p>

      <!-- Features -->
      <div class="space-y-6">
        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
            <Briefcase class="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 class="text-white font-medium mb-1">50,000+ Active Jobs</h3>
            <p class="text-gray-400 text-sm">New opportunities added every day from top companies</p>
          </div>
        </div>

        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-lg bg-success/20 flex items-center justify-center flex-shrink-0">
            <Shield class="w-5 h-5 text-success" />
          </div>
          <div>
            <h3 class="text-white font-medium mb-1">Verified Employers</h3>
            <p class="text-gray-400 text-sm">All companies are verified for your safety</p>
          </div>
        </div>

        <div class="flex items-start gap-4">
          <div class="w-10 h-10 rounded-lg bg-warning/20 flex items-center justify-center flex-shrink-0">
            <Zap class="w-5 h-5 text-warning" />
          </div>
          <div>
            <h3 class="text-white font-medium mb-1">Quick Apply</h3>
            <p class="text-gray-400 text-sm">Apply to jobs with just one click</p>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Right Panel - Form -->
  <div class="flex-1 flex flex-col bg-white">
    <!-- Header -->
    <header class="border-b border-border">
      <div class="max-w-lg mx-auto w-full px-6 h-16 flex items-center justify-between">
        <a href="/" class="flex items-center gap-2 lg:hidden">
          <div class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span class="text-sm font-bold text-white">P</span>
          </div>
          <span class="text-lg font-semibold text-black">PeelJobs</span>
        </a>
        <div class="text-sm text-muted ml-auto">
          Already have an account?{' '}
          <a href="/login/" class="text-primary hover:text-primary-hover font-medium">Sign in</a>
        </div>
      </div>
    </header>

    <div class="flex-1 flex items-center justify-center px-6 py-12">
      <div class="w-full max-w-lg">
        {#if step === 1}
          <!-- Step 1: User Type Selection -->
          <div class="animate-fade-in-up" style="opacity: 0; animation-fill-mode: forwards;">
            <div class="text-center mb-10">
              <h1 class="text-2xl font-semibold text-black mb-2">
                Join PeelJobs Today
              </h1>
              <p class="text-muted">
                Choose how you'd like to get started
              </p>
            </div>

            <div class="space-y-4">
              {#each userTypes as type, i}
                <button
                  type="button"
                  onclick={() => selectUserType(type.id)}
                  class="group w-full bg-white rounded-lg p-5 border border-border hover:border-primary hover:shadow-md transition-all text-left animate-fade-in-up"
                  style="opacity: 0; animation-delay: {100 + i * 100}ms; animation-fill-mode: forwards;"
                >
                  <div class="flex items-start gap-4">
                    <div class="w-12 h-12 rounded-lg bg-surface group-hover:bg-primary/10 flex items-center justify-center transition-colors">
                      <type.icon class="w-6 h-6 text-primary" />
                    </div>
                    <div class="flex-1">
                      <div class="flex items-center justify-between mb-1">
                        <h2 class="text-lg font-semibold text-black group-hover:text-primary transition-colors">
                          {type.title}
                        </h2>
                        {#if type.externalUrl}
                          <ExternalLink class="w-4 h-4 text-muted" />
                        {/if}
                      </div>
                      <p class="text-sm text-muted mb-4">
                        {type.description}
                      </p>

                      <div class="flex flex-wrap gap-2">
                        {#each type.benefits as benefit}
                          <span class="inline-flex items-center gap-1.5 px-2.5 py-1 bg-surface text-xs text-muted rounded">
                            <benefit.icon class="w-3 h-3 text-success" />
                            {benefit.text}
                          </span>
                        {/each}
                      </div>
                    </div>
                  </div>
                </button>
              {/each}
            </div>

            <!-- Trust Indicators -->
            <div class="mt-10 pt-8 border-t border-border">
              <div class="flex items-center justify-center gap-6 text-xs text-muted">
                <div class="flex items-center gap-1.5">
                  <Check class="w-4 h-4 text-success" />
                  <span>Free to use</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <Shield class="w-4 h-4 text-primary" />
                  <span>Secure & private</span>
                </div>
                <div class="flex items-center gap-1.5">
                  <Users class="w-4 h-4 text-muted" />
                  <span>1M+ users</span>
                </div>
              </div>
            </div>
          </div>

        {:else}
          <!-- Step 2: Registration Form -->
          <div class="animate-fade-in-up" style="opacity: 0; animation-fill-mode: forwards;">
            <!-- Header -->
            <div class="mb-8">
              <button
                type="button"
                onclick={goBackToUserType}
                class="inline-flex items-center gap-2 text-sm text-muted hover:text-primary font-medium mb-6 transition-colors"
              >
                <ArrowLeft class="w-4 h-4" />
                Change account type
              </button>

              <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center">
                  <UserCircle class="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h2 class="text-2xl font-semibold text-black">
                    Create Account
                  </h2>
                  <p class="text-sm text-muted">
                    Start your job search today
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
                class="w-full flex items-center justify-center gap-3 h-12 px-4 border border-border rounded-full bg-white text-black font-medium hover:bg-surface hover:border-muted transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg class="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Continue with Google</span>
              </button>
            </div>

            <div class="relative mb-6">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-border"></div>
              </div>
              <div class="relative flex justify-center">
                <span class="px-4 bg-white text-sm text-muted">Or register with email</span>
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
                <label for="fullName" class="block text-sm font-medium text-black mb-2">
                  Full Name
                </label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User class="w-5 h-5 text-muted" />
                  </span>
                  <input
                    id="fullName"
                    type="text"
                    bind:value={fullName}
                    placeholder="John Doe"
                    class="w-full h-12 pl-10 pr-4 border rounded-lg bg-white text-black placeholder-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.fullName ? 'border-error' : 'border-border'}"
                  />
                </div>
                {#if errors.fullName}
                  <p class="mt-1.5 text-sm text-error">{errors.fullName}</p>
                {/if}
              </div>

              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-black mb-2">
                  Email Address
                </label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail class="w-5 h-5 text-muted" />
                  </span>
                  <input
                    id="email"
                    type="email"
                    bind:value={email}
                    placeholder="you@example.com"
                    class="w-full h-12 pl-10 pr-4 border rounded-lg bg-white text-black placeholder-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.email ? 'border-error' : 'border-border'}"
                  />
                </div>
                {#if errors.email}
                  <p class="mt-1.5 text-sm text-error">{errors.email}</p>
                {/if}
              </div>

              <!-- Password -->
              <div>
                <label for="password" class="block text-sm font-medium text-black mb-2">
                  Password
                </label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock class="w-5 h-5 text-muted" />
                  </span>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    bind:value={password}
                    placeholder="Create a strong password"
                    class="w-full h-12 pl-10 pr-12 border rounded-lg bg-white text-black placeholder-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.password ? 'border-error' : 'border-border'}"
                  />
                  <button
                    type="button"
                    onclick={() => togglePasswordVisibility('password')}
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-muted hover:text-black"
                  >
                    {#if showPassword}
                      <EyeOff class="w-5 h-5" />
                    {:else}
                      <Eye class="w-5 h-5" />
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
                <label for="confirmPassword" class="block text-sm font-medium text-black mb-2">
                  Confirm Password
                </label>
                <div class="relative">
                  <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock class="w-5 h-5 text-muted" />
                  </span>
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    bind:value={confirmPassword}
                    placeholder="Confirm your password"
                    class="w-full h-12 pl-10 pr-12 border rounded-lg bg-white text-black placeholder-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all outline-none {errors.confirmPassword ? 'border-error' : 'border-border'}"
                  />
                  <button
                    type="button"
                    onclick={() => togglePasswordVisibility('confirm')}
                    class="absolute inset-y-0 right-0 pr-3 flex items-center text-muted hover:text-black"
                  >
                    {#if showConfirmPassword}
                      <EyeOff class="w-5 h-5" />
                    {:else}
                      <Eye class="w-5 h-5" />
                    {/if}
                  </button>
                </div>
                {#if errors.confirmPassword}
                  <p class="mt-1.5 text-sm text-error">{errors.confirmPassword}</p>
                {/if}
              </div>

              <!-- Terms -->
              <div class="pt-2">
                <label class="flex items-start gap-3 cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={acceptTerms}
                    class="mt-0.5 w-4 h-4 text-primary border-border rounded focus:ring-primary"
                  />
                  <span class="text-sm text-muted">
                    I agree to the{' '}
                    <a href="/terms/" target="_blank" class="text-primary hover:text-primary-hover font-medium">Terms of Service</a>
                    {' '}and{' '}
                    <a href="/privacy/" target="_blank" class="text-primary hover:text-primary-hover font-medium">Privacy Policy</a>
                  </span>
                </label>
                {#if errors.terms}
                  <p class="mt-1.5 text-sm text-error">{errors.terms}</p>
                {/if}
              </div>

              <!-- Submit Error -->
              {#if errors.submit}
                <div class="p-4 bg-error-light border border-error/20 rounded-lg">
                  <p class="text-sm text-error">{errors.submit}</p>
                </div>
              {/if}

              <!-- Submit Button -->
              <button
                type="submit"
                disabled={isLoading}
                class="w-full h-12 px-6 bg-primary hover:bg-primary-hover text-white font-medium rounded-full transition-all shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
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
              <p class="text-sm text-muted">
                Already have an account?{' '}
                <a href="/login/" class="text-primary hover:text-primary-hover font-medium">Sign in</a>
              </p>
            </div>
          </div>
        {/if}
      </div>
    </div>
  </div>
</div>
