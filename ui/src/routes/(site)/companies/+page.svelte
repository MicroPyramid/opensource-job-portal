<script>
  import { Search, MapPin, Users, Briefcase, Building2, Star, TrendingUp, Filter } from '@lucide/svelte';

  // Mock data - will be replaced with API calls
  const featuredCompanies = [
    {
      id: 1,
      name: 'TechCorp Solutions',
      logo: '🏢',
      industry: 'Technology',
      location: 'San Francisco, CA',
      size: '500-1000',
      openJobs: 24,
      description: 'Leading provider of enterprise software solutions',
      featured: true,
      rating: 4.5
    },
    {
      id: 2,
      name: 'FinanceHub Inc',
      logo: '💰',
      industry: 'Finance',
      location: 'New York, NY',
      size: '1000-5000',
      openJobs: 18,
      description: 'Global financial services and investment banking',
      featured: true,
      rating: 4.3
    },
    {
      id: 3,
      name: 'HealthTech Innovations',
      logo: '🏥',
      industry: 'Healthcare',
      location: 'Boston, MA',
      size: '100-500',
      openJobs: 15,
      description: 'Revolutionizing healthcare through technology',
      featured: true,
      rating: 4.7
    },
    {
      id: 4,
      name: 'EduLearn Platform',
      logo: '📚',
      industry: 'Education',
      location: 'Austin, TX',
      size: '50-100',
      openJobs: 12,
      description: 'Online learning platform for professionals',
      featured: true,
      rating: 4.4
    }
  ];

  const allCompanies = [
    ...featuredCompanies,
    {
      id: 5,
      name: 'GreenEnergy Corp',
      logo: '🌱',
      industry: 'Energy',
      location: 'Seattle, WA',
      size: '500-1000',
      openJobs: 10,
      description: 'Sustainable energy solutions for the future',
      rating: 4.2
    },
    {
      id: 6,
      name: 'RetailMax',
      logo: '🛒',
      industry: 'Retail',
      location: 'Chicago, IL',
      size: '5000+',
      openJobs: 32,
      description: 'Leading retail chain with nationwide presence',
      rating: 4.0
    },
    {
      id: 7,
      name: 'CloudScale Systems',
      logo: '☁️',
      industry: 'Technology',
      location: 'Denver, CO',
      size: '100-500',
      openJobs: 8,
      description: 'Cloud infrastructure and DevOps solutions',
      rating: 4.6
    },
    {
      id: 8,
      name: 'MediaStream Inc',
      logo: '📺',
      industry: 'Media',
      location: 'Los Angeles, CA',
      size: '1000-5000',
      openJobs: 20,
      description: 'Digital media and streaming services',
      rating: 4.1
    },
    {
      id: 9,
      name: 'AutoDrive Technologies',
      logo: '🚗',
      industry: 'Automotive',
      location: 'Detroit, MI',
      size: '500-1000',
      openJobs: 14,
      description: 'Autonomous vehicle technology and innovation',
      rating: 4.5
    },
    {
      id: 10,
      name: 'FoodDelight Services',
      logo: '🍔',
      industry: 'Food & Beverage',
      location: 'Miami, FL',
      size: '100-500',
      openJobs: 16,
      description: 'Food delivery and restaurant management',
      rating: 3.9
    },
    {
      id: 11,
      name: 'TravelWise',
      logo: '✈️',
      industry: 'Travel',
      location: 'Orlando, FL',
      size: '500-1000',
      openJobs: 11,
      description: 'Travel booking and itinerary planning',
      rating: 4.3
    },
    {
      id: 12,
      name: 'CyberSecure Systems',
      logo: '🔒',
      industry: 'Security',
      location: 'Washington, DC',
      size: '100-500',
      openJobs: 19,
      description: 'Cybersecurity and data protection solutions',
      rating: 4.8
    }
  ];

  const industries = ['All', 'Technology', 'Finance', 'Healthcare', 'Education', 'Energy', 'Retail', 'Media', 'Automotive', 'Food & Beverage', 'Travel', 'Security'];
  const companySizes = ['All', '1-50', '50-100', '100-500', '500-1000', '1000-5000', '5000+'];
  const locations = ['All', 'San Francisco, CA', 'New York, NY', 'Boston, MA', 'Austin, TX', 'Seattle, WA', 'Chicago, IL', 'Denver, CO', 'Los Angeles, CA', 'Detroit, MI', 'Miami, FL', 'Orlando, FL', 'Washington, DC'];

  // Filter state
  let searchQuery = '';
  let selectedIndustry = 'All';
  let selectedSize = 'All';
  let selectedLocation = 'All';
  let showFilters = false;

  // Filtered companies
  $: filteredCompanies = allCompanies.filter(company => {
    const matchesSearch = !searchQuery ||
      company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      company.description.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesIndustry = selectedIndustry === 'All' || company.industry === selectedIndustry;
    const matchesSize = selectedSize === 'All' || company.size === selectedSize;
    const matchesLocation = selectedLocation === 'All' || company.location === selectedLocation;

    return matchesSearch && matchesIndustry && matchesSize && matchesLocation;
  });

  function toggleFilters() {
    showFilters = !showFilters;
  }

  function resetFilters() {
    searchQuery = '';
    selectedIndustry = 'All';
    selectedSize = 'All';
    selectedLocation = 'All';
  }
