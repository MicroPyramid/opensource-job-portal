<script lang="ts">
  import { goto } from '$app/navigation';
  import { 
    MapPin, 
    DollarSign, 
    Clock, 
    Building, 
    Bookmark, 
    BookmarkCheck,
    Send, 
    Phone, 
    Mail, 
    Calendar,
    Users,
    Award,
    CheckCircle,
    ArrowLeft,
    Share2,
    ExternalLink
  } from '@lucide/svelte';
  
  interface Recruiter {
    name: string;
    title: string;
    email: string;
    phone: string;
    avatar: string;
  }

  interface CompanyInfo {
    founded: string;
    employees: string;
    industry: string;
    website: string;
  }

  interface JobDetails {
    id: string;
    title: string;
    company: string;
    companyLogo: string;
    location: string;
    locationType: string;
    salary: string;
    jobType: string;
    experience: string;
    postedDate: string;
    applicants: number;
    description: string;
    requirements: string[];
    responsibilities: string[];
    benefits: string[];
    recruiter: Recruiter;
    company_info: CompanyInfo;
  }

  interface RelatedJob {
    id: string;
    title: string;
    company: string;
    location: string;
    salary: string;
    logo: string;
    postedDate: string;
  }

  let isAuthenticated = $state(false); // Replace with actual auth state
  let isJobSaved = $state(false);
  let showApplyModal = $state(false);
  let showLoginPrompt = $state(false);
  let isApplying = $state(false);
  
  // Mock job data - replace with actual data fetching
  let jobData = $state<JobDetails>({
    id: '1',
    title: "Senior Frontend Developer",
    company: "TechCorp Solutions",
    companyLogo: "/api/placeholder/80/80",
    location: "Bangalore, Karnataka",
    locationType: "Hybrid",
    salary: "₹15-25 LPA",
    jobType: "Full-time",
    experience: "3-5 years",
    postedDate: "2 days ago",
    applicants: 47,
    description: `We are looking for a skilled Frontend Developer to join our dynamic team. You will be responsible for developing user-facing web applications using modern JavaScript frameworks and ensuring excellent user experience.`,
    requirements: [
      "3+ years of experience in React.js or Vue.js",
      "Strong proficiency in JavaScript, HTML5, and CSS3",
      "Experience with responsive design and mobile-first development",
      "Knowledge of state management libraries (Redux, Vuex)",
      "Familiarity with modern build tools (Webpack, Vite)",
      "Understanding of RESTful APIs and GraphQL",
      "Experience with Git version control"
    ],
    responsibilities: [
      "Develop and maintain user-facing web applications",
      "Collaborate with design team to implement UI/UX designs",
      "Optimize applications for maximum speed and scalability",
      "Write clean, maintainable, and well-documented code",
      "Participate in code reviews and team discussions",
      "Stay updated with latest frontend technologies and trends"
    ],
    benefits: [
      "Competitive salary with performance bonuses",
      "Health insurance for employee and family",
      "Flexible working hours and remote work options",
      "Learning and development opportunities",
      "Annual company retreats and team building activities",
      "Modern office with latest technology and amenities"
    ],
    recruiter: {
      name: "Sarah Johnson",
      title: "HR Manager",
      email: "sarah.johnson@techcorp.com",
      phone: "+91 98765 43210",
      avatar: "/api/placeholder/60/60"
    },
    company_info: {
      founded: "2015",
      employees: "500-1000",
      industry: "Technology",
      website: "https://techcorp.com"
    }
  });
  
  // Mock related jobs
  let relatedJobs = [
    {
      id: "2",
      title: "React Developer",
      company: "StartupTech",
      location: "Mumbai, Maharashtra",
      salary: "₹12-18 LPA",
      logo: "/api/placeholder/50/50",
      postedDate: "1 day ago"
    },
    {
      id: "3", 
      title: "Full Stack Developer",
      company: "InnovateCorp",
      location: "Pune, Maharashtra",
      salary: "₹18-28 LPA",
      logo: "/api/placeholder/50/50",
      postedDate: "3 days ago"
    },
    {
      id: "4",
      title: "Frontend Engineer",
      company: "WebSolutions",
      location: "Hyderabad, Telangana", 
      salary: "₹14-22 LPA",
      logo: "/api/placeholder/50/50",
      postedDate: "5 days ago"
    }
  ];
  
  function handleApply(): void {
    if (!isAuthenticated) {
      showLoginPrompt = true;
      return;
    }
    showApplyModal = true;
  }
  
  function handleSaveJob(): void {
    isJobSaved = !isJobSaved;
    // Add API call to save/unsave job
  }
  
  function handleShare(): void {
    if (typeof navigator === 'undefined') {
      return;
    }

    const shareData = {
      title: jobData.title,
      text: `Check out this job at ${jobData.company}`,
      url: typeof window !== 'undefined' ? window.location.href : ''
    };

    if (navigator.share) {
      void navigator.share(shareData);
    } else if (navigator.clipboard && shareData.url) {
      void navigator.clipboard.writeText(shareData.url);
    }
  }
  
  async function submitApplication(): Promise<void> {
    isApplying = true;
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000));
    isApplying = false;
    showApplyModal = false;
    // Show success message
  }
  
  function navigateToJob(jobId: string): void {
    goto(`/jobs/${jobId}`);
  }
