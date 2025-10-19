<script>
  import { Search, Briefcase, Users, Star, MapPin, Brain, TrendingUp, Shield, Clock, ChevronRight, Building, DollarSign } from '@lucide/svelte';

  let jobKeyword = '';
  let location = '';

  const stats = [
    { label: 'Active Jobs', value: '50,000+', icon: Briefcase },
    { label: 'Happy Users', value: '100,000+', icon: Users },
    { label: 'Companies', value: '5,000+', icon: Building },
    { label: 'Success Rate', value: '95%', icon: TrendingUp }
  ];

  const featuredJobs = [
    { 
      id: 1, 
      title: 'Senior Software Engineer', 
      company: 'Tech Innovations Inc.', 
      location: 'San Francisco, CA', 
      salary: '$140k - $180k', 
      type: 'Full-time',
      tags: ['React', 'Node.js', 'AWS'],
      logo: 'https://via.placeholder.com/50?text=TI',
      posted: '2 days ago',
      applicants: 45
    },
    { 
      id: 2, 
      title: 'Product Manager', 
      company: 'Innovate Solutions', 
      location: 'New York, NY', 
      salary: '$130k - $160k', 
      type: 'Full-time',
      tags: ['Strategy', 'Analytics', 'Leadership'],
      logo: 'https://via.placeholder.com/50?text=IS',
      posted: '1 day ago',
      applicants: 67
    },
    { 
      id: 3, 
      title: 'UX/UI Designer', 
      company: 'Creative Studio Co.', 
      location: 'Remote', 
      salary: '$90k - $120k', 
      type: 'Contract',
      tags: ['Figma', 'Design Systems', 'User Research'],
      logo: 'https://via.placeholder.com/50?text=CS',
      posted: '3 days ago',
      applicants: 23
    },
    { 
      id: 4, 
      title: 'Data Scientist', 
      company: 'AI Analytics Corp.', 
      location: 'Austin, TX', 
      salary: '$120k - $150k', 
      type: 'Full-time',
      tags: ['Python', 'Machine Learning', 'SQL'],
      logo: 'https://via.placeholder.com/50?text=AA',
      posted: '1 day ago',
      applicants: 89
    },
  ];

  const testimonials = [
    { 
      id: 1, 
      name: 'Sarah Johnson', 
      role: 'Software Developer at Google', 
      quote: 'The AI matching was incredible! I found my dream job at Google within just one week of signing up. The platform made the entire process seamless.',
      avatar: 'https://via.placeholder.com/80?text=SJ',
      company: 'Google'
    },
    { 
      id: 2, 
      name: 'Michael Chen', 
      role: 'HR Director at Microsoft', 
      quote: 'As an employer, HirePulse.in has revolutionized our hiring process. The quality of candidates and the AI-powered matching saves us countless hours.',
      avatar: 'https://via.placeholder.com/80?text=MC',
      company: 'Microsoft'
    },
    {
      id: 3,
      name: 'Emily Rodriguez',
      role: 'Product Manager at Stripe',
      quote: 'The career resources and resume builder helped me land my dream role. The platform truly understands what modern job seekers need.',
      avatar: 'https://via.placeholder.com/80?text=ER',
      company: 'Stripe'
    }
  ];

  const jobCategories = [
    { name: 'Technology', count: '15,000+', icon: '💻' },
    { name: 'Marketing', count: '8,500+', icon: '📈' },
    { name: 'Design', count: '5,200+', icon: '🎨' },
    { name: 'Sales', count: '12,000+', icon: '💼' },
    { name: 'Healthcare', count: '6,800+', icon: '🏥' },
    { name: 'Finance', count: '9,300+', icon: '💰' }
  ];

  function handleSearch() {
    // In a real app, you'd navigate to a search results page
    if (jobKeyword || location) {
      alert(`Searching for: ${jobKeyword || 'All jobs'} in ${location || 'All locations'}`);
    } else {
      alert('Please enter a job title or location to search');
    }
  }
</script>