</script>

<svelte:head>
  <title>Companies - HirePulse.in</title>
  <meta name="description" content="Browse companies hiring on HirePulse.in. Find your next employer from top companies across various industries." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-16 md:py-20">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-4xl md:text-5xl font-bold mb-4 animate-fade-in-down">
        Discover Top Companies
      </h1>
      <p class="text-lg md:text-xl mb-8 text-blue-100 animate-fade-in-up">
        Explore companies hiring on HirePulse.in and find your perfect workplace
      </p>

      <!-- Search Bar -->
      <div class="bg-white rounded-xl shadow-2xl p-2 md:p-3 animate-fade-in">
        <div class="flex flex-col md:flex-row gap-2">
          <div class="flex-1 relative">
            <Search class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              bind:value={searchQuery}
              placeholder="Search companies by name or description..."
              class="w-full pl-12 pr-4 py-3 md:py-4 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-800 bg-gray-50 focus:bg-white transition-colors duration-200"
            />
          </div>
          <button
            type="button"
            onclick={toggleFilters}
            class="md:hidden flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors duration-200"
          >
            <Filter size={20} />
            Filters
          </button>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Stats Section -->
<section class="py-12 bg-white border-b border-gray-100">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
      <div>
        <div class="text-3xl lg:text-4xl font-bold text-blue-600 mb-2">{allCompanies.length}+</div>
        <div class="text-gray-600">Companies</div>
      </div>
      <div>
        <div class="text-3xl lg:text-4xl font-bold text-blue-600 mb-2">{allCompanies.reduce((sum, c) => sum + c.openJobs, 0)}+</div>
        <div class="text-gray-600">Open Jobs</div>
      </div>
      <div>
        <div class="text-3xl lg:text-4xl font-bold text-blue-600 mb-2">{industries.length - 1}</div>
        <div class="text-gray-600">Industries</div>
      </div>
      <div>
        <div class="text-3xl lg:text-4xl font-bold text-blue-600 mb-2">4.3</div>
        <div class="text-gray-600">Avg Rating</div>
      </div>
    </div>
  </div>
</section>

<!-- Featured Companies -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center justify-between mb-12">
      <div>
        <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-2">Featured Companies</h2>
        <p class="text-lg text-gray-600">Top employers actively hiring right now</p>
      </div>
      <TrendingUp class="text-blue-600" size={32} />
    </div>

    <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each featuredCompanies as company}
        <a
          href="/companies/{company.id}"
          class="group bg-white rounded-xl shadow-lg hover:shadow-2xl transition-all duration-300 p-6 border border-blue-100 hover:border-blue-300 hover:-translate-y-1"
        >
          <div class="flex items-start justify-between mb-4">
            <div class="text-4xl">{company.logo}</div>
            <div class="flex items-center gap-1 bg-blue-100 px-2 py-1 rounded-full">
              <Star class="text-yellow-500 fill-yellow-500" size={14} />
              <span class="text-sm font-medium text-gray-700">{company.rating}</span>
            </div>
          </div>

          <h3 class="text-xl font-bold text-gray-800 mb-2 group-hover:text-blue-600 transition-colors">
            {company.name}
          </h3>

          <div class="space-y-2 mb-4 text-sm text-gray-600">
            <div class="flex items-center gap-2">
              <Briefcase size={16} class="text-gray-400" />
              <span>{company.industry}</span>
            </div>
            <div class="flex items-center gap-2">
              <MapPin size={16} class="text-gray-400" />
              <span>{company.location}</span>
            </div>
            <div class="flex items-center gap-2">
              <Users size={16} class="text-gray-400" />
              <span>{company.size} employees</span>
            </div>
          </div>

          <p class="text-sm text-gray-600 mb-4 line-clamp-2">
            {company.description}
          </p>

          <div class="flex items-center justify-between pt-4 border-t border-gray-100">
            <span class="text-blue-600 font-semibold">{company.openJobs} Open Jobs</span>
            <span class="text-gray-400 group-hover:text-blue-600 transition-colors">View →</span>
          </div>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- All Companies -->
