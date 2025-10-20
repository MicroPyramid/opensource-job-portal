<script lang="ts">
  import '../../app.css';
  import { Menu, X, Mail, MapPin, LogOut, ChevronDown, Twitter, Linkedin, Facebook } from '@lucide/svelte';
  import { authStore } from '$lib/stores/auth';
  import Toast from '$lib/components/Toast.svelte';
  import type { PageData } from './$types';

  // Receive server-side auth data and children
  let { data, children }: { data: PageData, children: any } = $props();

  let mobileMenuOpen = $state(false);
  let latestJobsDropdownOpen = $state(false);

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
  }

  function toggleLatestJobsDropdown() {
    latestJobsDropdownOpen = !latestJobsDropdownOpen;
  }

  async function handleLogout() {
    await authStore.logout();
  }

  // Close dropdowns when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    if (latestJobsDropdownOpen && !target.closest('.latest-jobs-menu')) {
      latestJobsDropdownOpen = false;
    }
  }

  // Initialize auth store from server data (SSR-compatible)
  // Use $derived to compute auth state from both server data and store
  // Server data is used for initial SSR, then store takes over on client
  $effect(() => {
    // Initialize auth store with server data if authenticated on first mount
    if (data.isAuthenticated && data.user) {
      // Only update if store doesn't already have this user
      if (!$authStore.isAuthenticated || $authStore.user?.id !== data.user.id) {
        authStore.login(data.user);
      }
    }
  });

  // Determine which auth state to display (prefer server data during SSR)
  let isAuthenticated = $derived(data.isAuthenticated || $authStore.isAuthenticated);
  let user = $derived(data.user || $authStore.user);

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
    { name: 'IT-Software', slug: 'it-software' },
    { name: 'BPO', slug: 'bpo' },
    { name: 'Education', slug: 'education' },
    { name: 'Banking', slug: 'banking' },
    { name: 'Sales & Marketing', slug: 'sales' },
    { name: 'Travel & Hotels', slug: 'travel' },
    { name: 'Accounting', slug: 'accounting' },
    { name: 'Medical', slug: 'medical' },
    { name: 'Other', slug: 'other' },
    { name: 'Advertising', slug: 'advertising' },
    { name: 'Construction', slug: 'construction' },
    { name: 'Automobile', slug: 'automobile' },
    { name: 'Aviation', slug: 'aviation' },
    { name: 'Freshers', slug: 'freshers' },
    { name: 'IT-Hardware', slug: 'it-hardware' },
    { name: 'Recruitment', slug: 'recruitment' },
    { name: 'Digital Marketing', slug: 'digital-marketing' }
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

</script>

<svelte:window onclick={handleClickOutside} />

