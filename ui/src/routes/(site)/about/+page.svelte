<script>
  import { Target, Users, Zap, Heart, Award, Globe, TrendingUp, Shield, CheckCircle } from '@lucide/svelte';

  const stats = [
    { label: 'Active Jobs', value: '50,000+', icon: TrendingUp },
    { label: 'Companies', value: '5,000+', icon: Globe },
    { label: 'Job Seekers', value: '100,000+', icon: Users },
    { label: 'Success Stories', value: '25,000+', icon: Award }
  ];

  const values = [
    {
      icon: Target,
      title: 'Mission-Driven',
      description: 'We\'re committed to connecting talented individuals with opportunities that align with their career goals and aspirations.'
    },
    {
      icon: Users,
      title: 'People-First',
      description: 'Both job seekers and employers are at the heart of everything we do. We prioritize user experience and satisfaction above all.'
    },
    {
      icon: Shield,
      title: 'Trust & Transparency',
      description: 'We maintain the highest standards of integrity, ensuring a safe and transparent platform for all users.'
    },
    {
      icon: Zap,
      title: 'Innovation',
      description: 'We leverage cutting-edge technology to streamline the hiring process and deliver exceptional results.'
    }
  ];

  const howItWorks = {
    jobSeekers: [
      {
        step: 1,
        title: 'Create Your Profile',
        description: 'Build a comprehensive profile showcasing your skills, experience, and career goals.'
      },
      {
        step: 2,
        title: 'Discover Opportunities',
        description: 'Browse thousands of jobs or let our smart algorithms match you with the perfect positions.'
      },
      {
        step: 3,
        title: 'Apply with Confidence',
        description: 'Submit applications with your tailored resume and track your progress in real-time.'
      },
      {
        step: 4,
        title: 'Land Your Dream Job',
        description: 'Connect with recruiters, ace your interviews, and start your next career chapter.'
      }
    ],
    employers: [
      {
        step: 1,
        title: 'Post Your Job',
        description: 'Create detailed job listings that attract the right candidates for your organization.'
      },
      {
        step: 2,
        title: 'Find Top Talent',
        description: 'Access a pool of qualified candidates and use our tools to identify the best matches.'
      },
      {
        step: 3,
        title: 'Review Applications',
        description: 'Efficiently review applications, communicate with candidates, and schedule interviews.'
      },
      {
        step: 4,
        title: 'Hire the Best',
        description: 'Make informed hiring decisions and welcome exceptional talent to your team.'
      }
    ]
  };

  let activeTab = 'jobSeekers'; // jobSeekers or employers
</script>

<svelte:head>
  <title>About Us - HirePulse.in</title>
  <meta name="description" content="Learn about HirePulse's mission to connect talented professionals with their dream careers" />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-20 md:py-32">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto text-center">
      <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 animate-fade-in-down">
        Empowering Careers,<br />Transforming Lives
      </h1>
      <p class="text-xl md:text-2xl text-blue-100 mb-8 animate-fade-in-up">
        HirePulse is India's leading job portal, connecting talented professionals with opportunities that matter.
      </p>
      <div class="flex flex-wrap justify-center gap-4 animate-fade-in">
        <a
          href="/jobs"
          class="bg-white text-blue-700 hover:bg-blue-50 font-semibold px-8 py-4 rounded-lg transition duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Explore Jobs
        </a>
        <a
          href="/contact"
          class="border-2 border-white text-white hover:bg-white hover:text-blue-700 font-semibold px-8 py-4 rounded-lg transition duration-200"
        >
          Get in Touch
        </a>
      </div>
    </div>
  </div>
</section>