<section class="py-16 lg:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex flex-col lg:flex-row gap-8">

      <!-- Filters Sidebar - Desktop -->
      <aside class="hidden md:block w-full lg:w-64 flex-shrink-0">
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100 sticky top-24">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-lg font-bold text-gray-800">Filters</h3>
            <button
              type="button"
              onclick={resetFilters}
              class="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              Reset
            </button>
          </div>

          <div class="space-y-6">
            <!-- Industry Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <select
                bind:value={selectedIndustry}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {#each industries as industry}
                  <option value={industry}>{industry}</option>
                {/each}
              </select>
            </div>

            <!-- Company Size Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Company Size
              </label>
              <select
                bind:value={selectedSize}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {#each companySizes as size}
                  <option value={size}>{size} {size !== 'All' ? 'employees' : ''}</option>
                {/each}
              </select>
            </div>

            <!-- Location Filter -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <select
                bind:value={selectedLocation}
                class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                {#each locations as location}
                  <option value={location}>{location}</option>
                {/each}
              </select>
            </div>
          </div>
        </div>
      </aside>

      <!-- Mobile Filters -->
      {#if showFilters}
        <div class="md:hidden fixed inset-0 bg-black bg-opacity-50 z-50" onclick={toggleFilters}>
          <div class="bg-white rounded-t-3xl p-6 absolute bottom-0 left-0 right-0 max-h-[80vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-bold text-gray-800">Filters</h3>
              <button
                type="button"
                onclick={toggleFilters}
                class="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div class="space-y-6">
              <!-- Industry Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Industry
                </label>
                <select
                  bind:value={selectedIndustry}
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {#each industries as industry}
                    <option value={industry}>{industry}</option>
                  {/each}
                </select>
              </div>

              <!-- Company Size Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Company Size
                </label>
                <select
                  bind:value={selectedSize}
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {#each companySizes as size}
                    <option value={size}>{size} {size !== 'All' ? 'employees' : ''}</option>
                  {/each}
                </select>
              </div>

              <!-- Location Filter -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Location
                </label>
                <select
                  bind:value={selectedLocation}
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  {#each locations as location}
                    <option value={location}>{location}</option>
                  {/each}
                </select>
              </div>
            </div>

            <div class="flex gap-3 mt-6">
              <button
                type="button"
                onclick={resetFilters}
                class="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                Reset
              </button>
              <button
                type="button"
                onclick={toggleFilters}
                class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      {/if}

      <!-- Companies Grid -->
      <div class="flex-1">
        <div class="mb-6">
          <h2 class="text-2xl font-bold text-gray-800 mb-2">All Companies</h2>
          <p class="text-gray-600">
            {filteredCompanies.length} {filteredCompanies.length === 1 ? 'company' : 'companies'} found
          </p>
        </div>

        {#if filteredCompanies.length > 0}
          <div class="grid md:grid-cols-2 gap-6">
            {#each filteredCompanies as company}
              <a
                href="/companies/{company.id}"
                class="group bg-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 border border-gray-100 hover:border-blue-200 hover:-translate-y-1"
              >
                <div class="flex items-start gap-4 mb-4">
                  <div class="text-4xl">{company.logo}</div>
                  <div class="flex-1">
                    <h3 class="text-xl font-bold text-gray-800 mb-1 group-hover:text-blue-600 transition-colors">
                      {company.name}
                    </h3>
                    <div class="flex items-center gap-1">
                      <Star class="text-yellow-500 fill-yellow-500" size={14} />
                      <span class="text-sm font-medium text-gray-700">{company.rating}</span>
                      <span class="text-sm text-gray-500 ml-1">rating</span>
                    </div>
                  </div>
                </div>

                <p class="text-sm text-gray-600 mb-4 line-clamp-2">
                  {company.description}
                </p>

                <div class="grid grid-cols-2 gap-2 mb-4 text-sm text-gray-600">
                  <div class="flex items-center gap-2">
                    <Briefcase size={14} class="text-gray-400" />
                    <span>{company.industry}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <MapPin size={14} class="text-gray-400" />
                    <span>{company.location}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <Users size={14} class="text-gray-400" />
                    <span>{company.size}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <Building2 size={14} class="text-blue-600" />
                    <span class="text-blue-600 font-semibold">{company.openJobs} Jobs</span>
                  </div>
                </div>

                <div class="pt-4 border-t border-gray-100">
                  <span class="text-blue-600 font-medium group-hover:underline">
                    View Company Profile →
                  </span>
                </div>
              </a>
            {/each}
          </div>
        {:else}
          <div class="text-center py-16">
            <Building2 class="mx-auto text-gray-300 mb-4" size={64} />
            <h3 class="text-xl font-bold text-gray-800 mb-2">No companies found</h3>
            <p class="text-gray-600 mb-6">Try adjusting your filters or search query</p>
            <button
              type="button"
              onclick={resetFilters}
              class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors duration-200"
            >
              Reset Filters
            </button>
          </div>
        {/if}
      </div>
    </div>
  </div>
</section>

<style>
  .animate-fade-in-down {
    animation: fadeInDown 0.8s ease-out forwards;
  }

  .animate-fade-in-up {
    animation: fadeInUp 0.8s ease-out 0.2s forwards;
    opacity: 0;
  }

  .animate-fade-in {
    animation: fadeIn 1s ease-out 0.4s forwards;
    opacity: 0;
  }

  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
