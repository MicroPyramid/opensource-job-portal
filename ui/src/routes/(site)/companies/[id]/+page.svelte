<script>
  import { page } from '$app/stores';
  import { MapPin, Users, Calendar, Briefcase, Star, Heart, ExternalLink, Globe, Mail, Phone, Building2, DollarSign, TrendingUp, Award, CheckCircle } from '@lucide/svelte';

  // Get company ID from route params
  $: companyId = $page.params.id;

  // Mock company data - will be replaced with API call
  const company = {
    id: 1,
    name: 'TechCorp Solutions',
    logo: '🏢',
    tagline: 'Building the future of enterprise software',
    description: 'TechCorp Solutions is a leading provider of enterprise software solutions, helping businesses transform digitally and achieve operational excellence. With over 15 years of experience, we serve Fortune 500 companies across the globe.',
    industry: 'Technology',
    location: 'San Francisco, CA',
    size: '500-1000',
    founded: 2008,
    website: 'https://techcorp.example.com',
    email: 'careers@techcorp.example.com',
    phone: '+1 (555) 123-4567',
    rating: 4.5,
    reviewCount: 342,
    employeeGrowth: '+15%',
    featured: true,
    culture: {
      mission: 'To empower businesses with innovative technology solutions that drive growth and efficiency.',
      vision: 'To be the world\'s most trusted technology partner for enterprises.',
      values: [
        'Innovation First',
        'Customer Success',
        'Integrity & Trust',
        'Continuous Learning',
        'Collaborative Spirit'
      ]
    },
    benefits: [
      {
        icon: '🏥',
        title: 'Health & Wellness',
        description: 'Comprehensive health, dental, and vision insurance'
      },
      {
        icon: '💰',
        title: 'Competitive Salary',
        description: 'Above market compensation with equity options'
      },
      {
        icon: '🏖️',
        title: 'Flexible PTO',
        description: 'Unlimited paid time off and holidays'
      },
      {
        icon: '🏠',
        title: 'Remote Work',
        description: 'Hybrid and fully remote work options'
      },
      {
        icon: '📚',
        title: 'Learning Budget',
        description: '$2,000 annual budget for courses and conferences'
      },
      {
        icon: '🍽️',
        title: 'Free Meals',
        description: 'Catered lunch and fully stocked kitchen'
      }
    ],
    stats: [
      { label: 'Employees', value: '750+', icon: Users },
      { label: 'Open Positions', value: '24', icon: Briefcase },
      { label: 'Offices Worldwide', value: '8', icon: Building2 },
      { label: 'Years in Business', value: '15+', icon: Calendar }
    ]
  };

  // Mock job listings
  const companyJobs = [
    {
      id: 1,
      title: 'Senior Software Engineer',
      department: 'Engineering',
      location: 'San Francisco, CA',
      type: 'Full-time',
      remote: true,
      salary: '$120k - $180k',
      postedDate: '2 days ago',
      applicants: 45
    },
    {
      id: 2,
      title: 'Product Manager',
      department: 'Product',
      location: 'San Francisco, CA',
      type: 'Full-time',
      remote: true,
      salary: '$130k - $190k',
      postedDate: '1 week ago',
      applicants: 32
    },
    {
      id: 3,
      title: 'UX Designer',
      department: 'Design',
      location: 'Remote',
      type: 'Full-time',
      remote: true,
      salary: '$100k - $150k',
      postedDate: '3 days ago',
      applicants: 28
    },
    {
      id: 4,
      title: 'DevOps Engineer',
      department: 'Engineering',
      location: 'New York, NY',
      type: 'Full-time',
      remote: true,
      salary: '$110k - $160k',
      postedDate: '5 days ago',
      applicants: 19
    },
    {
      id: 5,
      title: 'Data Scientist',
      department: 'Data',
      location: 'San Francisco, CA',
      type: 'Full-time',
      remote: false,
      salary: '$140k - $200k',
      postedDate: '1 week ago',
      applicants: 52
    },
    {
      id: 6,
      title: 'Marketing Manager',
      department: 'Marketing',
      location: 'Remote',
      type: 'Full-time',
      remote: true,
      salary: '$90k - $130k',
      postedDate: '4 days ago',
      applicants: 38
    }
  ];

  let isFollowing = false;

  function toggleFollow() {
    isFollowing = !isFollowing;
    // TODO: Implement API call to follow/unfollow company
  }
