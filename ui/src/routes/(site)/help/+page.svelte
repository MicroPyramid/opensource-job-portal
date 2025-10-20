<script lang="ts">
  import { HelpCircle, Search, ChevronDown, ChevronUp, Book, UserCircle, Briefcase, Settings, MessageCircle, Shield } from '@lucide/svelte';

  type IconComponent = typeof HelpCircle;

  interface Category {
    id: 'all' | 'getting_started' | 'account' | 'job_search' | 'applications' | 'privacy' | 'technical';
    name: string;
    icon: IconComponent;
  }

  type CategoryId = Category['id'];

  interface FaqItem {
    id: number;
    category: Exclude<CategoryId, 'all'>;
    question: string;
    answer: string;
  }

  interface Article {
    title: string;
    description: string;
    category: string;
    readTime: string;
  }

  let searchQuery = $state('');
  let selectedCategory = $state<CategoryId>('all');
  let expandedFaqId = $state<number | null>(null);

  const categories: Category[] = [
    { id: 'all', name: 'All Topics', icon: HelpCircle },
    { id: 'getting_started', name: 'Getting Started', icon: Book },
    { id: 'account', name: 'Account & Profile', icon: UserCircle },
    { id: 'job_search', name: 'Job Search', icon: Search },
    { id: 'applications', name: 'Applications', icon: Briefcase },
    { id: 'privacy', name: 'Privacy & Security', icon: Shield },
    { id: 'technical', name: 'Technical Issues', icon: Settings }
  ];

  const faqs: FaqItem[] = [
    // Getting Started
    {
      id: 1,
      category: 'getting_started',
      question: 'How do I create an account on HirePulse?',
      answer: 'To create an account, click on "Register" in the top right corner of the homepage. You can sign up using your email address or use Google/Facebook OAuth for quick registration. Fill in your basic details, verify your email, and you\'re ready to start your job search!'
    },
    {
      id: 2,
      category: 'getting_started',
      question: 'Is HirePulse free to use for job seekers?',
      answer: 'Yes! HirePulse is completely free for job seekers. You can create an account, search for jobs, apply to unlimited positions, and use all our features without any charges.'
    },
    {
      id: 3,
      category: 'getting_started',
      question: 'What are the benefits of creating a profile?',
      answer: 'Creating a profile allows you to save jobs, apply quickly with your saved resume, track application status, receive personalized job recommendations, and get notified when new jobs matching your preferences are posted.'
    },

    // Account & Profile
    {
      id: 4,
      category: 'account',
      question: 'How do I update my profile information?',
      answer: 'Navigate to your profile by clicking on your name in the top right corner, then select "Profile". You can edit your personal information, add work experience, education, skills, and upload your resume. Make sure to save your changes!'
    },
    {
      id: 5,
      category: 'account',
      question: 'How do I change my password?',
      answer: 'Go to Settings > Password from your account menu. Enter your current password, then your new password twice to confirm. Your password must be at least 8 characters and include uppercase, lowercase, and numbers.'
    },
    {
      id: 6,
      category: 'account',
      question: 'Can I delete my account?',
      answer: 'Yes, you can delete your account by going to Settings > Privacy and scrolling to the bottom. Please note that account deletion is permanent and all your data, applications, and saved jobs will be permanently removed.'
    },
    {
      id: 7,
      category: 'account',
      question: 'How do I upload or update my resume?',
      answer: 'Visit the Profile page and scroll to the Resume section. Click "Upload Resume" to add a new PDF resume (max 5MB). You can upload multiple resumes and set one as default for quick applications.'
    },

    // Job Search
    {
      id: 8,
      category: 'job_search',
      question: 'How do I search for jobs?',
      answer: 'Use the search bar on the homepage or visit the Jobs page. You can search by keywords (job title, skills, company), location, and apply filters for job type, salary range, experience level, and more. Advanced filters help you find exactly what you\'re looking for.'
    },
    {
      id: 9,
      category: 'job_search',
      question: 'How do I save a job to apply later?',
      answer: 'Click the bookmark/star icon on any job listing to save it for later. Access all your saved jobs from your dashboard or the "Saved Jobs" page in your account menu.'
    },
    {
      id: 10,
      category: 'job_search',
      question: 'What are job alerts and how do I set them up?',
      answer: 'Job alerts notify you when new jobs matching your criteria are posted. Go to Settings > Job Alerts to create custom alerts based on keywords, location, job type, and salary. Choose how often you want to receive notifications (instant, daily, or weekly).'
    },
    {
      id: 11,
      category: 'job_search',
      question: 'How does the job matching algorithm work?',
      answer: 'Our AI-powered matching system analyzes your profile, skills, experience, and preferences to recommend jobs that best fit your qualifications. The more complete your profile, the better the matches!'
    },

    // Applications
    {
      id: 12,
      category: 'applications',
      question: 'How do I apply for a job?',
      answer: 'Click on any job listing to view details, then click "Apply Now". You\'ll need to select a resume and optionally add a cover letter. Review your application and submit. You can track all your applications from your dashboard.'
    },
    {
      id: 13,
      category: 'applications',
      question: 'Can I withdraw an application?',
      answer: 'Currently, once an application is submitted, it cannot be withdrawn through the platform. However, you can contact the recruiter directly through our messaging system to withdraw your application.'
    },
    {
      id: 14,
      category: 'applications',
      question: 'How can I track my application status?',
      answer: 'Visit the "Applications" page from your dashboard to see all your submitted applications. Each application shows its current status (Under Review, Shortlisted, Interview Scheduled, etc.) and timeline.'
    },
    {
      id: 15,
      category: 'applications',
      question: 'Why was my application rejected?',
      answer: 'Application decisions are made by employers based on their specific requirements. While we don\'t have access to their decision criteria, you can message the recruiter for feedback or continue applying to other positions that match your profile.'
    },

    // Privacy & Security
    {
      id: 16,
      category: 'privacy',
      question: 'How is my personal data protected?',
      answer: 'We use industry-standard encryption and security measures to protect your data. Your information is never shared with third parties without your explicit consent. Read our Privacy Policy for complete details.'
    },
    {
      id: 17,
      category: 'privacy',
      question: 'Can I control who sees my profile?',
      answer: 'Yes! Go to Settings > Privacy to control your profile visibility. You can choose to make it public, visible only to verified recruiters, or completely private. You can also control individual elements like contact information visibility.'
    },
    {
      id: 18,
      category: 'privacy',
      question: 'How do I report a suspicious job posting?',
      answer: 'If you encounter a suspicious job posting, click the "Report" button on the job detail page. Provide details about why you think it\'s suspicious. Our team reviews all reports within 24 hours.'
    },

    // Technical Issues
    {
      id: 19,
      category: 'technical',
      question: 'The website is not loading properly. What should I do?',
      answer: 'Try clearing your browser cache and cookies, or use a different browser. Make sure you\'re using an updated browser version. If the issue persists, contact our support team with details about your browser and operating system.'
    },
    {
      id: 20,
      category: 'technical',
      question: 'I\'m not receiving email notifications. How do I fix this?',
      answer: 'Check your spam/junk folder for emails from HirePulse. Add support@hirepulse.in to your contacts. Also verify that email notifications are enabled in Settings > Notifications. If issues persist, contact support.'
    },
    {
      id: 21,
      category: 'technical',
      question: 'My resume upload is failing. What formats are supported?',
      answer: 'We currently support PDF format only. Your resume must be under 5MB in size. Make sure your PDF is not password-protected. If you continue to experience issues, try converting your resume to PDF using a different tool.'
    }
  ];

  const popularArticles: Article[] = [
    {
      title: 'How to Create a Winning Resume',
      description: 'Tips and best practices for crafting a resume that stands out',
      category: 'Getting Started',
      readTime: '5 min read'
    },
    {
      title: 'Interview Preparation Guide',
      description: 'Complete guide to preparing for your job interviews',
      category: 'Job Search',
      readTime: '8 min read'
    },
    {
      title: 'Understanding Application Status',
      description: 'What each application status means and what to expect',
      category: 'Applications',
      readTime: '3 min read'
    }
  ];

  // Filter FAQs
  const filteredFaqs = $derived((): FaqItem[] => {
    const query = searchQuery.toLowerCase().trim();
    return faqs.filter(faq => {
      const matchesCategory = selectedCategory === 'all' || faq.category === selectedCategory;
      const matchesSearch =
        query === '' ||
        faq.question.toLowerCase().includes(query) ||
        faq.answer.toLowerCase().includes(query);

      return matchesCategory && matchesSearch;
    });
  });

  function toggleFaq(id: number): void {
    expandedFaqId = expandedFaqId === id ? null : id;
  }

  function selectCategory(categoryId: CategoryId): void {
    selectedCategory = categoryId;
    expandedFaqId = null; // Collapse all when changing category
  }
