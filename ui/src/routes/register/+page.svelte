<script>
  import { goto } from '$app/navigation';
  import {
    User,
    Mail,
    Lock,
    Briefcase,
    UserCircle,
    Eye,
    EyeOff,
    CheckCircle,
    Building2,
    Sparkles
  } from '@lucide/svelte';

  // Form state
  let step = 1; // 1: User type selection, 2: Registration form
  let userType = ''; // 'jobseeker' or 'recruiter'
  let email = '';
  let password = '';
  let confirmPassword = '';
  let fullName = '';
  let companyName = ''; // For recruiters only
  let acceptTerms = false;
  let showPassword = false;
  let showConfirmPassword = false;
  let isLoading = false;

  // Error handling
  /** @type {Record<string, string>} */
  let errors = {};

  // User type options
  const userTypes = [
    {
      id: 'jobseeker',
      title: 'Job Seeker',
      description: 'Looking for your next career opportunity',
      icon: UserCircle,
      benefits: [
        'Browse thousands of jobs',
        'Get personalized recommendations',
        'Track your applications',
        'Build your professional profile'
      ]
    },
    {
      id: 'recruiter',
      title: 'Recruiter / Employer',
      description: 'Hire top talent for your organization',
      icon: Building2,
      benefits: [
        'Post unlimited job listings',
        'Access qualified candidates',
        'Manage applications efficiently',
        'Build your employer brand'
      ]
    }
  ];

  /**
   * @param {string} type
   */
  function selectUserType(type) {
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
    // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
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

    if (userType === 'recruiter' && !companyName.trim()) {
      errors.companyName = 'Company name is required';
      isValid = false;
    }

    if (!acceptTerms) {
      errors.terms = 'You must accept the terms and conditions';
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
      const formData = {
        userType,
        email,
        password,
        fullName,
        ...(userType === 'recruiter' && { companyName })
      };

      console.log('Registration data:', formData);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Redirect based on user type
      if (userType === 'jobseeker') {
        goto('/jobseeker-dashboard');
      } else {
        goto('/recruiter');
      }
    } catch (error) {
      console.error('Registration error:', error);
      errors.submit = 'Registration failed. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  /**
   * @param {string} provider
   */
  async function handleOAuthLogin(provider) {
    isLoading = true;
    try {
      // TODO: Implement OAuth flow
      console.log(`OAuth login with ${provider} for ${userType}`);
      // Redirect to OAuth endpoint with userType parameter
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

  // Password strength indicator
  $: passwordStrength = password.length === 0 ? 0 :
    password.length < 8 ? 1 :
    !validatePassword(password) ? 2 :
    3;

  $: passwordStrengthText = ['', 'Weak', 'Fair', 'Strong'][passwordStrength];
  $: passwordStrengthColor = ['', 'bg-red-500', 'bg-yellow-500', 'bg-green-500'][passwordStrength];
</script>

<svelte:head>
  <title>Sign Up - HirePulse.in</title>
  <meta name="description" content="Create your HirePulse.in account and start your journey to finding the perfect job or hiring top talent." />
</svelte:head>

<div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4 sm:px-6 lg:px-8">
  <div class="max-w-7xl mx-auto">

    {#if step === 1}
      <!-- Step 1: User Type Selection -->
      <div class="text-center mb-12 animate-fade-in">
        <div class="flex justify-center mb-4">
          <div class="p-3 bg-blue-100 rounded-full">
            <Sparkles class="text-blue-600" size={32} />
          </div>
        </div>
        <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Join HirePulse.in Today
        </h1>
        <p class="text-lg md:text-xl text-gray-600 max-w-2xl mx-auto">
          Choose how you'd like to get started and unlock opportunities
        </p>
      </div>

      <div class="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
        {#each userTypes as type}
          <div
            class="group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 p-8 border-2 border-gray-100 hover:border-blue-500 cursor-pointer transform hover:-translate-y-2"
            role="button"
            tabindex="0"
            onclick={() => selectUserType(type.id)}
            onkeydown={(e) => e.key === 'Enter' && selectUserType(type.id)}
          >
            <div class="flex justify-center mb-6">
              <div class="p-4 bg-blue-100 rounded-full group-hover:bg-blue-600 transition-colors duration-300">
                <type.icon class="text-blue-600 group-hover:text-white transition-colors duration-300" size={48} />
              </div>
            </div>

            <h2 class="text-2xl font-bold text-gray-900 mb-3 text-center">
              {type.title}
            </h2>

            <p class="text-gray-600 text-center mb-6">
              {type.description}
            </p>

            <ul class="space-y-3 mb-8">
              {#each type.benefits as benefit}
                <li class="flex items-start">
                  <CheckCircle class="text-green-500 mr-3 flex-shrink-0 mt-0.5" size={20} />
                  <span class="text-gray-700">{benefit}</span>
                </li>
              {/each}
            </ul>

            <button
              type="button"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 px-6 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg"
            >
              Get Started as {type.title}
            </button>
          </div>
        {/each}
      </div>

      <div class="text-center mt-12">
        <p class="text-gray-600">
          Already have an account?
          <a href="/login" class="text-blue-600 hover:text-blue-700 font-medium">
            Sign in here
          </a>
        </p>
      </div>

    {:else}
      <!-- Step 2: Registration Form -->
      <div class="max-w-md mx-auto">
        <div class="bg-white rounded-2xl shadow-xl p-8 md:p-10 border border-gray-100">
          <!-- Header -->
          <div class="text-center mb-8">
            <button
              type="button"
              onclick={goBackToUserType}
              class="text-sm text-gray-600 hover:text-blue-600 mb-4 inline-flex items-center"
            >
              ← Back to user type selection
            </button>

            <div class="flex justify-center mb-4">
              <div class="p-3 bg-blue-100 rounded-full">
                {#if userType === 'jobseeker'}
                  <UserCircle class="text-blue-600" size={32} />
                {:else}
                  <Building2 class="text-blue-600" size={32} />
                {/if}
              </div>
            </div>

            <h2 class="text-3xl font-bold text-gray-900 mb-2">
              Create Your Account
            </h2>
            <p class="text-gray-600">
              {userType === 'jobseeker' ? 'Start your job search journey' : 'Begin hiring top talent'}
            </p>
          </div>

          <!-- OAuth Options -->
          <div class="space-y-3 mb-6">
            <button
              type="button"
              onclick={() => handleOAuthLogin('google')}
              disabled={isLoading}
              class="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5 mr-3" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span class="text-gray-700 font-medium">Continue with Google</span>
            </button>

            <button
              type="button"
              onclick={() => handleOAuthLogin('facebook')}
              disabled={isLoading}
              class="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm bg-white hover:bg-gray-50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-5 h-5 mr-3" fill="#1877F2" viewBox="0 0 24 24">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
              </svg>
              <span class="text-gray-700 font-medium">Continue with Facebook</span>
            </button>
          </div>

          <div class="relative mb-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white text-gray-500">Or register with email</span>
            </div>
          </div>

          <!-- Registration Form -->
          <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-5">
            <!-- Full Name -->
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 mb-2">
                Full Name *
              </label>
              <div class="relative">
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User class="text-gray-400" size={20} />
                </div>
                <input
                  id="fullName"
                  type="text"
                  bind:value={fullName}
                  placeholder="John Doe"
                  class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.fullName}
                />
              </div>
              {#if errors.fullName}
                <p class="mt-1 text-sm text-red-600">{errors.fullName}</p>
              {/if}
            </div>

            <!-- Company Name (Recruiters only) -->
            {#if userType === 'recruiter'}
              <div>
                <label for="companyName" class="block text-sm font-medium text-gray-700 mb-2">
                  Company Name *
                </label>
                <div class="relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Building2 class="text-gray-400" size={20} />
                  </div>
                  <input
                    id="companyName"
                    type="text"
                    bind:value={companyName}
                    placeholder="Acme Corporation"
                    class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                    class:border-red-500={errors.companyName}
                  />
                </div>
                {#if errors.companyName}
                  <p class="mt-1 text-sm text-red-600">{errors.companyName}</p>
                {/if}
              </div>
            {/if}

            <!-- Email -->
            <div>
              <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
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
                />
              </div>
              {#if errors.email}
                <p class="mt-1 text-sm text-red-600">{errors.email}</p>
              {/if}
            </div>

            <!-- Password -->
            <div>
              <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
                Password *
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
                Confirm Password *
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

            <!-- Terms and Conditions -->
            <div>
              <label class="flex items-start">
                <input
                  type="checkbox"
                  bind:checked={acceptTerms}
                  class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span class="ml-3 text-sm text-gray-600">
                  I agree to the
                  <a href="/terms" target="_blank" class="text-blue-600 hover:text-blue-700 font-medium">Terms of Service</a>
                  and
                  <a href="/privacy" target="_blank" class="text-blue-600 hover:text-blue-700 font-medium">Privacy Policy</a>
                </span>
              </label>
              {#if errors.terms}
                <p class="mt-1 text-sm text-red-600">{errors.terms}</p>
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
                Creating Account...
              {:else}
                Create Account
              {/if}
            </button>
          </form>

          <!-- Sign In Link -->
          <div class="mt-6 text-center">
            <p class="text-sm text-gray-600">
              Already have an account?
              <a href="/login" class="text-blue-600 hover:text-blue-700 font-medium">
                Sign in
              </a>
            </p>
          </div>
        </div>

        <!-- Additional Info -->
        <div class="mt-8 text-center">
          <p class="text-sm text-gray-500">
            By signing up, you'll get access to exclusive features and personalized job recommendations.
          </p>
        </div>
      </div>
    {/if}

  </div>
</div>

<style>
  .animate-fade-in {
    animation: fadeIn 0.6s ease-out forwards;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
</style>