</script>

<svelte:head>
  <title>{company.name} - Company Profile | HirePulse.in</title>
  <meta name="description" content={company.tagline} />
</svelte:head>

<!-- Company Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12 md:py-16">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex flex-col md:flex-row gap-6 items-start md:items-center">
      <!-- Company Logo -->
      <div class="text-6xl md:text-7xl bg-white rounded-2xl p-6 shadow-xl">
        {company.logo}
      </div>

      <!-- Company Info -->
      <div class="flex-1">
        <div class="flex items-start justify-between flex-wrap gap-4">
          <div>
            <h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-2">
              {company.name}
            </h1>
            <p class="text-lg md:text-xl text-blue-100 mb-4">
              {company.tagline}
            </p>

            <div class="flex flex-wrap gap-4 text-sm md:text-base">
              <div class="flex items-center gap-2">
                <Star class="text-yellow-400 fill-yellow-400" size={20} />
                <span class="font-semibold">{company.rating}</span>
                <span class="text-blue-200">({company.reviewCount} reviews)</span>
              </div>
              <div class="flex items-center gap-2">
                <MapPin size={20} />
                <span>{company.location}</span>
              </div>
              <div class="flex items-center gap-2">
                <Briefcase size={20} />
                <span>{company.industry}</span>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex gap-3">
            <button
              type="button"
              onclick={toggleFollow}
              class="flex items-center gap-2 {isFollowing ? 'bg-white text-blue-600' : 'bg-blue-500 text-white'} hover:bg-white hover:text-blue-600 font-semibold px-6 py-3 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl"
            >
              <Heart size={20} class={isFollowing ? 'fill-current' : ''} />
              {isFollowing ? 'Following' : 'Follow'}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Company Stats -->