</script>

<svelte:head>
  <title>Help Center - HirePulse.in</title>
  <meta name="description" content="Find answers to common questions about using HirePulse" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-20">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-3xl mx-auto text-center">
      <div class="flex justify-center mb-6">
        <div class="p-4 bg-white/10 rounded-full">
          <HelpCircle size={48} />
        </div>
      </div>
      <h1 class="text-4xl md:text-5xl font-bold mb-6">How Can We Help?</h1>
      <p class="text-xl text-blue-100 mb-8">
        Search our knowledge base for quick answers to your questions
      </p>

      <!-- Search Bar -->
      <div class="relative max-w-2xl mx-auto">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search class="text-blue-300" size={24} />
        </div>
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search for help articles, FAQs..."
          class="w-full pl-14 pr-4 py-5 bg-white text-gray-800 rounded-lg focus:outline-none focus:ring-4 focus:ring-white/50 text-lg"
        />
      </div>
    </div>
  </div>
</section>

<!-- Popular Articles -->
{#if searchQuery === ''}
  <section class="py-12 bg-white">
    <div class="container mx-auto px-4 lg:px-6">
      <div class="max-w-6xl mx-auto">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Popular Articles</h2>

        <div class="grid md:grid-cols-3 gap-6">
          {#each popularArticles as article}
            <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100 hover:shadow-lg transition-shadow duration-300 cursor-pointer">
              <div class="mb-3">
                <span class="bg-blue-600 text-white text-xs px-3 py-1 rounded-full font-medium">{article.category}</span>
              </div>
              <h3 class="text-lg font-bold text-gray-800 mb-2">{article.title}</h3>
              <p class="text-sm text-gray-600 mb-3">{article.description}</p>
              <p class="text-xs text-gray-500">{article.readTime}</p>
            </div>
          {/each}
        </div>
      </div>
    </div>
  </section>
{/if}

<!-- Main Content -->
<section class="py-16 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-6xl mx-auto">

      <!-- Category Filters -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Browse by Category</h2>

        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4">
          {#each categories as category}
            <button
              onclick={() => selectCategory(category.id)}
              class="flex flex-col items-center gap-2 p-4 rounded-xl transition-all duration-200"
              class:bg-blue-600={selectedCategory === category.id}
              class:text-white={selectedCategory === category.id}
              class:shadow-lg={selectedCategory === category.id}
              class:bg-white={selectedCategory !== category.id}
              class:text-gray-700={selectedCategory !== category.id}
              class:border={selectedCategory !== category.id}
              class:border-gray-200={selectedCategory !== category.id}
              class:hover:border-blue-300={selectedCategory !== category.id}
            >
              <category.icon size={24} />
              <span class="text-xs font-medium text-center">{category.name}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Results Count -->
      {#if searchQuery !== ''}
        <div class="mb-6">
          <p class="text-gray-600">
            Found <span class="font-semibold text-gray-800">{filteredFaqs().length}</span>
            result{filteredFaqs().length !== 1 ? 's' : ''} for "{searchQuery}"
          </p>
        </div>
      {/if}

      <!-- FAQs -->
      {#if filteredFaqs().length > 0}
        <div class="bg-white rounded-xl shadow-lg border border-gray-100">
          {#each filteredFaqs() as faq, index (faq.id)}
            <div class="border-b border-gray-200 last:border-b-0">
              <button
                onclick={() => toggleFaq(faq.id)}
                class="w-full px-8 py-6 text-left hover:bg-gray-50 transition-colors duration-200 flex items-center justify-between gap-4"
              >
                <div class="flex-1">
                  <h3 class="text-lg font-semibold text-gray-800 pr-4">{faq.question}</h3>
                </div>
                <div class="flex-shrink-0">
                  {#if expandedFaqId === faq.id}
                    <ChevronUp class="text-blue-600" size={24} />
                  {:else}
                    <ChevronDown class="text-gray-400" size={24} />
                  {/if}
                </div>
              </button>

              {#if expandedFaqId === faq.id}
                <div class="px-8 pb-6 text-gray-700 leading-relaxed animate-slide-down">
                  {faq.answer}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {:else}
        <div class="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-100">
          <div class="flex justify-center mb-4">
            <div class="p-4 bg-gray-100 rounded-full">
              <Search class="text-gray-400" size={48} />
            </div>
          </div>
          <h2 class="text-2xl font-bold text-gray-800 mb-2">No Results Found</h2>
          <p class="text-gray-600 mb-6">
            We couldn't find any FAQs matching your search. Try different keywords or browse by category.
          </p>
          <button
            onclick={() => { searchQuery = ''; selectedCategory = 'all'; }}
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition-colors duration-200"
          >
            Clear Search
          </button>
        </div>
      {/if}

    </div>
  </div>
</section>

<!-- Still Need Help -->
<section class="py-16 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto">
      <div class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white rounded-2xl p-12 text-center">
        <div class="flex justify-center mb-6">
          <div class="p-4 bg-white/10 rounded-full">
            <MessageCircle size={40} />
          </div>
        </div>
        <h2 class="text-3xl font-bold mb-4">Still Need Help?</h2>
        <p class="text-xl text-blue-100 mb-8">
          Can't find what you're looking for? Our support team is here to help.
        </p>
        <div class="flex flex-wrap justify-center gap-4">
          <a
            href="/contact/"
            class="bg-white text-blue-700 hover:bg-blue-50 font-semibold px-8 py-4 rounded-lg transition duration-200 shadow-lg hover:shadow-xl"
          >
            Contact Support
          </a>
          <a
            href="mailto:support@hirepulse.in"
            class="border-2 border-white text-white hover:bg-white hover:text-blue-700 font-semibold px-8 py-4 rounded-lg transition duration-200"
          >
            Email Us
          </a>
        </div>

        <div class="mt-8 pt-8 border-t border-white/20">
          <p class="text-blue-100">
            <strong>Response Time:</strong> We typically respond within 24 hours during business days
          </p>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  @keyframes slide-down {
    from {
      opacity: 0;
      max-height: 0;
    }
    to {
      opacity: 1;
      max-height: 500px;
    }
  }

  .animate-slide-down {
    animation: slide-down 0.3s ease-out;
  }
</style>
