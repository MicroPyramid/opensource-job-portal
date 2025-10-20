<script lang="ts">
  import { Check, X, Zap, Users, TrendingUp, Shield, Clock, Heart, Award, Target, Sparkles, ArrowRight, BadgeCheck } from '@lucide/svelte';

  // Features included in the free plan
  const includedFeatures = [
    { name: 'Unlimited Job Postings', icon: Zap },
    { name: 'Access to Entire Candidate Database', icon: Users },
    { name: 'Advanced Search & Filters', icon: Target },
    { name: 'Application Tracking System', icon: TrendingUp },
    { name: 'Email Notifications', icon: Clock },
    { name: 'Company Profile Page', icon: BadgeCheck },
    { name: 'Resume Database Access', icon: Users },
    { name: 'Candidate Messaging', icon: Heart },
    { name: 'Priority Customer Support', icon: Shield },
    { name: 'Analytics & Insights', icon: Award }
  ];

  // What competitors charge for
  const competitorFeatures = [
    { name: 'Job Posting Fees', free: true, competitors: false },
    { name: 'Resume Database Access', free: true, competitors: false },
    { name: 'Featured Listings', free: true, competitors: false },
    { name: 'Unlimited Applications', free: true, competitors: false },
    { name: 'Advanced Analytics', free: true, competitors: false }
  ];

  // FAQs
  const faqs = [
    {
      question: 'Is PeelJobs really 100% free?',
      answer: 'Yes! We never charge for job postings, candidate access, or any recruiting features. Our mission is to connect employers with the best talent in India at zero cost.'
    },
    {
      question: 'Are there any hidden fees or premium plans?',
      answer: 'No hidden fees whatsoever. We don\'t have premium plans because we believe all employers deserve equal access to top talent, regardless of their budget.'
    },
    {
      question: 'How do you make money if everything is free?',
      answer: 'We\'re supported by strategic partnerships and display advertising. We never compromise the quality of our platform or charge employers for core recruiting features.'
    },
    {
      question: 'Will you start charging in the future?',
      answer: 'No. We\'re committed to keeping PeelJobs free forever. Our goal is to make quality hiring accessible to every employer in India, from startups to enterprises.'
    },
    {
      question: 'How many jobs can I post?',
      answer: 'There\'s no limit! Post as many jobs as you need, whenever you need. We want to help you build your entire team without worrying about costs.'
    },
    {
      question: 'Can I access the resume database for free?',
      answer: 'Absolutely! You get full access to our database of over 1 million job seekers, including advanced search filters, without paying a single rupee.'
    },
    {
      question: 'How quickly can I start posting jobs?',
      answer: 'You can create an account and post your first job in under 5 minutes. No credit card required, no approval wait times.'
    },
    {
      question: 'What kind of support do I get?',
      answer: 'All employers get access to our dedicated support team via email and chat. We\'re here to help you succeed in finding the right talent.'
    }
  ];

  let openFaqIndex: number | null = null;

  function toggleFaq(index: number) {
    openFaqIndex = openFaqIndex === index ? null : index;
  }
</script>

