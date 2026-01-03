<script lang="ts">
  import "../../app.css";
  import {
    Menu,
    X,
    Mail,
    MapPin,
    LogOut,
    ChevronDown,
    Twitter,
    Linkedin,
    Facebook,
    User,
    FileText,
    Bookmark,
    FilePlus,
    MessageSquare,
    Search,
    Briefcase,
    Building2,
    Zap,
    Users,
    GraduationCap,
    Home,
  } from "@lucide/svelte";
  import { authStore } from "$lib/stores/auth";
  import Toast from "$lib/components/Toast.svelte";

  // Receive children snippet
  let { children }: { children: any } = $props();

  let mobileMenuOpen = $state(false);
  let latestJobsDropdownOpen = $state(false);
  let userMenuDropdownOpen = $state(false);
  let headerScrolled = $state(false);

  function toggleMobileMenu() {
    mobileMenuOpen = !mobileMenuOpen;
    if (mobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  }

  function toggleLatestJobsDropdown() {
    latestJobsDropdownOpen = !latestJobsDropdownOpen;
  }

  function toggleUserMenuDropdown() {
    userMenuDropdownOpen = !userMenuDropdownOpen;
  }

  async function handleLogout() {
    await authStore.logout();
    userMenuDropdownOpen = false;
  }

  // Close dropdowns when clicking outside
  function handleClickOutside(event: MouseEvent) {
    const target = event.target;
    if (!(target instanceof HTMLElement)) {
      return;
    }

    if (latestJobsDropdownOpen && !target.closest(".latest-jobs-menu")) {
      latestJobsDropdownOpen = false;
    }

    if (userMenuDropdownOpen && !target.closest(".user-menu")) {
      userMenuDropdownOpen = false;
    }
  }

  // Handle scroll for header elevation
  function handleScroll() {
    headerScrolled = window.scrollY > 10;
  }

  // Auth state comes from client-side store (tokens stored in localStorage)
  let isAuthenticated = $derived($authStore.isAuthenticated);
  let user = $derived($authStore.user);

  // Navigation items for mega menu - full data
  const skills = [
    { name: "Basic Computer Knowledge", slug: "basic-computer-knowledge" },
    { name: "Basic Computer Skills", slug: "basic-computer-skills" },
    { name: "Sales", slug: "sales" },
    { name: "Communication Skills", slug: "communication-skills" },
    { name: "Java", slug: "java" },
    { name: "JavaScript", slug: "javascript" },
    { name: "BPO", slug: "bpo" },
    { name: "PHP", slug: "php" },
    { name: "HTML", slug: "html" },
    { name: "Good Communication", slug: "good-communication" },
    { name: "ASP.NET", slug: "asp-dot-net" },
    { name: "jQuery", slug: "jquery" },
    { name: "Accounting", slug: "accounting" },
    { name: "CSS", slug: "css" },
    { name: "Marketing", slug: "marketing" },
    { name: "Business Development", slug: "business-development" },
    { name: "English Communication", slug: "english-communication" },
  ];

  const industries = [
    { name: "IT-Software", slug: "it-software" },
    { name: "BPO", slug: "bpo" },
    { name: "Education", slug: "education" },
    { name: "Banking", slug: "banking" },
    { name: "Sales & Marketing", slug: "sales" },
    { name: "Travel & Hotels", slug: "travel" },
    { name: "Accounting", slug: "accounting" },
    { name: "Medical", slug: "medical" },
    { name: "Other", slug: "other" },
    { name: "Advertising", slug: "advertising" },
    { name: "Construction", slug: "construction" },
    { name: "Automobile", slug: "automobile" },
    { name: "Aviation", slug: "aviation" },
    { name: "Freshers", slug: "freshers" },
    { name: "IT-Hardware", slug: "it-hardware" },
    { name: "Recruitment", slug: "recruitment" },
    { name: "Digital Marketing", slug: "digital-marketing" },
  ];

  const locations = [
    { name: "Chennai", slug: "chennai" },
    { name: "Bangalore", slug: "bangalore" },
    { name: "Mumbai", slug: "mumbai" },
    { name: "Kolkata", slug: "kolkata" },
    { name: "Delhi", slug: "delhi" },
    { name: "Hyderabad", slug: "hyderabad" },
    { name: "Noida", slug: "noida" },
    { name: "Gurgaon", slug: "gurgaon" },
    { name: "Pune", slug: "pune" },
    { name: "Ahmedabad", slug: "ahmedabad" },
    { name: "Odisha", slug: "odisha" },
    { name: "Coimbatore", slug: "coimbatore" },
    { name: "Jaipur", slug: "jaipur" },
    { name: "Indore", slug: "indore" },
    { name: "Thane", slug: "thane" },
    { name: "Gujarat", slug: "gujarat" },
    { name: "Kochi", slug: "kochi" },
  ];

  const internshipCities = [
    { name: "Hyderabad", slug: "hyderabad" },
    { name: "Bangalore", slug: "bangalore" },
    { name: "Chennai", slug: "chennai" },
    { name: "Pune", slug: "pune" },
    { name: "Delhi", slug: "delhi" },
    { name: "Mumbai", slug: "mumbai" },
    { name: "Coimbatore", slug: "coimbatore" },
    { name: "Goa", slug: "goa" },
    { name: "Kanchipuram", slug: "kanchipuram" },
    { name: "Kerala", slug: "kerala" },
    { name: "Kochi", slug: "kochi" },
    { name: "Trivandrum", slug: "trivandrum" },
    { name: "Gujarat", slug: "gujarat" },
    { name: "Nasik", slug: "nasik" },
    { name: "Noida", slug: "noida" },
    { name: "Kolkata", slug: "kolkata" },
    { name: "Gurgaon", slug: "gurgaon" },
  ];
</script>

<svelte:window onclick={handleClickOutside} onscroll={handleScroll} />

<div class="min-h-screen flex flex-col bg-white">
  <!-- Header -->
  <header
    class="bg-white sticky top-0 z-50 transition-shadow duration-200 {headerScrolled
      ? 'shadow-card'
      : 'border-b border-border'}"
  >
    <nav class="max-w-7xl mx-auto px-4 lg:px-8">
      <div class="flex justify-between items-center h-14">
        <!-- Logo -->
        <a href="/" data-sveltekit-reload class="flex items-center gap-2 group">
          <img src="/logo.png" alt="PeelJobs" class="h-8 w-auto" />
          <span class="text-xl font-semibold text-black">PeelJobs</span>
        </a>

        <!-- Desktop Navigation -->
        <div class="hidden lg:flex items-center gap-1">
          <!-- Jobs Mega Menu -->
          <div class="relative latest-jobs-menu">
            <button
              onclick={toggleLatestJobsDropdown}
              class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-muted rounded-full hover:bg-surface hover:text-black transition-colors"
            >
              <Search size={16} />
              <span>Find Jobs</span>
              <ChevronDown
                size={14}
                class="transition-transform {latestJobsDropdownOpen
                  ? 'rotate-180'
                  : ''}"
              />
            </button>

            {#if latestJobsDropdownOpen}
              <div
                class="absolute left-0 top-full mt-2 bg-white shadow-dropdown rounded-lg z-50 overflow-hidden animate-scale-in origin-top-left max-h-[85vh] overflow-y-auto border border-border"
              >
                <div class="p-6">
                  <div class="flex gap-6">
                    <!-- Skills Column -->
                    <div class="w-48 flex-shrink-0">
                      <div class="flex items-center gap-2 mb-3">
                        <div
                          class="w-7 h-7 rounded bg-primary-50 flex items-center justify-center"
                        >
                          <Zap size={14} class="text-primary-600" />
                        </div>
                        <a
                          href="/jobs/"
                          class="font-semibold text-black hover:text-primary-600 text-sm"
                          >Skills</a
                        >
                      </div>
                      <ul class="space-y-0.5">
                        {#each skills as skill}
                          <li>
                            <a
                              href="/jobs/?skills={skill.slug}"
                              class="block px-2 py-1.5 text-xs text-muted rounded hover:bg-primary-50 hover:text-primary-600 transition-colors"
                            >
                              Jobs For {skill.name}
                            </a>
                          </li>
                        {/each}
                      </ul>
                    </div>

                    <!-- Industry Column -->
                    <div class="w-48 flex-shrink-0">
                      <div class="flex items-center gap-2 mb-3">
                        <div
                          class="w-7 h-7 rounded bg-success-light flex items-center justify-center"
                        >
                          <Building2 size={14} class="text-success-600" />
                        </div>
                        <a
                          href="/jobs/"
                          class="font-semibold text-black hover:text-success-600 text-sm"
                          >Industry</a
                        >
                      </div>
                      <ul class="space-y-0.5">
                        {#each industries as industry}
                          <li>
                            <a
                              href="/jobs/?industry={industry.slug}"
                              class="block px-2 py-1.5 text-xs text-muted rounded hover:bg-success-light hover:text-success-600 transition-colors"
                            >
                              Jobs For {industry.name}
                            </a>
                          </li>
                        {/each}
                      </ul>
                    </div>

                    <!-- Location Column -->
                    <div class="w-44 flex-shrink-0">
                      <div class="flex items-center gap-2 mb-3">
                        <div
                          class="w-7 h-7 rounded bg-warning-light flex items-center justify-center"
                        >
                          <MapPin size={14} class="text-warning-600" />
                        </div>
                        <a
                          href="/jobs/"
                          class="font-semibold text-black hover:text-warning-600 text-sm"
                          >Location</a
                        >
                      </div>
                      <ul class="space-y-0.5">
                        {#each locations as location}
                          <li>
                            <a
                              href="/jobs/?location={location.slug}"
                              class="block px-2 py-1.5 text-xs text-muted rounded hover:bg-warning-light hover:text-warning-600 transition-colors"
                            >
                              Jobs in {location.name}
                            </a>
                          </li>
                        {/each}
                      </ul>
                    </div>

                    <!-- Internship Column -->
                    <div class="w-44 flex-shrink-0">
                      <div class="flex items-center gap-2 mb-3">
                        <div
                          class="w-7 h-7 rounded bg-error-light flex items-center justify-center"
                        >
                          <Users size={14} class="text-error-600" />
                        </div>
                        <a
                          href="/jobs/?job_type=internship"
                          class="font-semibold text-black hover:text-error-600 text-sm"
                          >Internship</a
                        >
                      </div>
                      <ul class="space-y-0.5">
                        {#each internshipCities as city}
                          <li>
                            <a
                              href="/jobs/?job_type=internship&location={city.slug}"
                              class="block px-2 py-1.5 text-xs text-muted rounded hover:bg-error-light hover:text-error-600 transition-colors"
                            >
                              Internship in {city.name}
                            </a>
                          </li>
                        {/each}
                      </ul>
                    </div>

                    <!-- Fresher Column -->
                    <div class="w-48 flex-shrink-0">
                      <div class="flex items-center gap-2 mb-3">
                        <div
                          class="w-7 h-7 rounded bg-primary-100 flex items-center justify-center"
                        >
                          <GraduationCap size={14} class="text-primary-700" />
                        </div>
                        <a
                          href="/jobs/?fresher=true"
                          class="font-semibold text-black hover:text-primary-700 text-sm"
                          >Fresher</a
                        >
                      </div>
                      <ul class="space-y-0.5">
                        {#each skills as skill}
                          <li>
                            <a
                              href="/jobs/?fresher=true&skills={skill.slug}"
                              class="block px-2 py-1.5 text-xs text-muted rounded hover:bg-primary-100 hover:text-primary-700 transition-colors"
                            >
                              {skill.name} Fresher Jobs
                            </a>
                          </li>
                        {/each}
                      </ul>
                    </div>
                  </div>
                </div>

                <!-- View All -->
                <div class="bg-surface-50 px-6 py-3 border-t border-border">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-3">
                      <a
                        href="/jobs/?is_remote=true"
                        class="flex items-center gap-1.5 px-3 py-1.5 bg-success-light text-success-600 rounded-full text-xs font-medium hover:bg-success-light/80 transition-colors"
                      >
                        <Home size={12} />
                        Remote Jobs
                      </a>
                    </div>
                    <a
                      href="/jobs/"
                      class="flex items-center gap-2 text-primary-600 font-semibold hover:text-primary-700 transition-colors text-sm"
                    >
                      <span>View All Jobs</span>
                      <ChevronDown size={14} class="-rotate-90" />
                    </a>
                  </div>
                </div>
              </div>
            {/if}
          </div>

          <a
            href="/jobs/?fresher=true"
            class="px-4 py-2 text-sm font-medium text-muted rounded-full hover:bg-surface hover:text-black transition-colors"
          >
            Fresher Jobs
          </a>
          <a
            href="/jobs/?is_remote=true"
            class="px-4 py-2 text-sm font-medium text-muted rounded-full hover:bg-surface hover:text-black transition-colors"
          >
            Remote Jobs
          </a>
          <a
            href="/jobs/?job_type=internship"
            class="px-4 py-2 text-sm font-medium text-muted rounded-full hover:bg-surface hover:text-black transition-colors"
          >
            Internship
          </a>
          <a
            href="/companies/"
            class="flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-muted rounded-full hover:bg-surface hover:text-black transition-colors"
          >
            <Building2 size={16} />
            <span>Companies</span>
          </a>
        </div>

        <!-- Auth Section -->
        <div class="hidden lg:flex items-center gap-2">
          {#if isAuthenticated && user}
            <!-- User Menu Dropdown -->
            <div class="relative user-menu">
              <button
                onclick={toggleUserMenuDropdown}
                class="flex items-center gap-2 p-1.5 rounded-full hover:bg-surface transition-colors"
              >
                {#if user.photo || user.profile_pic}
                  <img
                    src={user.photo || user.profile_pic}
                    alt={user.first_name}
                    class="w-8 h-8 rounded-full object-cover"
                  />
                {:else}
                  <div
                    class="w-8 h-8 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold text-sm"
                  >
                    {user.first_name?.charAt(0) || user.email?.charAt(0) || "U"}
                  </div>
                {/if}
                <ChevronDown
                  size={14}
                  class="text-muted transition-transform {userMenuDropdownOpen
                    ? 'rotate-180'
                    : ''}"
                />
              </button>

              {#if userMenuDropdownOpen}
                <div
                  class="absolute right-0 top-full mt-2 bg-white shadow-dropdown rounded-lg z-50 w-72 overflow-hidden animate-scale-in origin-top-right border border-border"
                >
                  <!-- User Info Header -->
                  <div class="px-4 py-4 bg-surface-50 border-b border-border">
                    <div class="flex items-center gap-3">
                      {#if user.photo || user.profile_pic}
                        <img
                          src={user.photo || user.profile_pic}
                          alt={user.first_name}
                          class="w-12 h-12 rounded-full object-cover"
                        />
                      {:else}
                        <div
                          class="w-12 h-12 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold"
                        >
                          {user.first_name?.charAt(0) ||
                            user.email?.charAt(0) ||
                            "U"}
                        </div>
                      {/if}
                      <div class="flex-1 min-w-0">
                        <p class="font-semibold text-black truncate">
                          {user.first_name}
                          {user.last_name}
                        </p>
                        <p class="text-sm text-muted truncate">{user.email}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Menu Items -->
                  <div class="py-2">
                    <a
                      href="/profile/"
                      class="flex items-center gap-3 px-4 py-2.5 text-muted hover:bg-surface hover:text-black transition-colors"
                    >
                      <User size={18} />
                      <span class="text-sm font-medium">My Profile</span>
                    </a>
                    <a
                      href="/applications/"
                      class="flex items-center gap-3 px-4 py-2.5 text-muted hover:bg-surface hover:text-black transition-colors"
                    >
                      <FileText size={18} />
                      <span class="text-sm font-medium">My Applications</span>
                    </a>
                    <a
                      href="/saved/"
                      class="flex items-center gap-3 px-4 py-2.5 text-muted hover:bg-surface hover:text-black transition-colors"
                    >
                      <Bookmark size={18} />
                      <span class="text-sm font-medium">Saved Jobs</span>
                    </a>
                    <a
                      href="/resume/"
                      class="flex items-center gap-3 px-4 py-2.5 text-muted hover:bg-surface hover:text-black transition-colors"
                    >
                      <FilePlus size={18} />
                      <span class="text-sm font-medium">My Resumes</span>
                    </a>
                    <a
                      href="/messages/"
                      class="flex items-center gap-3 px-4 py-2.5 text-muted hover:bg-surface hover:text-black transition-colors"
                    >
                      <MessageSquare size={18} />
                      <span class="text-sm font-medium">Messages</span>
                    </a>
                  </div>

                  <!-- Logout -->
                  <div class="border-t border-border py-2">
                    <button
                      onclick={handleLogout}
                      class="flex items-center gap-3 px-4 py-2.5 text-error-600 hover:bg-error-light transition-colors w-full"
                    >
                      <LogOut size={18} />
                      <span class="text-sm font-medium">Sign out</span>
                    </button>
                  </div>
                </div>
              {/if}
            </div>
          {:else}
            <a
              href="/login/"
              class="px-4 py-2 text-sm font-semibold text-primary-600 rounded-full hover:bg-primary-50 transition-colors"
            >
              Sign in
            </a>
            <a
              href="/register/"
              class="h-8 px-4 flex items-center text-sm font-semibold text-white bg-primary-600 rounded-full hover:bg-primary-700 transition-colors"
            >
              Join now
            </a>
            <a
              href="/employer/"
              class="h-8 px-4 flex items-center text-sm font-semibold text-primary-600 border border-primary-600 rounded-full hover:bg-primary-50 transition-colors"
            >
              For Employers
            </a>
          {/if}
        </div>

        <!-- Mobile Menu Button -->
        <button
          class="lg:hidden p-2 rounded-full text-muted hover:bg-surface transition-colors"
          onclick={toggleMobileMenu}
        >
          {#if mobileMenuOpen}
            <X size={24} />
          {:else}
            <Menu size={24} />
          {/if}
        </button>
      </div>
    </nav>

    <!-- Mobile Navigation -->
    {#if mobileMenuOpen}
      <div
        class="lg:hidden fixed inset-0 top-14 bg-white z-40 overflow-y-auto animate-fade-in"
      >
        <div class="px-4 py-6">
          {#if isAuthenticated && user}
            <!-- User Info (Mobile) -->
            <div class="mb-6 p-4 bg-surface-50 rounded-lg border border-border">
              <div class="flex items-center gap-3">
                {#if user.photo || user.profile_pic}
                  <img
                    src={user.photo || user.profile_pic}
                    alt={user.first_name}
                    class="w-12 h-12 rounded-full object-cover"
                  />
                {:else}
                  <div
                    class="w-12 h-12 rounded-full bg-primary-600 flex items-center justify-center text-white font-semibold"
                  >
                    {user.first_name?.charAt(0) || user.email?.charAt(0) || "U"}
                  </div>
                {/if}
                <div>
                  <p class="font-semibold text-black">
                    {user.first_name}
                    {user.last_name}
                  </p>
                  <p class="text-sm text-muted">{user.email}</p>
                </div>
              </div>
            </div>
          {/if}

          <!-- Quick Job Links -->
          <div class="mb-6">
            <p
              class="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-2"
            >
              Quick Access
            </p>
            <div class="grid grid-cols-3 gap-2">
              <a
                href="/jobs/"
                class="flex flex-col items-center gap-2 p-4 bg-primary-50 rounded-lg hover:bg-primary-100 transition-colors"
              >
                <Search size={20} class="text-primary-600" />
                <span class="text-xs font-medium text-primary-600"
                  >All Jobs</span
                >
              </a>
              <a
                href="/jobs/?fresher=true"
                class="flex flex-col items-center gap-2 p-4 bg-success-light rounded-lg hover:bg-success-light/80 transition-colors"
              >
                <GraduationCap size={20} class="text-success-600" />
                <span class="text-xs font-medium text-success-600">Fresher</span
                >
              </a>
              <a
                href="/jobs/?is_remote=true"
                class="flex flex-col items-center gap-2 p-4 bg-warning-light rounded-lg hover:bg-warning-light/80 transition-colors"
              >
                <Home size={20} class="text-warning-600" />
                <span class="text-xs font-medium text-warning-600">Remote</span>
              </a>
            </div>
          </div>

          <!-- Navigation Links -->
          <div class="space-y-1">
            <a
              href="/jobs/?job_type=internship"
              class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
            >
              <Users size={20} />
              <span class="font-medium">Internships</span>
            </a>
            <a
              href="/companies/"
              class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
            >
              <Building2 size={20} />
              <span class="font-medium">Companies</span>
            </a>
          </div>

          {#if isAuthenticated && user}
            <!-- User Menu Section (Mobile) -->
            <div class="mt-6 pt-6 border-t border-border">
              <p
                class="text-xs font-semibold text-muted uppercase tracking-wider mb-3 px-2"
              >
                My Account
              </p>
              <div class="space-y-1">
                <a
                  href="/profile/"
                  class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
                >
                  <User size={20} />
                  <span class="font-medium">My Profile</span>
                </a>
                <a
                  href="/applications/"
                  class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
                >
                  <FileText size={20} />
                  <span class="font-medium">My Applications</span>
                </a>
                <a
                  href="/saved/"
                  class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
                >
                  <Bookmark size={20} />
                  <span class="font-medium">Saved Jobs</span>
                </a>
                <a
                  href="/resume/"
                  class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
                >
                  <FilePlus size={20} />
                  <span class="font-medium">My Resumes</span>
                </a>
                <a
                  href="/messages/"
                  class="flex items-center gap-3 px-4 py-3 text-muted rounded-lg hover:bg-surface hover:text-black transition-colors"
                >
                  <MessageSquare size={20} />
                  <span class="font-medium">Messages</span>
                </a>
              </div>

              <button
                onclick={handleLogout}
                class="flex items-center gap-3 px-4 py-3 mt-2 text-error-600 rounded-lg hover:bg-error-light transition-colors w-full"
              >
                <LogOut size={20} />
                <span class="font-medium">Sign out</span>
              </button>
            </div>
          {:else}
            <div class="mt-6 pt-6 border-t border-border space-y-3">
              <a
                href="/login/"
                class="flex items-center justify-center w-full h-10 text-primary-600 font-semibold border border-primary-600 rounded-full hover:bg-primary-50 transition-colors"
              >
                Sign in
              </a>
              <a
                href="/register/"
                class="flex items-center justify-center w-full h-10 text-white font-semibold bg-primary-600 rounded-full hover:bg-primary-700 transition-colors"
              >
                Join now
              </a>
              <a
                href="/employer/"
                class="flex items-center justify-center w-full h-10 text-success-600 font-semibold border border-success-600 rounded-full hover:bg-success-light transition-colors"
              >
                For Employers
              </a>
            </div>
          {/if}
        </div>
      </div>
    {/if}
  </header>

  <!-- Main Content -->
  <main class="flex-grow">
    {@render children()}
  </main>

  <!-- Footer -->
  <footer class="bg-[#1D2226] text-white">
    <!-- Main Footer Content -->
    <div class="max-w-7xl mx-auto px-4 lg:px-8 py-12">
      <div
        class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10 lg:gap-8"
      >
        <!-- Brand Column -->
        <div class="lg:col-span-2">
          <a href="/" class="flex items-center gap-2 mb-5">
            <img src="/logo.png" alt="PeelJobs" class="h-8 w-auto" />
            <span class="text-xl font-semibold">PeelJobs</span>
          </a>
          <p class="text-gray-400 text-sm leading-relaxed mb-5 max-w-sm">
            India's trusted job platform connecting professionals with verified
            opportunities at top companies.
          </p>
          <div class="flex items-center gap-2">
            <a
              href="https://x.com/peeljobs"
              class="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-primary-600 hover:text-white transition-colors"
              aria-label="Follow us on Twitter"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Twitter size={16} />
            </a>
            <a
              href="https://linkedin.com/company/peeljobs"
              class="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-primary-600 hover:text-white transition-colors"
              aria-label="Follow us on LinkedIn"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Linkedin size={16} />
            </a>
            <a
              href="https://facebook.com/peeljobs"
              class="w-9 h-9 rounded-full bg-white/10 flex items-center justify-center text-gray-400 hover:bg-primary-600 hover:text-white transition-colors"
              aria-label="Follow us on Facebook"
              rel="noopener noreferrer"
              target="_blank"
            >
              <Facebook size={16} />
            </a>
          </div>
        </div>

        <!-- For Job Seekers -->
        <div>
          <h5 class="font-semibold text-white mb-4 text-sm">For Job Seekers</h5>
          <ul class="space-y-2.5">
            <li>
              <a
                href="/jobs/"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Browse All Jobs</a
              >
            </li>
            <li>
              <a
                href="/jobs/?fresher=true"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Fresher Jobs</a
              >
            </li>
            <li>
              <a
                href="/jobs/?is_remote=true"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Remote Jobs</a
              >
            </li>
            <li>
              <a
                href="/jobs/?job_type=internship"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Internships</a
              >
            </li>
            <li>
              <a
                href="/companies/"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Top Companies</a
              >
            </li>
          </ul>
        </div>

        <!-- For Employers -->
        <div>
          <h5 class="font-semibold text-white mb-4 text-sm">For Employers</h5>
          <ul class="space-y-2.5">
            <li>
              <a
                href="https://recruiter.peeljobs.com"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Post a Job</a
              >
            </li>
            <li>
              <a
                href="https://recruiter.peeljobs.com/dashboard"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Employer Dashboard</a
              >
            </li>
            <li>
              <a
                href="/pricing/"
                class="text-gray-400 hover:text-white transition-colors text-sm"
                >Pricing Plans</a
              >
            </li>
          </ul>
        </div>

        <!-- Contact Info -->
        <div>
          <h5 class="font-semibold text-white mb-4 text-sm">Get in Touch</h5>
          <div class="space-y-3">
            <a
              href="mailto:peeljobs@micropyramid.com"
              class="flex items-center gap-3 text-gray-400 hover:text-white transition-colors group"
            >
              <div
                class="w-8 h-8 rounded bg-white/10 flex items-center justify-center group-hover:bg-primary-600 transition-colors"
              >
                <Mail size={14} />
              </div>
              <span class="text-sm">peeljobs@micropyramid.com</span>
            </a>
            <div class="flex items-center gap-3 text-gray-400">
              <div
                class="w-8 h-8 rounded bg-white/10 flex items-center justify-center"
              >
                <MapPin size={14} />
              </div>
              <span class="text-sm">Hyderabad, Telangana, India</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Bottom Footer -->
    <div class="border-t border-white/10">
      <div class="max-w-7xl mx-auto px-4 lg:px-8 py-5">
        <div
          class="flex flex-col md:flex-row justify-between items-center gap-4"
        >
          <p class="text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} PeelJobs. All rights reserved.
          </p>
          <div class="flex flex-wrap justify-center gap-6 text-sm">
            <a
              href="/about/"
              class="text-gray-400 hover:text-white transition-colors">About</a
            >
            <a
              href="/privacy/"
              class="text-gray-400 hover:text-white transition-colors"
              >Privacy</a
            >
            <a
              href="/terms/"
              class="text-gray-400 hover:text-white transition-colors">Terms</a
            >
            <a
              href="/contact/"
              class="text-gray-400 hover:text-white transition-colors"
              >Contact</a
            >
          </div>
        </div>
      </div>
    </div>
  </footer>
</div>

<!-- Toast Notifications -->
<Toast />