<div class="min-h-screen flex flex-col bg-gray-50 text-gray-800">
  <!-- Header -->
  <header class="bg-white shadow-sm sticky top-0 z-50">
    <nav class="container mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <a href="/" class="flex items-center space-x-2 hover:opacity-90 transition-opacity duration-200">
          <img src="/logo.png" alt="PeelJobs" class="h-8 md:h-10 w-auto" />
          <span class="text-xl md:text-2xl font-bold text-blue-600">PeelJobs</span>
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
                    <a href="/jobs/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Skills</a>
                    <ul class="space-y-1.5">
                      {#each skills as skill}
                        <li>
                          <a href="/jobs/?skills={skill.slug}" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs For {skill.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Industry Column -->
                  <div class="w-48">
                    <a href="/jobs/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Industry</a>
                    <ul class="space-y-1.5">
                      {#each industries as industry}
                        <li>
                          <a href="/jobs/?industry={industry.slug}" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs For {industry.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Location Column -->
                  <div class="w-48">
                    <a href="/jobs/" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Location</a>
                    <ul class="space-y-1.5">
                      {#each locations as location}
                        <li>
                          <a href="/jobs/?location={location.slug}" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Jobs in {location.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Internship Column -->
                  <div class="w-48">
                    <a href="/jobs/?job_type=internship" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Internship</a>
                    <ul class="space-y-1.5">
                      {#each internshipCities as city}
                        <li>
                          <a href="/jobs/?job_type=internship&location={city.slug}" class="text-gray-600 hover:text-blue-600 text-xs block">
                            Internship Jobs in {city.name}
                          </a>
                        </li>
                      {/each}
                    </ul>
                  </div>

                  <!-- Fresher Column -->
                  <div class="w-48">
                    <a href="/jobs/?fresher=true" class="block font-semibold text-gray-900 mb-3 hover:text-blue-600 text-sm">Fresher</a>
                    <ul class="space-y-1.5">
                      {#each skills as skill}
                        <li>
                          <a href="/jobs/?fresher=true&skills={skill.slug}" class="text-gray-600 hover:text-blue-600 text-xs block">
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

          <a href="/jobs/?fresher=true" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Fresher Jobs
          </a>
          <a href="/jobs/?is_remote=true" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Remote Jobs
          </a>
          <a href="/jobs/?job_type=internship" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Internship
          </a>
          <a href="/companies/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
            Companies
          </a>
        </div>

        <!-- Auth Section -->
        <div class="hidden lg:flex items-center space-x-3">
          {#if isAuthenticated && user}
            <!-- User Profile Picture -->
            {#if user.photo || user.profile_pic}
              <img
                src={user.photo || user.profile_pic}
                alt={user.first_name}
                class="w-10 h-10 rounded-full border-2 border-gray-300"
              />
            {:else}
              <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                {user.first_name?.charAt(0) || user.email?.charAt(0) || 'U'}
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
            <a href="/login/" class="text-gray-700 hover:text-blue-600 transition-colors duration-200 px-3 py-2 text-sm">
              Login
            </a>
            <a href="/register/" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors duration-200 text-sm font-medium">
              Register
            </a>
            <a href="/employer/" class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200 text-sm font-medium">
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
          {#if isAuthenticated && user}
            <!-- User Info (Mobile) -->
            <div class="px-3 py-3 mb-3 bg-gray-100 rounded">
              <div class="flex items-center space-x-3">
                {#if user.photo || user.profile_pic}
                  <img
                    src={user.photo || user.profile_pic}
                    alt={user.first_name}
                    class="w-10 h-10 rounded-full border-2 border-gray-300"
                  />
                {:else}
                  <div class="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
                    {user.first_name?.charAt(0) || user.email?.charAt(0) || 'U'}
                  </div>
                {/if}
                <div>
                  <p class="text-sm font-semibold text-gray-900">{user.first_name} {user.last_name}</p>
                  <p class="text-xs text-gray-600 truncate">{user.email}</p>
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

            <a href="/jobs/?fresher=true" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Fresher Jobs
            </a>
            <a href="/jobs/?is_remote=true" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Remote Jobs
            </a>
            <a href="/jobs/?job_type=internship" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Internship
            </a>
            <a href="/companies/" class="text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
              Companies
            </a>

            {#if isAuthenticated && user}
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
                <a href="/login/" class="block text-gray-700 hover:text-blue-600 py-2 px-3 rounded hover:bg-gray-100 transition-colors duration-200 text-sm">
                  Login
                </a>
                <a href="/register/" class="block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors duration-200 text-sm font-medium text-center">
                  Register
                </a>
                <a href="/employer/" class="block bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition-colors duration-200 text-sm font-medium text-center">
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
    {@render children()}
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
            <a
              href="https://x.com/peeljobs"
              class="text-gray-400 hover:text-blue-400 transition-colors duration-200"
              aria-label="PeelJobs on Twitter"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Twitter size={20} />
            </a>
            <a
              href="https://linkedin.com/company/peeljobs"
              class="text-gray-400 hover:text-blue-400 transition-colors duration-200"
              aria-label="PeelJobs on LinkedIn"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Linkedin size={20} />
            </a>
            <a
              href="https://facebook.com/peeljobs"
              class="text-gray-400 hover:text-blue-400 transition-colors duration-200"
              aria-label="PeelJobs on Facebook"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Facebook size={20} />
            </a>
          </div>
        </div>
        
        <!-- Quick Links -->
        <div>
          <h5 class="font-bold mb-4 text-lg">For Job Seekers</h5>
          <ul class="space-y-2">
            <li><a href="/jobs/" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Browse Jobs</a></li>
          </ul>
        </div>
        
        <!-- For Employers -->
        <div>
          <h5 class="font-bold mb-4 text-lg">For Employers</h5>
          <ul class="space-y-2">
            <li><a href="https://recruiter.peeljobs.com" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Post a Job</a></li>
            <li><a href="https://recruiter.peeljobs.com/dashboard" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Employer Dashboard</a></li>
            <li><a href="/pricing/" class="text-gray-300 hover:text-blue-400 transition-colors duration-200">Pricing Plans</a></li>
          </ul>
        </div>
        
        <!-- Contact Info -->
        <div>
          <h5 class="font-bold mb-4 text-lg">Contact Us</h5>
          <div class="space-y-3">
            <div class="flex items-center space-x-3">
              <Mail size={16} class="text-blue-400" />
              <a href="mailto:peeljobs@micropyramid.com" class="text-gray-300 hover:text-blue-400 transition-colors">peeljobs@micropyramid.com</a>
            </div>
            <div class="flex items-center space-x-3">
              <MapPin size={16} class="text-blue-400" />
              <span class="text-gray-300">Hyderabad, Telangana, India</span>
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
          <div class="flex flex-wrap justify-center md:justify-end gap-4 md:gap-6 text-sm">
            <a href="/about/" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">About Us</a>
            <a href="/privacy/" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Privacy Policy</a>
            <a href="/terms/" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Terms & Conditions</a>
            <a href="/contact/" class="text-gray-400 hover:text-blue-400 transition-colors duration-200">Contact Us</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</div>

<!-- Toast Notifications -->
<Toast />