<svelte:head>
  <title>HirePulse.in - AI-Powered Job Matching Platform | Find Your Dream Job</title>
  <meta name="description" content="HirePulse.in uses advanced AI to match you with perfect job opportunities. Search thousands of jobs, get personalized recommendations, and accelerate your career growth." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 text-white py-16 md:py-24 lg:py-32 relative overflow-hidden">

  
  <div class="container mx-auto px-4 lg:px-6 relative z-10">
    <div class="text-center max-w-4xl mx-auto">
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight animate-fade-in-down">
        Find Your Dream Job with 
        <span class="text-yellow-400">AI-Powered</span> Precision
      </h1>
      <p class="text-lg md:text-xl lg:text-2xl mb-8 max-w-3xl mx-auto leading-relaxed animate-fade-in-up text-blue-100">
        Join thousands of professionals who've accelerated their careers with our intelligent job matching platform. Your perfect opportunity is just one search away.
      </p>
      
      <!-- Search Form -->
      <form onsubmit={handleSearch} class="max-w-4xl mx-auto bg-white p-4 sm:p-6 lg:p-8 rounded-xl shadow-2xl animate-fade-in">
        <div class="grid grid-cols-1 md:grid-cols-12 gap-4 items-end">
          <div class="md:col-span-5">
            <label for="job-search" class="block text-sm font-medium text-gray-700 mb-2 text-left">What job are you looking for?</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Briefcase class="text-gray-400" size={20} />
              </span>
              <input
                id="job-search"
                type="text"
                bind:value={jobKeyword}
                placeholder="Job title, skills, or company"
                class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 bg-gray-50 focus:bg-white transition-colors duration-200"
              />
            </div>
          </div>
          <div class="md:col-span-4">
            <label for="location-search" class="block text-sm font-medium text-gray-700 mb-2 text-left">Where?</label>
            <div class="relative">
              <span class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MapPin class="text-gray-400" size={20} />
              </span>
              <input
                id="location-search"
                type="text"
                bind:value={location}
                placeholder="City, state, or remote"
                class="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-700 bg-gray-50 focus:bg-white transition-colors duration-200"
              />
            </div>
          </div>
          <div class="md:col-span-3">
            <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition duration-200 ease-in-out transform hover:scale-105 shadow-lg hover:shadow-xl">
              <Search class="inline mr-2" size={20} />
              Search Jobs
            </button>
          </div>
        </div>
        <p class="text-gray-600 text-sm mt-4 text-center">Popular searches: Software Engineer, Product Manager, Data Scientist, UX Designer</p>
      </form>
    </div>
  </div>
</section>