<!-- Stats Section -->
<section class="py-16 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-8">
      {#each stats as stat}
        <div class="text-center">
          <div class="flex justify-center mb-4">
            <div class="p-4 bg-blue-100 rounded-full">
              <stat.icon class="text-blue-600" size={32} />
            </div>
          </div>
          <div class="text-3xl md:text-4xl font-bold text-gray-800 mb-2">{stat.value}</div>
          <div class="text-gray-600 font-medium">{stat.label}</div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Mission & Vision -->
<section class="py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-12">
        <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Our Story</h2>
        <p class="text-lg text-gray-600">Building bridges between talent and opportunity</p>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-8 md:p-12 border border-gray-100 mb-8">
        <div class="flex items-start gap-4 mb-6">
          <div class="p-3 bg-blue-100 rounded-lg flex-shrink-0">
            <Target class="text-blue-600" size={28} />
          </div>
          <div>
            <h3 class="text-2xl font-bold text-gray-800 mb-4">Our Mission</h3>
            <p class="text-gray-700 leading-relaxed mb-4">
              At HirePulse, we believe that everyone deserves access to meaningful career opportunities. Our mission is to revolutionize the job search experience by creating a platform that's intuitive, transparent, and effective for both job seekers and employers.
            </p>
            <p class="text-gray-700 leading-relaxed">
              We're committed to leveraging technology to break down barriers in the hiring process, making it easier for talented professionals to find roles where they can thrive and for companies to discover exceptional talent that drives their success.
            </p>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-8 md:p-12 border border-gray-100">
        <div class="flex items-start gap-4">
          <div class="p-3 bg-purple-100 rounded-lg flex-shrink-0">
            <Heart class="text-purple-600" size={28} />
          </div>
          <div>
            <h3 class="text-2xl font-bold text-gray-800 mb-4">Our Vision</h3>
            <p class="text-gray-700 leading-relaxed mb-4">
              We envision a world where finding the perfect job or hiring the ideal candidate is no longer a challenge but an exciting, streamlined experience. HirePulse aims to be the go-to platform for career advancement across India.
            </p>
            <p class="text-gray-700 leading-relaxed">
              Through continuous innovation, user-centric design, and unwavering commitment to quality, we're building the future of work—one connection at a time.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Core Values -->
<section class="py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Our Core Values</h2>
      <p class="text-lg text-gray-600">The principles that guide everything we do</p>
    </div>

    <div class="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
      {#each values as value}
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-100 hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-start gap-4">
            <div class="p-3 bg-blue-600 rounded-lg flex-shrink-0">
              <value.icon class="text-white" size={24} />
            </div>
            <div>
              <h3 class="text-xl font-bold text-gray-800 mb-3">{value.title}</h3>
              <p class="text-gray-700 leading-relaxed">{value.description}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- How It Works -->
<section class="py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">How It Works</h2>
      <p class="text-lg text-gray-600">Simple steps to achieve your goals</p>
    </div>

    <!-- Tabs -->
    <div class="flex justify-center gap-4 mb-12">
      <button
        onclick={() => activeTab = 'jobSeekers'}
        class="px-8 py-3 rounded-lg font-semibold transition-all duration-200"
        class:bg-blue-600={activeTab === 'jobSeekers'}
        class:text-white={activeTab === 'jobSeekers'}
        class:shadow-lg={activeTab === 'jobSeekers'}
        class:bg-white={activeTab !== 'jobSeekers'}
        class:text-gray-700={activeTab !== 'jobSeekers'}
        class:border={activeTab !== 'jobSeekers'}
        class:border-gray-300={activeTab !== 'jobSeekers'}
      >
        For Job Seekers
      </button>
      <button
        onclick={() => activeTab = 'employers'}
        class="px-8 py-3 rounded-lg font-semibold transition-all duration-200"
        class:bg-blue-600={activeTab === 'employers'}
        class:text-white={activeTab === 'employers'}
        class:shadow-lg={activeTab === 'employers'}
        class:bg-white={activeTab !== 'employers'}
        class:text-gray-700={activeTab !== 'employers'}
        class:border={activeTab !== 'employers'}
        class:border-gray-300={activeTab !== 'employers'}
      >
        For Employers
      </button>
    </div>

    <!-- Job Seekers Flow -->
    {#if activeTab === 'jobSeekers'}
      <div class="max-w-4xl mx-auto">
        <div class="grid md:grid-cols-2 gap-8">
          {#each howItWorks.jobSeekers as step}
            <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-700 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {step.step}
                  </div>
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-800 mb-3">{step.title}</h3>
                  <p class="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Employers Flow -->
    {#if activeTab === 'employers'}
      <div class="max-w-4xl mx-auto">
        <div class="grid md:grid-cols-2 gap-8">
          {#each howItWorks.employers as step}
            <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100 hover:shadow-xl transition-shadow duration-300">
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0">
                  <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-700 rounded-full flex items-center justify-center text-white font-bold text-xl">
                    {step.step}
                  </div>
                </div>
                <div class="flex-1">
                  <h3 class="text-xl font-bold text-gray-800 mb-3">{step.title}</h3>
                  <p class="text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}
  </div>
</section>

<!-- Why Choose HirePulse -->
<section class="py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl lg:text-4xl font-bold text-gray-800 mb-4">Why Choose HirePulse?</h2>
      <p class="text-lg text-gray-600">We're different, and here's why</p>
    </div>

    <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
      <div class="text-center">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-green-100 rounded-full">
            <CheckCircle class="text-green-600" size={40} />
          </div>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-3">Verified Companies</h3>
        <p class="text-gray-600 leading-relaxed">
          Every company on our platform is verified to ensure authenticity and protect job seekers from fraud.
        </p>
      </div>

      <div class="text-center">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-blue-100 rounded-full">
            <Zap class="text-blue-600" size={40} />
          </div>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-3">Smart Matching</h3>
        <p class="text-gray-600 leading-relaxed">
          Our AI-powered algorithms match you with jobs that truly fit your skills, experience, and preferences.
        </p>
      </div>

      <div class="text-center">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-purple-100 rounded-full">
            <Shield class="text-purple-600" size={40} />
          </div>
        </div>
        <h3 class="text-xl font-bold text-gray-800 mb-3">Privacy Protected</h3>
        <p class="text-gray-600 leading-relaxed">
          Your data is secure with us. We never share your information without your explicit consent.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- CTA Section -->
<section class="py-20 bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-3xl mx-auto text-center">
      <h2 class="text-3xl lg:text-4xl font-bold mb-6">Ready to Get Started?</h2>
      <p class="text-xl text-blue-100 mb-8">
        Join thousands of professionals who have found their dream jobs through HirePulse
      </p>
      <div class="flex flex-wrap justify-center gap-4">
        <a
          href="/register"
          class="bg-white text-blue-700 hover:bg-blue-50 font-semibold px-8 py-4 rounded-lg transition duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Create Free Account
        </a>
        <a
          href="/jobs"
          class="border-2 border-white text-white hover:bg-white hover:text-blue-700 font-semibold px-8 py-4 rounded-lg transition duration-200"
        >
          Browse Jobs
        </a>
      </div>
    </div>
  </div>
</section>

<style>
  @keyframes fade-in-down {
    from {
      opacity: 0;
      transform: translateY(-20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fade-in-up {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fade-in {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  .animate-fade-in-down {
    animation: fade-in-down 0.8s ease-out forwards;
  }

  .animate-fade-in-up {
    animation: fade-in-up 0.8s ease-out 0.2s forwards;
    opacity: 0;
  }

  .animate-fade-in {
    animation: fade-in 1s ease-out 0.4s forwards;
    opacity: 0;
  }
</style>
