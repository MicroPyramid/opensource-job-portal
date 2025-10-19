<script>
  import '../../app.css';
  import { page } from '$app/stores';
  import { Menu, X, Phone, Mail, MapPin, User, LogOut, ChevronDown } from '@lucide/svelte';
  import { authStore } from '$lib/stores/auth';
  import Toast from '$lib/components/Toast.svelte';

  let mobileMenuOpen = false;
  let userMenuOpen = false;

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function toggleUserMenu() {
    userMenuOpen = !userMenuOpen;
  }

  async function handleLogout() {
    await authStore.logout();
    userMenuOpen = false;
  }

  // Close user menu when clicking outside
  function handleClickOutside(event) {
    if (userMenuOpen && !event.target.closest('.user-menu-container')) {
      userMenuOpen = false;
    }
  }
</script>

<svelte:window onclick={handleClickOutside} />

<div class="min-h-screen flex flex-col bg-gray-50 text-gray-800">
  <!-- Header -->
  <header class="bg-white shadow-lg sticky top-0 z-50 border-b border-gray-100">
    <nav class="container mx-auto px-4 lg:px-6 py-4">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <a href="/" class="text-2xl lg:text-3xl font-bold text-blue-600 hover:text-blue-700 transition-colors duration-200">
          PeelJobs
        </a>

        <!-- Desktop Navigation -->
        <div class="hidden md:flex items-center space-x-8">
          <a href="/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium {$page.url.pathname === '/' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : ''}">
            Home
          </a>
          <a href="/jobs" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium {$page.url.pathname === '/jobs' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : ''}">
            Find Jobs
          </a>
          <a href="/post-job" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium {$page.url.pathname === '/post-job' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : ''}">
            Post a Job
          </a>
          <a href="/companies" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium {$page.url.pathname === '/companies' ? 'text-blue-600 border-b-2 border-blue-600 pb-1' : ''}">
            Companies
          </a>

          {#if $authStore.isAuthenticated && $authStore.user}
            <!-- User Menu Dropdown -->
            <div class="relative user-menu-container">
              <button
                onclick={toggleUserMenu}
                class="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors duration-200 font-medium"
              >
                {#if $authStore.user.photo || $authStore.user.profile_pic}
                  <img
                    src={$authStore.user.photo || $authStore.user.profile_pic}
                    alt={$authStore.user.first_name}
                    class="w-8 h-8 rounded-full border-2 border-blue-600"
                  />
                {:else}
                  <div class="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {$authStore.user.first_name?.charAt(0) || $authStore.user.email?.charAt(0) || 'U'}
                  </div>
                {/if}
                <span class="max-w-[100px] truncate">{$authStore.user.first_name || $authStore.user.email}</span>
                <ChevronDown size={16} class="transition-transform {userMenuOpen ? 'rotate-180' : ''}" />
              </button>

              {#if userMenuOpen}
                <div class="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50">
                  <div class="px-4 py-3 border-b border-gray-100">
                    <p class="text-sm font-semibold text-gray-900">{$authStore.user.first_name} {$authStore.user.last_name}</p>
                    <p class="text-xs text-gray-500 truncate">{$authStore.user.email}</p>
                  </div>

                  <a href="/profile" class="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">
                    <User size={16} class="mr-3" />
                    My Profile
                  </a>

                  <button
                    onclick={handleLogout}
                    class="w-full flex items-center px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                  >
                    <LogOut size={16} class="mr-3" />
                    Logout
                  </button>
                </div>
              {/if}
            </div>
          {:else}
            <a href="/login" class="bg-blue-600 text-white px-6 py-2.5 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium shadow-md hover:shadow-lg">
              Sign In
            </a>
          {/if}
        </div>
        
        <!-- Mobile Menu Button -->
        <button 
          class="md:hidden p-2 rounded-lg text-gray-600 hover:text-blue-600 hover:bg-gray-100 transition-colors duration-200"
          onclick={toggleMobileMenu}
        >
          {#if mobileMenuOpen}
            <X size={24} />
          {:else}
            <Menu size={24} />
          {/if}
        </button>
      </div>
      
      <!-- Mobile Navigation -->
      {#if mobileMenuOpen}
        <div class="md:hidden mt-4 pb-4 border-t border-gray-100 pt-4">
          {#if $authStore.isAuthenticated && $authStore.user}
            <!-- User Info (Mobile) -->
            <div class="px-3 py-3 mb-3 bg-blue-50 rounded-lg">
              <div class="flex items-center space-x-3">
                {#if $authStore.user.photo || $authStore.user.profile_pic}
                  <img
                    src={$authStore.user.photo || $authStore.user.profile_pic}
                    alt={$authStore.user.first_name}
                    class="w-10 h-10 rounded-full border-2 border-blue-600"
                  />
                {:else}
                  <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {$authStore.user.first_name?.charAt(0) || $authStore.user.email?.charAt(0) || 'U'}
                  </div>
                {/if}
                <div>
                  <p class="text-sm font-semibold text-gray-900">{$authStore.user.first_name} {$authStore.user.last_name}</p>
                  <p class="text-xs text-gray-600 truncate">{$authStore.user.email}</p>
                </div>
              </div>
            </div>
          {/if}

          <div class="flex flex-col space-y-3">
            <a href="/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 {$page.url.pathname === '/' ? 'text-blue-600 bg-blue-50' : ''}">
              Home
            </a>
            <a href="/jobs" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 {$page.url.pathname === '/jobs' ? 'text-blue-600 bg-blue-50' : ''}">
              Find Jobs
            </a>
            <a href="/post-job" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 {$page.url.pathname === '/post-job' ? 'text-blue-600 bg-blue-50' : ''}">
              Post a Job
            </a>
            <a href="/companies" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 {$page.url.pathname === '/companies' ? 'text-blue-600 bg-blue-50' : ''}">
              Companies
            </a>

            {#if $authStore.isAuthenticated && $authStore.user}
              <a href="/profile" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 flex items-center">
                <User size={16} class="mr-2" />
                My Profile
              </a>
              <button
                onclick={handleLogout}
                class="text-red-600 hover:bg-red-50 py-2 px-3 rounded-lg transition-colors duration-200 flex items-center text-left"
              >
                <LogOut size={16} class="mr-2" />
                Logout
              </button>
            {:else}
              <a href="/login" class="bg-blue-600 text-white px-4 py-2.5 rounded-lg hover:bg-blue-700 transition-colors duration-200 font-medium text-center mt-2">
                Sign In
              </a>
            {/if}
          </div>
        </div>
      {/if}
    </nav>
  </header>

  <!-- Main Content -->
  <main class="flex-grow">
    <slot />
  </main>

  <!-- Footer -->
  <footer class="bg-gray-900 text-white py-12 lg:py-16">
    <div class="container mx-auto px-4 lg:px-6">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-8">
        <!-- Company Info -->
        <div class="lg:col-span-1">
          <h3 class="text-2xl font-bold text-blue-400 mb-4">PeelJobs</h3>
          <p class="text-gray-300 mb-4 leading-relaxed">
            Connecting talent with opportunities. Find your dream job or the perfect candidate with ease.
          </p>
          <div class="flex space-x-3">
            <a href="#" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
            </a>
            <a href="#" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.174-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.719-.359-1.781c0-1.663.967-2.911 2.168-2.911 1.024 0 1.518.769 1.518 1.688 0 1.029-.653 2.567-.992 3.992-.285 1.193.6 2.165 1.775 2.165 2.128 0 3.768-2.245 3.768-5.487 0-2.861-2.063-4.869-5.008-4.869-3.41 0-5.409 2.562-5.409 5.199 0 1.033.394 2.143.889 2.741.099.12.112.225.085.345-.09.375-.293 1.199-.334 1.363-.053.225-.172.271-.402.165-1.495-.69-2.433-2.878-2.433-4.646 0-3.776 2.748-7.252 7.92-7.252 4.158 0 7.392 2.967 7.392 6.923 0 4.135-2.607 7.462-6.233 7.462-1.214 0-2.357-.629-2.748-1.378 0 0-.598 2.284-.744 2.840-.282 1.079-1.039 2.425-1.544 3.245C9.505 23.767 10.729 24 12.017 24c6.624 0 11.99-5.367 11.99-11.987C24.007 5.367 18.641.001 12.017.001z"/></svg>
            </a>
          </div>
        </div>
        
        <!-- Quick Links -->
        <div>
          <h5 class="font-bold mb-4 text-lg">For Job Seekers</h5>
          <ul class="space-y-2">
            <li><a href="/jobs" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Browse Jobs</a></li>
            <li><a href="/career-advice" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Career Advice</a></li>
            <li><a href="/resume-builder" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Resume Builder</a></li>
            <li><a href="/salary-guide" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Salary Guide</a></li>
          </ul>
        </div>
        
        <!-- For Employers -->
        <div>
          <h5 class="font-bold mb-4 text-lg">For Employers</h5>
          <ul class="space-y-2">
            <li><a href="/post-job" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Post a Job</a></li>
            <li><a href="/employer-dashboard" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Employer Dashboard</a></li>
            <li><a href="/pricing" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Pricing Plans</a></li>
            <li><a href="/talent-search" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Search Candidates</a></li>
          </ul>
        </div>
        
        <!-- Contact Info -->
        <div>
          <h5 class="font-bold mb-4 text-lg">Contact Us</h5>
          <div class="space-y-3">
            <div class="flex items-center space-x-3">
              <Phone size={16} class="text-blue-400" />
              <span class="text-gray-300">+1 (555) 123-4567</span>
            </div>
            <div class="flex items-center space-x-3">
              <Mail size={16} class="text-blue-400" />
              <span class="text-gray-300">hello@hirepulse.in</span>
            </div>
            <div class="flex items-center space-x-3">
              <MapPin size={16} class="text-blue-400" />
              <span class="text-gray-300">San Francisco, CA</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Bottom Footer -->
      <div class="border-t border-gray-700 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center">
          <p class="text-gray-400 text-sm mb-4 md:mb-0">
            &copy; {new Date().getFullYear()} PeelJobs. All rights reserved.
          </p>
          <div class="flex space-x-6 text-sm">
            <a href="/privacy-policy" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Privacy Policy</a>
            <a href="/terms-of-service" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Terms of Service</a>
            <a href="/cookie-policy" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Cookie Policy</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</div>

<!-- Toast Notifications -->
<Toast />