<section class="py-8 bg-white border-b border-gray-100">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
      {#each company.stats as stat}
        <div class="text-center">
          <div class="flex justify-center mb-2">
            <div class="p-3 bg-blue-100 rounded-full">
              <stat.icon class="text-blue-600" size={24} />
            </div>
          </div>
          <div class="text-2xl md:text-3xl font-bold text-gray-800 mb-1">{stat.value}</div>
          <div class="text-sm text-gray-600">{stat.label}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid lg:grid-cols-3 gap-8">

      <!-- Left Column - Company Details -->
      <div class="lg:col-span-2 space-y-8">

        <!-- About Company -->
        <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <h2 class="text-2xl font-bold text-gray-800 mb-4">About {company.name}</h2>
          <p class="text-gray-600 leading-relaxed mb-6">
            {company.description}
          </p>

          <div class="grid md:grid-cols-2 gap-6">
            <!-- Mission -->
            <div>
              <h3 class="text-lg font-bold text-gray-800 mb-2 flex items-center gap-2">
                <TrendingUp class="text-blue-600" size={20} />
                Our Mission
              </h3>
              <p class="text-gray-600 text-sm">
                {company.culture.mission}
              </p>
            </div>

            <!-- Vision -->
            <div>
              <h3 class="text-lg font-bold text-gray-800 mb-2 flex items-center gap-2">
                <Award class="text-blue-600" size={20} />
                Our Vision
              </h3>
              <p class="text-gray-600 text-sm">
                {company.culture.vision}
              </p>
            </div>
          </div>
        </div>

        <!-- Core Values -->
        <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <h2 class="text-2xl font-bold text-gray-800 mb-6">Our Core Values</h2>
          <div class="grid md:grid-cols-2 gap-4">
            {#each company.culture.values as value}
              <div class="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
                <CheckCircle class="text-blue-600 flex-shrink-0" size={20} />
                <span class="text-gray-800 font-medium">{value}</span>
              </div>
            {/each}
          </div>
        </div>

        <!-- Benefits & Perks -->
        <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <h2 class="text-2xl font-bold text-gray-800 mb-6">Benefits & Perks</h2>
          <div class="grid md:grid-cols-2 gap-6">
            {#each company.benefits as benefit}
              <div class="flex gap-4">
                <div class="text-3xl flex-shrink-0">{benefit.icon}</div>
                <div>
                  <h3 class="text-lg font-bold text-gray-800 mb-1">{benefit.title}</h3>
                  <p class="text-sm text-gray-600">{benefit.description}</p>
                </div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Open Positions -->
        <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold text-gray-800">Open Positions</h2>
            <span class="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm font-semibold">
              {companyJobs.length} Jobs
            </span>
          </div>

          <div class="space-y-4">
            {#each companyJobs as job}
              <a
                href="/jobs/{job.id}"
                class="group block p-6 border border-gray-200 rounded-lg hover:border-blue-300 hover:shadow-md transition-all duration-200"
              >
                <div class="flex items-start justify-between mb-3">
                  <div class="flex-1">
                    <h3 class="text-lg font-bold text-gray-800 mb-1 group-hover:text-blue-600 transition-colors">
                      {job.title}
                    </h3>
                    <div class="flex flex-wrap gap-2 text-sm text-gray-600">
                      <span class="flex items-center gap-1">
                        <Briefcase size={14} />
                        {job.department}
                      </span>
                      <span>•</span>
                      <span class="flex items-center gap-1">
                        <MapPin size={14} />
                        {job.location}
                      </span>
                      {#if job.remote}
                        <span class="bg-green-100 text-green-700 px-2 py-0.5 rounded-full text-xs font-medium">
                          Remote
                        </span>
                      {/if}
                    </div>
                  </div>
                  <span class="text-blue-600 font-semibold flex-shrink-0">
                    {job.salary}
                  </span>
                </div>

                <div class="flex items-center justify-between text-sm">
                  <div class="flex gap-4 text-gray-500">
                    <span>{job.type}</span>
                    <span>•</span>
                    <span>{job.postedDate}</span>
                    <span>•</span>
                    <span>{job.applicants} applicants</span>
                  </div>
                  <span class="text-blue-600 group-hover:underline">Apply →</span>
                </div>
              </a>
            {/each}
          </div>

          <div class="mt-6 text-center">
            <a
              href="/jobs?company={company.id}"
              class="inline-block text-blue-600 hover:text-blue-700 font-semibold"
            >
              View All Open Positions →
            </a>
          </div>
        </div>

      </div>

      <!-- Right Column - Sidebar -->
      <div class="lg:col-span-1">
        <div class="sticky top-24 space-y-6">

          <!-- Company Info Card -->
          <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Company Information</h3>

            <div class="space-y-4">
              <div>
                <div class="text-sm text-gray-600 mb-1">Industry</div>
                <div class="font-medium text-gray-800">{company.industry}</div>
              </div>

              <div>
                <div class="text-sm text-gray-600 mb-1">Company Size</div>
                <div class="font-medium text-gray-800">{company.size} employees</div>
              </div>

              <div>
                <div class="text-sm text-gray-600 mb-1">Founded</div>
                <div class="font-medium text-gray-800">{company.founded}</div>
              </div>

              <div>
                <div class="text-sm text-gray-600 mb-1">Employee Growth</div>
                <div class="font-medium text-green-600 flex items-center gap-1">
                  <TrendingUp size={16} />
                  {company.employeeGrowth} YoY
                </div>
              </div>

              <div>
                <div class="text-sm text-gray-600 mb-1">Headquarters</div>
                <div class="font-medium text-gray-800">{company.location}</div>
              </div>
            </div>
          </div>

          <!-- Contact Card -->
          <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Contact</h3>

            <div class="space-y-3">
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                class="flex items-center gap-3 text-blue-600 hover:text-blue-700 transition-colors"
              >
                <Globe size={18} />
                <span class="text-sm">Visit Website</span>
                <ExternalLink size={14} class="ml-auto" />
              </a>

              <a
                href="mailto:{company.email}"
                class="flex items-center gap-3 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <Mail size={18} />
                <span class="text-sm">{company.email}</span>
              </a>

              <a
                href="tel:{company.phone}"
                class="flex items-center gap-3 text-gray-700 hover:text-blue-600 transition-colors"
              >
                <Phone size={18} />
                <span class="text-sm">{company.phone}</span>
              </a>
            </div>
          </div>

          <!-- Call to Action -->
          <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-lg p-6 text-white">
            <h3 class="text-lg font-bold mb-2">Interested in joining?</h3>
            <p class="text-sm text-blue-100 mb-4">
              Explore our open positions and find your perfect role.
            </p>
            <button
              type="button"
              onclick={() => document.getElementById('open-positions')?.scrollIntoView({ behavior: 'smooth' })}
              class="w-full bg-white text-blue-600 hover:bg-blue-50 font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
            >
              View Open Positions
            </button>
          </div>

        </div>
      </div>

    </div>
  </div>
</section>