</script>

<svelte:head>
  <title>{jobData.title} at {jobData.company} | HirePulse.in</title>
  <meta name="description" content="Apply for {jobData.title} position at {jobData.company}. {jobData.salary} • {jobData.location} • {jobData.jobType}" />
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Header with back button -->
  <div class="bg-white border-b border-gray-200 sticky top-0 z-10">
    <div class="max-w-6xl mx-auto px-4 py-4">
      <button 
        onclick={() => history.back()} 
        class="flex items-center gap-2 text-gray-600 hover:text-gray-900 transition-colors"
      >
        <ArrowLeft class="w-5 h-5" />
        <span class="hidden sm:inline">Back to Jobs</span>
      </button>
    </div>
  </div>

  <div class="max-w-6xl mx-auto px-4 py-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Content -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Job Header Card -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div class="flex flex-col sm:flex-row gap-4">
            <img 
              src={jobData.companyLogo} 
              alt="{jobData.company} logo"
              class="w-16 h-16 rounded-lg object-cover border border-gray-200"
            />
            <div class="flex-1">
              <h1 class="text-2xl font-bold text-gray-900 mb-2">{jobData.title}</h1>
              <div class="flex items-center gap-2 text-lg font-semibold text-blue-600 mb-3">
                <Building class="w-5 h-5" />
                {jobData.company}
              </div>
              
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm text-gray-600">
                <div class="flex items-center gap-2">
                  <MapPin class="w-4 h-4" />
                  {jobData.location} • {jobData.locationType}
                </div>
                <div class="flex items-center gap-2">
                  <DollarSign class="w-4 h-4" />
                  {jobData.salary}
                </div>
                <div class="flex items-center gap-2">
                  <Clock class="w-4 h-4" />
                  {jobData.jobType} • {jobData.experience}
                </div>
                <div class="flex items-center gap-2">
                  <Calendar class="w-4 h-4" />
                  Posted {jobData.postedDate}
                </div>
              </div>
            </div>
          </div>
          
          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 mt-6 pt-6 border-t border-gray-100">
            <button 
              onclick={handleApply}
              class="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2"
            >
              <Send class="w-5 h-5" />
              Apply Now
            </button>
            <button 
              onclick={handleSaveJob}
              class="px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 {isJobSaved ? 'text-blue-600 border-blue-300 bg-blue-50' : 'text-gray-700'}"
            >
              {#if isJobSaved}
                <BookmarkCheck class="w-5 h-5" />
                Saved
              {:else}
                <Bookmark class="w-5 h-5" />
                Save Job
              {/if}
            </button>
            <button 
              onclick={handleShare}
              class="px-6 py-3 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 text-gray-700"
            >
              <Share2 class="w-5 h-5" />
              Share
            </button>
          </div>
        </div>

        <!-- Job Description -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Job Description</h2>
          <p class="text-gray-700 leading-relaxed">{jobData.description}</p>
        </div>

        <!-- Responsibilities -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Key Responsibilities</h2>
          <ul class="space-y-3">
            {#each jobData.responsibilities as responsibility}
              <li class="flex gap-3">
                <CheckCircle class="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                <span class="text-gray-700">{responsibility}</span>
              </li>
            {/each}
          </ul>
        </div>

        <!-- Requirements -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Requirements</h2>
          <ul class="space-y-3">
            {#each jobData.requirements as requirement}
              <li class="flex gap-3">
                <Award class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <span class="text-gray-700">{requirement}</span>
              </li>
            {/each}
          </ul>
        </div>

        <!-- Benefits -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h2 class="text-xl font-bold text-gray-900 mb-4">Benefits & Perks</h2>
          <ul class="space-y-3">
            {#each jobData.benefits as benefit}
              <li class="flex gap-3">
                <CheckCircle class="w-5 h-5 text-emerald-500 mt-0.5 flex-shrink-0" />
                <span class="text-gray-700">{benefit}</span>
              </li>
            {/each}
          </ul>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Quick Apply Card -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-24">
          <div class="text-center mb-4">
            <div class="flex items-center justify-center gap-2 text-sm text-gray-600 mb-2">
              <Users class="w-4 h-4" />
              {jobData.applicants} applicants
            </div>
          </div>
          
          <button 
            onclick={handleApply}
            class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 mb-3"
          >
            <Send class="w-5 h-5" />
            Quick Apply
          </button>
          
          <button 
            onclick={handleSaveJob}
            class="w-full px-6 py-2 rounded-lg border border-gray-300 hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 {isJobSaved ? 'text-blue-600 border-blue-300 bg-blue-50' : 'text-gray-700'}"
          >
            {#if isJobSaved}
              <BookmarkCheck class="w-4 h-4" />
              Saved
            {:else}
              <Bookmark class="w-4 h-4" />
              Save for Later
            {/if}
          </button>
        </div>

        <!-- Company Info -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">About {jobData.company}</h3>
          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Founded</span>
              <span class="font-medium">{jobData.company_info.founded}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Employees</span>
              <span class="font-medium">{jobData.company_info.employees}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Industry</span>
              <span class="font-medium">{jobData.company_info.industry}</span>
            </div>
          </div>
          <a 
            href={jobData.company_info.website}
            target="_blank"
            rel="noopener noreferrer"
            class="w-full mt-4 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2 text-gray-700"
          >
            <ExternalLink class="w-4 h-4" />
            Visit Website
          </a>
        </div>

        <!-- Recruiter Contact -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 class="text-lg font-bold text-gray-900 mb-4">Contact Recruiter</h3>
          <div class="flex items-center gap-3 mb-4">
            <img 
              src={jobData.recruiter.avatar}
              alt="{jobData.recruiter.name}"
              class="w-12 h-12 rounded-full object-cover"
            />
            <div>
              <div class="font-semibold text-gray-900">{jobData.recruiter.name}</div>
              <div class="text-sm text-gray-600">{jobData.recruiter.title}</div>
            </div>
          </div>
          <div class="space-y-3">
            <a 
              href="mailto:{jobData.recruiter.email}"
              class="flex items-center gap-3 text-sm text-gray-700 hover:text-blue-600 transition-colors"
            >
              <Mail class="w-4 h-4" />
              {jobData.recruiter.email}
            </a>
            <a 
              href="tel:{jobData.recruiter.phone}"
              class="flex items-center gap-3 text-sm text-gray-700 hover:text-blue-600 transition-colors"
            >
              <Phone class="w-4 h-4" />
              {jobData.recruiter.phone}
            </a>
          </div>
        </div>
      </div>
    </div>

    <!-- Related Jobs -->
    <div class="mt-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6">Related Jobs</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {#each relatedJobs as job}
          <button
            type="button"
            class="w-full text-left bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer"
            onclick={() => navigateToJob(job.id)}
            aria-label="View job {job.title} at {job.company}"
          >
            <div class="flex items-start gap-4 mb-4">
              <img src={job.logo} alt="{job.company} logo" class="w-12 h-12 rounded-lg object-cover border border-gray-200" />
              <div class="flex-1">
                <h3 class="font-semibold text-gray-900 hover:text-blue-600 transition-colors">{job.title}</h3>
                <p class="text-gray-600 text-sm">{job.company}</p>
              </div>
            </div>
            <div class="space-y-2 text-sm text-gray-600">
              <div class="flex items-center gap-2">
                <MapPin class="w-4 h-4" />
                {job.location}
              </div>
              <div class="flex items-center gap-2">
                <DollarSign class="w-4 h-4" />
                {job.salary}
              </div>
              <div class="flex items-center gap-2">
                <Calendar class="w-4 h-4" />
                Posted {job.postedDate}
              </div>
            </div>
          </button>
        {/each}
      </div>
    </div>
  </div>
</div>

<!-- Apply Modal -->
{#if showApplyModal}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    onclick={() => (showApplyModal = false)}
    onkeydown={(event) => {
      if (event.key === 'Escape' || event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        showApplyModal = false;
      }
    }}
    role="button"
    tabindex="0"
    aria-label="Close apply modal"
  >
    <div
      class="bg-white rounded-xl max-w-md w-full p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Apply for job"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <h3 class="text-xl font-bold text-gray-900 mb-4">Apply for {jobData.title}</h3>
      <p class="text-gray-600 mb-6">Your profile and resume will be sent to {jobData.company} for review.</p>
      
      <div class="flex gap-3">
        <button 
          onclick={() => showApplyModal = false}
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          disabled={isApplying}
        >
          Cancel
        </button>
        <button 
          onclick={submitApplication}
          class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
          disabled={isApplying}
        >
          {#if isApplying}
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Applying...
          {:else}
            <Send class="w-4 h-4" />
            Confirm Application
          {/if}
        </button>
      </div>
    </div>
  </div>
{/if}

<!-- Login Prompt Modal -->
{#if showLoginPrompt}
  <div
    class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
    onclick={() => (showLoginPrompt = false)}
    onkeydown={(event) => {
      if (event.key === 'Escape' || event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        showLoginPrompt = false;
      }
    }}
    role="button"
    tabindex="0"
    aria-label="Dismiss login prompt"
  >
    <div
      class="bg-white rounded-xl max-w-md w-full p-6"
      role="dialog"
      aria-modal="true"
      aria-label="Login required"
      tabindex="-1"
      onpointerdown={(event) => event.stopPropagation()}
    >
      <h3 class="text-xl font-bold text-gray-900 mb-4">Login Required</h3>
      <p class="text-gray-600 mb-6">Please login to apply for this job position.</p>
      
      <div class="flex gap-3">
        <button 
          onclick={() => showLoginPrompt = false}
          class="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        <button 
          onclick={() => goto('/login')}
          class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          Login
        </button>
      </div>
    </div>
  </div>
{/if}