<svelte:head>
  <title>Pricing - 100% Free Forever | PeelJobs - India's Free Job Posting Platform</title>
  <meta name="description" content="Post unlimited jobs for FREE. No hidden costs, no premium plans. Access 1M+ candidates, advanced hiring tools, and unlimited job postings at zero cost. Join 50K+ employers hiring on PeelJobs." />
  <meta property="og:title" content="100% Free Job Posting Platform - PeelJobs Pricing" />
  <meta property="og:description" content="Never pay for job postings again. Unlimited free access to India's largest talent pool. Post jobs, search resumes, and hire the best candidates - all for free." />
  <meta property="og:type" content="website" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="100% Free Job Posting Platform - PeelJobs Pricing" />
  <meta name="twitter:description" content="Unlimited job postings, resume database access, and hiring tools - all FREE forever." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white py-16 md:py-20 lg:py-24 relative overflow-hidden">
  <div class="container mx-auto px-4 lg:px-6 relative z-10">
    <div class="max-w-4xl mx-auto text-center">
      <!-- Free Badge -->
      <div class="inline-flex items-center gap-2 bg-green-600 bg-opacity-90 px-6 py-3 rounded-full text-base md:text-lg font-semibold mb-6 shadow-lg">
        <Sparkles size={20} class="text-green-200" />
        <span>100% Free Forever</span>
      </div>

      <!-- Heading -->
      <h1 class="text-3xl md:text-5xl lg:text-6xl font-bold leading-tight mb-6">
        Hire the Best Talent in India
        <span class="block text-green-400 mt-2">Without Spending a Rupee</span>
      </h1>

      <p class="text-lg md:text-xl text-blue-100 leading-relaxed mb-8 max-w-3xl mx-auto">
        Join 50,000+ employers who trust PeelJobs for their hiring needs. Post unlimited jobs, access 1 million+ candidates, and build your dream team - all for <strong class="text-white">FREE</strong>.
      </p>

      <!-- CTA Buttons -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-12">
        <a href="/employer/" class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition duration-200 inline-flex items-center justify-center shadow-xl text-lg">
          Start Hiring Free
          <ArrowRight size={20} class="ml-2" />
        </a>
        <a href="#features" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition duration-200 text-lg">
          See What's Included
        </a>
      </div>

      <!-- Trust Indicators -->
      <div class="flex flex-wrap justify-center gap-6 text-sm text-blue-200">
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>No Credit Card Required</span>
        </div>
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>No Hidden Fees</span>
        </div>
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>Setup in 5 Minutes</span>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Pricing Card Section -->
<section id="features" class="py-16 md:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-4">One Simple Plan. Everything Included.</h2>
      <p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
        No tiers, no upsells, no complicated pricing. Just one powerful platform with everything you need to hire great people.
      </p>
    </div>

    <!-- Main Pricing Card -->
    <div class="max-w-2xl mx-auto">
      <div class="bg-white rounded-2xl shadow-2xl overflow-hidden border-4 border-blue-600 relative">
        <!-- Popular Badge -->
        <div class="absolute top-0 right-0 bg-blue-600 text-white px-6 py-2 text-sm font-semibold rounded-bl-lg">
          Most Popular
        </div>

        <div class="p-8 md:p-10">
          <!-- Plan Header -->
          <div class="text-center mb-8">
            <h3 class="text-2xl md:text-3xl font-bold text-gray-800 mb-3">Free Forever Plan</h3>
            <div class="mb-4">
              <span class="text-6xl md:text-7xl font-bold text-blue-600">₹0</span>
              <span class="text-2xl text-gray-600 ml-2">forever</span>
            </div>
            <p class="text-gray-600 text-lg">Everything you need to build your team. No catch.</p>
          </div>

          <!-- Features List -->
          <div class="space-y-4 mb-8">
            {#each includedFeatures as feature}
              <div class="flex items-start gap-3">
                <div class="flex-shrink-0 w-6 h-6 bg-green-100 rounded-full flex items-center justify-center mt-0.5">
                  <Check size={14} class="text-green-600 font-bold" />
                </div>
                <div class="flex items-center gap-3 flex-1">
                  <svelte:component this={feature.icon} size={18} class="text-blue-600 flex-shrink-0" />
                  <span class="text-gray-700 font-medium">{feature.name}</span>
                </div>
              </div>
            {/each}
          </div>

          <!-- CTA Button -->
          <a href="/employer/" class="w-full bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition duration-200 inline-flex items-center justify-center text-lg shadow-lg">
            Get Started Free
            <ArrowRight size={20} class="ml-2" />
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Comparison Section -->
<section class="py-16 md:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-4">How We Compare</h2>
      <p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
        See what other platforms charge thousands for - and what we give you for free.
      </p>
    </div>

    <div class="max-w-4xl mx-auto">
      <div class="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
        <!-- Header Row -->
        <div class="grid grid-cols-3 bg-gray-50 border-b border-gray-200">
          <div class="p-4 md:p-6"></div>
          <div class="p-4 md:p-6 text-center border-l border-gray-200">
            <div class="font-bold text-blue-600 text-lg md:text-xl">PeelJobs</div>
            <div class="text-xs md:text-sm text-gray-600 mt-1">Free Forever</div>
          </div>
          <div class="p-4 md:p-6 text-center border-l border-gray-200">
            <div class="font-bold text-gray-800 text-lg md:text-xl">Competitors</div>
            <div class="text-xs md:text-sm text-gray-600 mt-1">₹10K-50K/month</div>
          </div>
        </div>

        <!-- Feature Rows -->
        {#each competitorFeatures as feature}
          <div class="grid grid-cols-3 border-b border-gray-100 hover:bg-gray-50 transition-colors">
            <div class="p-4 md:p-6 font-medium text-gray-700 text-sm md:text-base">{feature.name}</div>
            <div class="p-4 md:p-6 text-center border-l border-gray-100">
              {#if feature.free}
                <div class="inline-flex items-center justify-center w-8 h-8 bg-green-100 rounded-full">
                  <Check size={18} class="text-green-600 font-bold" />
                </div>
              {:else}
                <div class="inline-flex items-center justify-center w-8 h-8 bg-red-100 rounded-full">
                  <X size={18} class="text-red-600" />
                </div>
              {/if}
            </div>
            <div class="p-4 md:p-6 text-center border-l border-gray-100">
              {#if feature.competitors}
                <div class="inline-flex items-center justify-center w-8 h-8 bg-green-100 rounded-full">
                  <Check size={18} class="text-green-600 font-bold" />
                </div>
              {:else}
                <div class="inline-flex items-center justify-center w-8 h-8 bg-red-100 rounded-full">
                  <X size={18} class="text-red-600" />
                </div>
                <div class="text-xs text-gray-500 mt-1 hidden md:block">Extra Cost</div>
              {/if}
            </div>
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<!-- Why Free Section -->
<section class="py-16 md:py-20 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-4">Why Is PeelJobs Free?</h2>
      <p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
        Our mission is simple: connect employers with the best talent in India without financial barriers.
      </p>
    </div>

    <div class="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-blue-100 rounded-full">
            <Heart class="text-blue-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Our Mission</h3>
        <p class="text-gray-600 text-center leading-relaxed">
          We believe every company, from startups to enterprises, deserves access to top talent without budget constraints limiting their growth.
        </p>
      </div>

      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-green-100 rounded-full">
            <Users class="text-green-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">More Opportunities</h3>
        <p class="text-gray-600 text-center leading-relaxed">
          By eliminating posting fees, we create more job opportunities for seekers and help employers find candidates they otherwise couldn't afford to reach.
        </p>
      </div>

      <div class="bg-white p-8 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300 border border-gray-100">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-purple-100 rounded-full">
            <TrendingUp class="text-purple-600" size={32} />
          </div>
        </div>
        <h3 class="text-xl font-bold mb-4 text-gray-800 text-center">Better Outcomes</h3>
        <p class="text-gray-600 text-center leading-relaxed">
          When more employers can afford to post jobs and more candidates apply, everyone wins. We measure success by successful hires, not revenue.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- FAQ Section -->
<section class="py-16 md:py-20 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="text-center mb-12">
      <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-800 mb-4">Frequently Asked Questions</h2>
      <p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
        Everything you need to know about our free platform
      </p>
    </div>

    <div class="max-w-3xl mx-auto space-y-4">
      {#each faqs as faq, index}
        <div class="bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
          <button
            onclick={() => toggleFaq(index)}
            class="w-full px-6 py-5 text-left flex justify-between items-center"
          >
            <span class="font-semibold text-gray-800 text-base md:text-lg pr-4">{faq.question}</span>
            <div class="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
              <div class="text-blue-600 font-bold text-xl transform transition-transform {openFaqIndex === index ? 'rotate-45' : ''}">
                +
              </div>
            </div>
          </button>
          {#if openFaqIndex === index}
            <div class="px-6 pb-5 text-gray-600 leading-relaxed">
              {faq.answer}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Final CTA Section -->
<section class="py-16 md:py-20 bg-gradient-to-r from-blue-600 to-indigo-700 text-white">
  <div class="container mx-auto px-4 lg:px-6 text-center">
    <div class="max-w-3xl mx-auto">
      <h2 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-6">Ready to Start Hiring?</h2>
      <p class="text-lg md:text-xl mb-8 text-blue-100 leading-relaxed">
        Join thousands of employers who are building amazing teams without spending a rupee. Create your free account in minutes and post your first job today.
      </p>

      <div class="flex flex-col sm:flex-row gap-4 justify-center mb-8">
        <a href="/employer/" class="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition duration-200 inline-flex items-center justify-center text-lg shadow-xl">
          Create Free Account
          <ArrowRight size={20} class="ml-2" />
        </a>
        <a href="/contact/" class="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition duration-200 text-lg">
          Talk to Our Team
        </a>
      </div>

      <div class="flex flex-wrap justify-center gap-6 text-sm text-blue-200">
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>Free Forever</span>
        </div>
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>No Credit Card</span>
        </div>
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>5 Minute Setup</span>
        </div>
        <div class="flex items-center gap-2">
          <Check size={18} class="text-green-400" />
          <span>Unlimited Postings</span>
        </div>
      </div>
    </div>
  </div>
</section>
