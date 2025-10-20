<script lang="ts">
  import { Mail, Phone, MapPin, Send, Clock, MessageCircle, HelpCircle, CheckCircle, AlertCircle } from '@lucide/svelte';
  import { submitContactForm, type ContactFormData } from '$lib/api/contact';
  import { toast } from '$lib/stores/toast';

  interface FormData {
    firstName: string;
    lastName: string;
    email: string;
    phone: string;
    subject: string;
    category: string;
    message: string;
  }

  interface FormErrors {
    firstName?: string;
    email?: string;
    subject?: string;
    message?: string;
    phone?: string;
    submit?: string;
  }

  const initialFormData: FormData = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    subject: '',
    category: 'general',
    message: ''
  };

  let formData = $state<FormData>({ ...initialFormData });

  let errors = $state<FormErrors>({});
  let isSubmitting = $state(false);
  let submitSuccess = $state(false);

  const categories = [
    { value: 'general', label: 'General Inquiry' },
    { value: 'support', label: 'Technical Support' },
    { value: 'job_seeker', label: 'Job Seeker Help' },
    { value: 'employer', label: 'Employer/Recruiter' },
    { value: 'partnership', label: 'Partnership Opportunities' },
    { value: 'feedback', label: 'Feedback & Suggestions' }
  ];

  const contactInfo = [
    {
      icon: Mail,
      title: 'Email Us',
      details: 'peeljobs@micropyramid.com',
      link: 'mailto:peeljobs@micropyramid.com',
      description: 'Send us an email anytime'
    },
    {
      icon: MapPin,
      title: 'Office Location',
      details: 'Hyderabad, Telangana, India',
      link: null,
      description: 'Head Office'
    }
  ];

  const faqs = [
    {
      question: 'How quickly will I get a response?',
      answer: 'We typically respond to all inquiries within 24 hours during business days.'
    },
    {
      question: 'Is PeelJobs really free?',
      answer: 'Yes! PeelJobs is completely free for both job seekers and employers. No hidden fees, ever.'
    },
    {
      question: 'Can I visit your office?',
      answer: 'Yes, but we recommend scheduling an appointment in advance by contacting us first.'
    }
  ];

  function validateForm(): boolean {
    errors = {};
    let isValid = true;

    if (!formData.firstName.trim()) {
      errors.firstName = 'First name is required';
      isValid = false;
    }

    if (!formData.email.trim()) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
      isValid = false;
    }

    if (formData.phone && !/^\d{10,12}$/.test(formData.phone.replace(/\s/g, ''))) {
      errors.phone = 'Please enter a valid phone number (10-12 digits)';
      isValid = false;
    }

    if (!formData.subject.trim()) {
      errors.subject = 'Subject is required';
      isValid = false;
    }

    if (!formData.message.trim()) {
      errors.message = 'Message is required';
      isValid = false;
    } else if (formData.message.trim().length < 10) {
      errors.message = 'Message must be at least 10 characters';
      isValid = false;
    }

    return isValid;
  }

  async function handleSubmit(event: SubmitEvent): Promise<void> {
    event.preventDefault();

    if (!validateForm()) {
      return;
    }

    isSubmitting = true;
    submitSuccess = false;
    errors.submit = undefined;

    try {
      // Prepare API request data
      const requestData: ContactFormData = {
        first_name: formData.firstName.trim(),
        last_name: formData.lastName.trim() || undefined,
        email: formData.email.trim(),
        phone: formData.phone ? parseInt(formData.phone.replace(/\s/g, '')) : undefined,
        category: formData.category,
        subject: formData.subject.trim(),
        comment: formData.message.trim()
      };

      // Submit to API
      const response = await submitContactForm(requestData);

      submitSuccess = true;
      toast.success('Message sent successfully! We\'ll get back to you within 24 hours.');

      // Reset form
      formData = { ...initialFormData };

      // Auto-hide success message after 10 seconds
      setTimeout(() => {
        submitSuccess = false;
      }, 10000);
    } catch (error: any) {
      console.error('Contact form error:', error);

      // Handle validation errors from API
      if (error.details) {
        // Map API field names to form field names
        if (error.details.first_name) errors.firstName = error.details.first_name[0];
        if (error.details.email) errors.email = error.details.email[0];
        if (error.details.phone) errors.phone = error.details.phone[0];
        if (error.details.subject) errors.subject = error.details.subject[0];
        if (error.details.comment) errors.message = error.details.comment[0];

        errors.submit = 'Please fix the errors above and try again.';
        toast.error('Please check the form for errors');
      } else {
        errors.submit = 'Failed to send message. Please try again or email us directly at peeljobs@micropyramid.com';
        toast.error('Failed to send message. Please try again.');
      }
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Contact Us - PeelJobs | Get in Touch with Our Support Team</title>
  <meta name="description" content="Have questions or need help? Contact the PeelJobs support team. We're here to assist job seekers and employers with our free job portal platform." />
  <link rel="canonical" href="https://peeljobs.com/contact/" />

  <!-- Open Graph -->
  <meta property="og:title" content="Contact PeelJobs Support - We're Here to Help" />
  <meta property="og:description" content="Get in touch with our team for any questions about our free job portal." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://peeljobs.com/contact/" />

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary" />
  <meta name="twitter:title" content="Contact PeelJobs" />
  <meta name="twitter:description" content="Reach out to our support team for assistance." />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-br from-blue-600 via-blue-700 to-blue-800 text-white py-12 md:py-16 relative overflow-hidden">
  <!-- Decorative background elements -->
  <div class="absolute inset-0 opacity-10">
    <div class="absolute top-10 left-10 w-64 h-64 bg-white rounded-full blur-3xl"></div>
    <div class="absolute bottom-10 right-10 w-96 h-96 bg-white rounded-full blur-3xl"></div>
  </div>

  <div class="container mx-auto px-4 lg:px-6 relative z-10">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 bg-white bg-opacity-20 rounded-full mb-6">
          <Mail size={32} class="md:w-12 md:h-12" />
        </div>
        <h1 class="text-3xl md:text-5xl font-bold mb-4">Get In Touch</h1>
        <p class="text-lg md:text-xl text-blue-100 max-w-2xl mx-auto">
          Have a question or need assistance? Our support team is here to help you. We typically respond within 24 hours.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Contact Info Cards -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
      {#each contactInfo as info}
        <div class="bg-white rounded-xl p-6 md:p-8 border border-gray-200 hover:border-blue-300 hover:shadow-xl transition-all duration-300 group">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="p-3 bg-blue-100 group-hover:bg-blue-600 rounded-lg transition-colors duration-300">
                <info.icon class="text-blue-600 group-hover:text-white transition-colors duration-300" size={24} />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <h3 class="text-lg font-bold text-gray-800 mb-2">{info.title}</h3>
              {#if info.link}
                <a href={info.link} class="text-blue-600 hover:text-blue-700 font-semibold text-base mb-1 block break-words">
                  {info.details}
                </a>
              {:else}
                <p class="text-gray-800 font-semibold text-base mb-1">{info.details}</p>
              {/if}
              <p class="text-sm text-gray-600">{info.description}</p>
            </div>
          </div>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 md:py-16 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">

      <!-- Contact Form -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-2xl shadow-xl p-6 md:p-8 border border-gray-200">
          <div class="mb-8">
            <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-2">Send Us a Message</h2>
            <p class="text-gray-600">Fill out the form below and our team will get back to you within 24 hours</p>
          </div>

          {#if submitSuccess}
            <div class="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3 animate-fade-in">
              <CheckCircle class="text-green-600 flex-shrink-0" size={24} />
              <div>
                <p class="text-green-700 font-medium">Message sent successfully!</p>
                <p class="text-sm text-green-600 mt-1">Thank you for contacting us. We'll respond within 24 hours.</p>
              </div>
            </div>
          {/if}

          <form onsubmit={handleSubmit} class="space-y-6">
            <!-- Name Fields -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- First Name -->
              <div>
                <label for="firstName" class="block text-sm font-medium text-gray-700 mb-2">
                  First Name *
                </label>
                <input
                  id="firstName"
                  type="text"
                  bind:value={formData.firstName}
                  placeholder="John"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.firstName}
                  disabled={isSubmitting}
                />
                {#if errors.firstName}
                  <p class="mt-1 text-sm text-red-600">{errors.firstName}</p>
                {/if}
              </div>

              <!-- Last Name -->
              <div>
                <label for="lastName" class="block text-sm font-medium text-gray-700 mb-2">
                  Last Name
                </label>
                <input
                  id="lastName"
                  type="text"
                  bind:value={formData.lastName}
                  placeholder="Doe"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  disabled={isSubmitting}
                />
              </div>
            </div>

            <!-- Email & Phone -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  id="email"
                  type="email"
                  bind:value={formData.email}
                  placeholder="john.doe@example.com"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.email}
                  disabled={isSubmitting}
                />
                {#if errors.email}
                  <p class="mt-1 text-sm text-red-600">{errors.email}</p>
                {/if}
              </div>

              <!-- Phone -->
              <div>
                <label for="phone" class="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <input
                  id="phone"
                  type="tel"
                  bind:value={formData.phone}
                  placeholder="9876543210"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  class:border-red-500={errors.phone}
                  disabled={isSubmitting}
                />
                {#if errors.phone}
                  <p class="mt-1 text-sm text-red-600">{errors.phone}</p>
                {:else}
                  <p class="mt-1 text-xs text-gray-500">Optional (10-12 digits)</p>
                {/if}
              </div>
            </div>

            <!-- Category -->
            <div>
              <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                id="category"
                bind:value={formData.category}
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                disabled={isSubmitting}
              >
                {#each categories as category}
                  <option value={category.value}>{category.label}</option>
                {/each}
              </select>
            </div>

            <!-- Subject -->
            <div>
              <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
                Subject *
              </label>
              <input
                id="subject"
                type="text"
                bind:value={formData.subject}
                placeholder="What is this regarding?"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                class:border-red-500={errors.subject}
                disabled={isSubmitting}
              />
              {#if errors.subject}
                <p class="mt-1 text-sm text-red-600">{errors.subject}</p>
              {/if}
            </div>

            <!-- Message -->
            <div>
              <label for="message" class="block text-sm font-medium text-gray-700 mb-2">
                Message *
              </label>
              <textarea
                id="message"
                bind:value={formData.message}
                placeholder="Tell us more about your inquiry..."
                rows="6"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                class:border-red-500={errors.message}
                disabled={isSubmitting}
              ></textarea>
              {#if errors.message}
                <p class="mt-1 text-sm text-red-600">{errors.message}</p>
              {:else}
                <p class="mt-1 text-xs text-gray-500">Minimum 10 characters</p>
              {/if}
            </div>

            <!-- Submit Error -->
            {#if errors.submit}
              <div class="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
                <AlertCircle class="text-red-600 flex-shrink-0" size={20} />
                <p class="text-sm text-red-600">{errors.submit}</p>
              </div>
            {/if}

            <!-- Submit Button -->
            <button
              type="submit"
              disabled={isSubmitting}
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-4 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {#if isSubmitting}
                <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Sending...
              {:else}
                <Send size={20} />
                Send Message
              {/if}
            </button>
          </form>
        </div>
      </div>

      <!-- Sidebar -->
      <div class="space-y-6">
        <!-- Business Hours -->
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center gap-3 mb-5">
            <div class="p-2.5 bg-blue-100 rounded-lg">
              <Clock class="text-blue-600" size={22} />
            </div>
            <h3 class="text-lg font-bold text-gray-800">Business Hours</h3>
          </div>

          <div class="space-y-3.5">
            <div class="flex justify-between items-center py-2 border-b border-gray-100">
              <span class="text-sm text-gray-600 font-medium">Monday - Friday</span>
              <span class="text-sm font-semibold text-gray-800">9:00 AM - 6:00 PM</span>
            </div>
            <div class="flex justify-between items-center py-2">
              <span class="text-sm text-gray-600 font-medium">Saturday & Sunday</span>
              <span class="text-sm font-semibold text-red-600">Closed</span>
            </div>
          </div>

          <div class="mt-4 pt-4 border-t border-gray-100">
            <p class="text-xs text-gray-500 flex items-center gap-2">
              <Clock size={14} />
              Indian Standard Time (IST)
            </p>
          </div>
        </div>

        <!-- Quick Help -->
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 border-2 border-blue-200 rounded-xl p-6 hover:shadow-lg transition-shadow duration-300">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2.5 bg-blue-600 rounded-lg shadow-md">
              <HelpCircle class="text-white" size={22} />
            </div>
            <h3 class="text-lg font-bold text-blue-900">Need Quick Help?</h3>
          </div>

          <p class="text-sm text-blue-800 mb-5 leading-relaxed">
            Check out our help center for instant answers to common questions about jobs and applications.
          </p>

          <a
            href="/help/"
            class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3.5 rounded-lg transition-all duration-200 text-center text-sm shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
          >
            Visit Help Center
          </a>
        </div>

        <!-- FAQs Preview -->
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-200 hover:shadow-xl transition-shadow duration-300">
          <div class="flex items-center gap-3 mb-5">
            <div class="p-2.5 bg-purple-100 rounded-lg">
              <MessageCircle class="text-purple-600" size={22} />
            </div>
            <h3 class="text-lg font-bold text-gray-800">Quick FAQs</h3>
          </div>

          <div class="space-y-4">
            {#each faqs as faq}
              <div class="pb-4 border-b border-gray-100 last:border-0 last:pb-0">
                <h4 class="font-semibold text-gray-800 text-sm mb-2 leading-snug">{faq.question}</h4>
                <p class="text-xs text-gray-600 leading-relaxed">{faq.answer}</p>
              </div>
            {/each}
          </div>

          <a
            href="/help/"
            class="text-blue-600 hover:text-blue-700 font-semibold text-sm mt-5 inline-flex items-center gap-1 group"
          >
            <span>View all FAQs</span>
            <span class="group-hover:translate-x-1 transition-transform duration-200">→</span>
          </a>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Alternative Contact Methods -->
<section class="py-12 md:py-16 bg-gradient-to-br from-gray-50 to-blue-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-5xl mx-auto">
      <div class="text-center mb-10 md:mb-12">
        <h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-3">Other Ways to Reach Us</h2>
        <p class="text-base md:text-lg text-gray-600">Choose the method that works best for you</p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white rounded-2xl p-6 md:p-8 border-2 border-blue-200 hover:border-blue-400 hover:shadow-xl transition-all duration-300 group">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-3 bg-blue-100 group-hover:bg-blue-600 rounded-lg transition-colors duration-300">
              <Mail class="text-blue-600 group-hover:text-white transition-colors duration-300" size={24} />
            </div>
            <h3 class="text-xl font-bold text-gray-800">For Job Seekers</h3>
          </div>
          <p class="text-gray-700 mb-5 leading-relaxed">
            Having trouble with your account, applications, or job search? Our support team is ready to assist you.
          </p>
          <a
            href="mailto:peeljobs@micropyramid.com"
            class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold group"
          >
            <Mail size={18} />
            <span class="break-all">peeljobs@micropyramid.com</span>
          </a>
        </div>

        <div class="bg-white rounded-2xl p-6 md:p-8 border-2 border-purple-200 hover:border-purple-400 hover:shadow-xl transition-all duration-300 group">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-3 bg-purple-100 group-hover:bg-purple-600 rounded-lg transition-colors duration-300">
              <Mail class="text-purple-600 group-hover:text-white transition-colors duration-300" size={24} />
            </div>
            <h3 class="text-xl font-bold text-gray-800">For Employers</h3>
          </div>
          <p class="text-gray-700 mb-5 leading-relaxed">
            Questions about posting jobs or managing applicants? We're here to help you find the right talent!
          </p>
          <a
            href="mailto:peeljobs@micropyramid.com"
            class="inline-flex items-center gap-2 text-purple-600 hover:text-purple-700 font-semibold group"
          >
            <Mail size={18} />
            <span class="break-all">peeljobs@micropyramid.com</span>
          </a>
        </div>
      </div>
    </div>
  </div>
</section>

<style>
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }
</style>
