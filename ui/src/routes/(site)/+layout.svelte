<script>
  import '../../app.css';
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { Menu, X, Phone, Mail, MapPin, User, LogOut, ChevronDown } from '@lucide/svelte';
  import { authStore } from '$lib/stores/auth';
  import Toast from '$lib/components/Toast.svelte';

  let mobileMenuOpen = false;
  let userMenuOpen = false;
  let latestJobsDropdownOpen = false;

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function toggleUserMenu() {
    userMenuOpen = !userMenuOpen;
  }

  function toggleLatestJobsDropdown() {
    latestJobsDropdownOpen = !latestJobsDropdownOpen;
  }

  async function handleLogout() {
    await authStore.logout();
    userMenuOpen = false;
  }

  // Close dropdowns when clicking outside
  function handleClickOutside(event) {
    if (userMenuOpen && !event.target.closest('.user-menu-container')) {
      userMenuOpen = false;
    }
    if (latestJobsDropdownOpen && !event.target.closest('.latest-jobs-menu')) {
      latestJobsDropdownOpen = false;
    }
  }

  // Validate auth state on mount
  onMount(() => {
    // If tokens exist but user is not in store, it means tokens might be invalid
    // The API client will handle token refresh automatically on next request
    if (typeof window !== 'undefined') {
      const hasTokens = localStorage.getItem('access_token') && localStorage.getItem('refresh_token');
      const hasUser = localStorage.getItem('user');

      // If we have tokens but no user data, clear everything to prevent errors
      if (hasTokens && !hasUser) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
  });

  // Sample data - in production, this would come from API
  const skills = [
    { name: 'Basic Computer Knowledge', slug: 'basic-computer-knowledge' },
    { name: 'Basic Computer Skills', slug: 'basic-computer-skills' },
    { name: 'Sales', slug: 'sales' },
    { name: 'Communication Skills', slug: 'communication-skills' },
    { name: 'Java', slug: 'java' },
    { name: 'JavaScript', slug: 'javascript' },
    { name: 'BPO', slug: 'bpo' },
    { name: 'PHP', slug: 'php' },
    { name: 'HTML', slug: 'html' },
    { name: 'Good Communication', slug: 'good-communication' },
    { name: 'ASP.NET', slug: 'asp-dot-net' },
    { name: 'jQuery', slug: 'jquery' },
    { name: 'Accounting', slug: 'accounting' },
    { name: 'CSS', slug: 'css' },
    { name: 'Marketing', slug: 'marketing' },
    { name: 'Business Development', slug: 'business-development' },
    { name: 'English Communication', slug: 'english-communication' }
  ];

  const industries = [
    { name: 'IT Services', slug: 'it-services-consulting-industry' },
    { name: 'BPO', slug: 'bpo-call-centre-industry' },
    { name: 'Advertising', slug: 'advertising-marketing-industry' },
    { name: 'Other', slug: 'other-industry' },
    { name: 'Education', slug: 'education-teaching-industry' },
    { name: 'Banking', slug: 'banking-industry' },
    { name: 'Hotels', slug: 'hotels-restaurants-travel-industry' },
    { name: 'Aerospace', slug: 'aerospace-aviation-industry' },
    { name: 'Healthcare', slug: 'healthcare-industry' },
    { name: 'Financial Services', slug: 'financial-services-industry' },
    { name: 'Consumer Goods', slug: 'consumer-goods-fmcg-industry' },
    { name: 'Engineering', slug: 'engineering-construction-industry' },
    { name: 'E-commerce', slug: 'e-commerce-internet-industry' },
    { name: 'Recruitment', slug: 'recruitment-industry' },
    { name: 'Automobile', slug: 'automobile-industry' },
    { name: 'IT-Hardware', slug: 'it-hardware-industry' },
    { name: 'Manufacturing Company', slug: 'manufacturing-company-industry' }
  ];

  const locations = [
    { name: 'Chennai', slug: 'chennai' },
    { name: 'Bangalore', slug: 'bangalore' },
    { name: 'Mumbai', slug: 'mumbai' },
    { name: 'Kolkata', slug: 'kolkata' },
    { name: 'Delhi', slug: 'delhi' },
    { name: 'Hyderabad', slug: 'hyderabad' },
    { name: 'Noida', slug: 'noida' },
    { name: 'Gurgaon', slug: 'gurgaon' },
    { name: 'Pune', slug: 'pune' },
    { name: 'Ahmedabad', slug: 'ahmedabad' },
    { name: 'Odisha', slug: 'odisha' },
    { name: 'Coimbatore', slug: 'coimbatore' },
    { name: 'Jaipur', slug: 'jaipur' },
    { name: 'Indore', slug: 'indore' },
    { name: 'Thane', slug: 'thane' },
    { name: 'Gujarat', slug: 'gujarat' },
    { name: 'Kochi', slug: 'kochi' }
  ];

  const internshipCities = [
    { name: 'Hyderabad', slug: 'hyderabad' },
    { name: 'Bangalore', slug: 'bangalore' },
    { name: 'Chennai', slug: 'chennai' },
    { name: 'Pune', slug: 'pune' },
    { name: 'Delhi', slug: 'delhi' },
    { name: 'Mumbai', slug: 'mumbai' },
    { name: 'Coimbatore', slug: 'coimbatore' },
    { name: 'Goa', slug: 'goa' },
    { name: 'Kanchipuram', slug: 'kanchipuram' },
    { name: 'Kerala', slug: 'kerala' },
    { name: 'Kochi', slug: 'kochi' },
    { name: 'Trivandrum', slug: 'trivandrum' },
    { name: 'Gujarat', slug: 'gujarat' },
    { name: 'Nasik', slug: 'nasik' },
    { name: 'Noida', slug: 'noida' },
    { name: 'Kolkata', slug: 'kolkata' },
    { name: 'Gurgaon', slug: 'gurgaon' }
  ];

  const companies = [
    { name: 'Sumukh Multigrains', slug: 'sumukh-multigrains' },
    { name: 'DIPS', slug: 'dips' },
    { name: 'MAC Technologies', slug: 'mac-technologies-pvt-ltd' },
    { name: 'Maximus Human Resources', slug: 'maximus-human-resources-pvt-ltd' },
    { name: 'Exovy Job Search', slug: 'exovy-job-search' },
    { name: 'Grape Services', slug: 'grape-services-pvt-ltd' },
    { name: 'TFG Vacations', slug: 'tfg-vacations-india-pvt-ltd' },
    { name: 'MAVEN INFOTECH', slug: 'maven-infotech-pvt-ltd' },
    { name: 'Alenam Technologies', slug: 'alenam-technologies-pvt-ltd' },
    { name: 'Tech Mahindra', slug: 'tech-mahindra-private-limited' },
    { name: 'Symplocos Solutions', slug: 'symplocos-solutions-limited' },
    { name: 'PRO HUNTERS', slug: 'pro-hunters' },
    { name: 'Regatta Recruiters', slug: 'regatta-recruiters' },
    { name: 'One Stop Career', slug: 'one-stop-career' },
    { name: 'HCL Technologies', slug: 'hcl-technologies-limited' },
    { name: 'ReadMind Info', slug: 'readmind-info-services' },
    { name: 'Human Life Consultancy', slug: 'human-life-consultancy' }
  ];
</script>

<svelte:window onclick={handleClickOutside} />

<div class="min-h-screen flex flex-col bg-gray-50 text-gray-800">
  <!-- Header -->
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <a href="/" class="text-xl md:text-2xl font-bold text-blue-600 hover:text-blue-700 transition-colors duration-200">
          Peeljobs
        </a>

        <!-- Desktop Navigation -->
        <div class="hidden lg:flex items-center space-x-1">
          <!-- Latest Jobs Dropdown -->
          <div class="relative latest-jobs-menu">
            <button
              onclick={toggleLatestJobsDropdown}
              class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm flex items-center space-x-1"
            >
              <span>Latest Jobs</span>
              <ChevronDown size={14} class="transition-transform {latestJobsDropdownOpen ? 'rotate-180' : ''}" />
            </button>

            {#if latestJobsDropdownOpen}
              <div class="absolute left-0 top-full mt-0 bg-white shadow-lg border border-gray-200 z-50 w-max">
                <div class="flex p-4 gap-6 max-w-6xl">
                  <!-- Skills Column -->
                  <div class="w-48">
                    <a href="/jobs-by-skill/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Skills</a>
                    <ul class="space-y-1.5">
                      {#each skills as skill}
                        <li>
                          <a href="/{skill.slug}-jobs/" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs For {skill.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Industry Column -->
                  <div class="w-48">
                    <a href="/jobs-by-industry/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Industry</a>
                    <ul class="space-y-1.5">
                      {#each industries as industry}
                        <li>
                          <a href="/{industry.slug}-jobs/" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs For {industry.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Location Column -->
                  <div class="w-48">
                    <a href="/jobs-by-location/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Location</a>
                    <ul class="space-y-1.5">
                      {#each locations as location}
                        <li>
                          <a href="/jobs-in-{location.slug}/" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs in {location.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Internship Column -->
                  <div class="w-48">
                    <a href="/internship-jobs/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Internship</a>
                    <ul class="space-y-1.5">
                      {#each internshipCities as city}
                        <li>
                          <a href="/internship-jobs-in-{city.slug}/" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Internship Jobs in {city.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Fresher Column -->
                  <div class="w-48">
                    <a href="/fresher-jobs/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Fresher</a>
                    <ul class="space-y-1.5">
                      {#each skills as skill}
                        <li>
                          <a href="/{skill.slug}-fresher-jobs/" class="text-gray-600 hover:text-blue-600 text-xs block">
                            {skill.name} Fresher Jobs
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>
                </div>
              </div>
            {/if}
          </div>

          <a href="/fresher-jobs/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Fresher Jobs
          </a>
          <a href="/walkin-jobs/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Walkin Jobs
          </a>
          {#if $authStore.isAuthenticated && $authStore.user && $authStore.user.user_type === 'JS'}
            <a href="/applied-jobs/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
              Applied Jobs
            </a>
          {/if}
          <a href="/internship-jobs/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Internship
          </a>
          <a href="/companies/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Companies
          </a>
          <a href="/recruiters/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Recruiters
          </a>
          <a href="/job-alerts/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Job Alerts
          </a>
        </div>

        <!-- Auth Section -->
        <div class="hidden lg:flex items-center space-x-3">
          {#if $authStore.isAuthenticated && $authStore.user}
            <!-- User Profile Picture -->
            {#if $authStore.user.photo || $authStore.user.profile_pic}
              <img
                src={$authStore.user.photo || $authStore.user.profile_pic}
                alt={$authStore.user.first_name}
                class="w-10 h-10 rounded-full border-2 border-gray-300"
              />
            {:else}
              <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                {$authStore.user.first_name?.charAt(0) || $authStore.user.email?.charAt(0) || 'U'}
              </div>
            {/if}

            <!-- Logout Button -->
            <button
              onclick={handleLogout}
              class="text-gray-700 hover:text-red-600 transition-colors duration-200 px-3 py-2 text-sm flex items-center space-x-1"
            >
              <LogOut size={16} />
              <span>Logout</span>
            </button>
          {:else}
            <a href="/login" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
              Login
            </a>
            <a href="/register" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors duration-200 text-sm font-medium">
              Register
            </a>
            <a href="/employer" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200 text-sm font-medium">
              Employer
            </a>
          {/if}
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="lg:hidden p-2 rounded text-gray-600 hover:text-blue-600 hover:bg-gray-100 transition-colors duration-200"
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
        <div class="lg:hidden mt-4 pb-4 border-t border-gray-200 pt-4">
          {#if $authStore.isAuthenticated && $authStore.user}
            <!-- User Info (Mobile) -->
            <div class="px-3 py-3 mb-3 bg-gray-100 rounded">
              <div class="flex items-center space-x-3">
                {#if $authStore.user.photo || $authStore.user.profile_pic}
                  <img
                    src={$authStore.user.photo || $authStore.user.profile_pic}
                    alt={$authStore.user.first_name}
                    class="w-10 h-10 rounded-full border-2 border-gray-300"
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

          <div class="flex flex-col space-y-2">
            <!-- Mobile Latest Jobs with simple list -->
            <div>
              <a href="/jobs/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm block font-medium">
                Latest Jobs
              </a>
            </div>

            <a href="/fresher-jobs/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Fresher Jobs
            </a>
            <a href="/walkin-jobs/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Walkin Jobs
            </a>
            {#if $authStore.isAuthenticated && $authStore.user && $authStore.user.user_type === 'JS'}
              <a href="/applied-jobs/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
                Applied Jobs
              </a>
            {/if}
            <a href="/internship-jobs/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Internship
            </a>
            <a href="/companies/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Companies
            </a>
            <a href="/recruiters/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Recruiters
            </a>
            <a href="/job-alerts/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Job Alerts
            </a>

            {#if $authStore.isAuthenticated && $authStore.user}
              <a href="/profile/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
                My Profile
              </a>
              <button
                onclick={handleLogout}
                class="text-red-600 hover:bg-red-50 py-2 px-3 rounded transition-colors duration-200 flex items-center space-x-2 text-left text-sm mt-2"
              >
                <LogOut size={16} />
                <span>Logout</span>
              </button>
            {:else}
              <div class="pt-3 space-y-2 border-t border-gray-200 mt-2">
                <a href="/login" class="block text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
                  Login
                </a>
                <a href="/register" class="block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors duration-200 text-sm font-medium text-center">
                  Register
                </a>
                <a href="/employer" class="block bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200 text-sm font-medium text-center">
                  Employer
                </a>
              </div>
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