<!-- Stats Section -->
<section class="py-12 bg-white border-b border-gray-200">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      {#each stats as stat}
        <div class="text-center">
          <div class="flex justify-center mb-3">
            <div class="p-3 bg-blue-100 rounded-full">
              <svelte:component this={stat.icon} class="text-blue-600" size={24} />
            </div>
          </div>
          <div class="text-2xl lg:text-3xl font-bold text-gray-800 mb-1">{stat.value}</div>
          <div class="text-gray-600 text-sm font-medium">{stat.label}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Platform Highlights -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-16">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Why Choose HirePulse.in?</h2>
      <p class="text-lg text-gray-600 max-w-2xl mx-auto">Experience the future of job searching with our cutting-edge features designed to accelerate your career.</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-blue-100 rounded-full">
            <Brain class="text-blue-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">AI-Powered Matching</h3>
        <p class="text-gray-600 text-center leading-relaxed">Our advanced algorithms analyze your skills, experience, and preferences to find the most relevant opportunities.</p>
      </div>
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-green-100 rounded-full">
            <Shield class="text-green-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Verified Companies</h3>
        <p class="text-gray-600 text-center leading-relaxed">All employers are thoroughly vetted to ensure you're applying to legitimate, high-quality opportunities.</p>
      </div>
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-purple-100 rounded-full">
            <Clock class="text-purple-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Fast Applications</h3>
        <p class="text-gray-600 text-center leading-relaxed">Apply to multiple jobs in minutes with our streamlined application process and smart autofill features.</p>
      </div>
    </div>
  </div>
</section>

<!-- Job Categories -->
<section class="py-16 lg:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Browse Jobs by Category</h2>
      <p class="text-lg text-gray-600">Explore opportunities across various industries and find your perfect match.</p>
    </div>
    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
      {#each jobCategories as category}
        <a href="/jobs?category={category.name.toLowerCase()}" class="group bg-gray-50 hover:bg-blue-50 p-6 rounded-xl text-center transition-all duration-300 hover:shadow-lg border border-gray-200 hover:border-blue-200">
          <div class="text-3xl mb-3">{category.icon}</div>
          <h3 class="font-semibold text-gray-800 group-hover:text-blue-600 mb-1">{category.name}</h3>
          <p class="text-sm text-gray-500">{category.count} jobs</p>
        </a>
      {/each}
    </div>
  </div>
</section>

<!-- Featured Jobs Section -->
<section class="py-16 lg:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Featured Job Opportunities</h2>
      <p class="text-lg text-gray-600">Discover hand-picked opportunities from top companies looking for talented professionals.</p>
    </div>
    <div class="grid md:grid-cols-2 xl:grid-cols-4 gap-6 mb-10">
      {#each featuredJobs as job (job.id)}
        <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100">
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center">
                <img src={job.logo} alt="{job.company} logo" class="w-12 h-12 rounded-lg mr-3 object-cover border border-gray-200">
                <div>
                  <h3 class="font-bold text-gray-800 text-lg leading-tight">{job.title}</h3>
                  <p class="text-gray-600 text-sm">{job.company}</p>
                </div>
              </div>
            </div>
            
            <div class="space-y-2 mb-4">
              <div class="flex items-center text-gray-600 text-sm">
                <MapPin size={14} class="mr-2 text-gray-400" />
                {job.location}
              </div>
              <div class="flex items-center text-gray-600 text-sm">
                <DollarSign size={14} class="mr-2 text-gray-400" />
                {job.salary}
              </div>
              <div class="flex items-center text-gray-600 text-sm">
                <Clock size={14} class="mr-2 text-gray-400" />
                {job.type} • {job.posted}
              </div>
            </div>
            
            <div class="flex flex-wrap gap-1 mb-4">
              {#each job.tags as tag}
                <span class="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded-full">{tag}</span>
              {/each}
            </div>
            
            <div class="flex items-center justify-between">
              <span class="text-xs text-gray-500">{job.applicants} applicants</span>
              <a href="/jobs/{job.id}" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition duration-200 text-sm font-medium inline-flex items-center">
                Apply Now
                <ChevronRight size={14} class="ml-1" />
              </a>
            </div>
          </div>
        </div>
      {/each}
    </div>
    <div class="text-center">
      <a href="/jobs" class="inline-flex items-center bg-transparent hover:bg-blue-600 text-blue-600 font-semibold hover:text-white py-3 px-8 border-2 border-blue-500 hover:border-blue-600 rounded-lg transition duration-200">
        View All Jobs
        <ChevronRight size={20} class="ml-2" />
      </a>
    </div>
  </div>
</section>

<!-- Testimonials Section -->
<section class="py-16 lg:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Success Stories</h2>
      <p class="text-lg text-gray-600">Hear from professionals who've transformed their careers with HirePulse.in</p>
    </div>
    <div class="grid md:grid-cols-3 gap-8">
      {#each testimonials as testimonial (testimonial.id)}
        <div class="bg-gray-50 p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
          <div class="flex mb-4">
            {#each {length: 5} as _, i}
              <Star class="text-yellow-400 fill-current" size={18} />
            {/each}
          </div>
          <blockquote class="text-gray-700 italic mb-6 leading-relaxed">"{testimonial.quote}"</blockquote>
          <div class="flex items-center">
            <img src={testimonial.avatar} alt="{testimonial.name}" class="w-12 h-12 rounded-full mr-4 object-cover border-2 border-gray-200">
            <div>
              <h4 class="font-bold text-gray-800">{testimonial.name}</h4>
              <p class="text-sm text-gray-600">{testimonial.role}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- CTA Section -->
<section class="py-16 lg:py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
  <div class="container mx-auto px-4 lg:px-6 text-center">
    <h2 class="text-3xl lg:text-4xl font-bold mb-6">Ready to Transform Your Career?</h2>
    <p class="text-lg lg:text-xl mb-8 max-w-2xl mx-auto text-blue-100">
      Join thousands of professionals who've found their dream jobs through our AI-powered platform.
    </p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href="/register" class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition duration-200 inline-flex items-center justify-center">
        Get Started Free
        <ChevronRight size={20} class="ml-2" />
      </a>
      <a href="/jobs" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition duration-200">
        Browse Jobs
      </a>
    </div>
  </div>
</section>

<style>
  /* Enhanced animations */
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
      transform: translateY(-30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(30px);
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

  /* Smooth scrolling for anchor links */
  :global(html) {
    scroll-behavior: smooth;
  }
</style>
