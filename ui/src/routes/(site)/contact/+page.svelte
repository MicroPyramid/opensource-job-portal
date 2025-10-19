<script>
  import { Mail, Phone, MapPin, Send, Clock, MessageCircle, HelpCircle, CheckCircle, AlertCircle } from '@lucide/svelte';

  let formData = {
    name: '',
    email: '',
    subject: '',
    category: 'general',
    message: ''
  };

  let errors = {};
  let isSubmitting = false;
  let submitSuccess = false;

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
      details: 'support@hirepulse.in',
      link: 'mailto:support@hirepulse.in',
      description: 'Send us an email anytime'
    },
    {
      icon: Phone,
      title: 'Call Us',
      details: '+91 1800-123-4567',
      link: 'tel:+911800123 4567',
      description: 'Mon-Fri, 9AM-6PM IST'
    },
    {
      icon: MapPin,
      title: 'Visit Us',
      details: 'Mumbai, Maharashtra, India',
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
      question: 'Do you offer phone support?',
      answer: 'Yes! Our support team is available Mon-Fri, 9AM-6PM IST at +91 1800-123-4567.'
    },
    {
      question: 'Can I visit your office?',
      answer: 'Yes, but we recommend scheduling an appointment in advance by contacting us first.'
    }
  ];

  function validateForm() {
    errors = {};
    let isValid = true;

    if (!formData.name.trim()) {
      errors.name = 'Name is required';
      isValid = false;
    }

    if (!formData.email.trim()) {
      errors.email = 'Email is required';
      isValid = false;
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Please enter a valid email address';
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

  async function handleSubmit() {
    if (!validateForm()) {
      return;
    }

    isSubmitting = true;
    submitSuccess = false;

    try {
      // TODO: Replace with actual API call
      console.log('Submitting contact form:', formData);

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      submitSuccess = true;

      // Reset form
      formData = {
        name: '',
        email: '',
        subject: '',
        category: 'general',
        message: ''
      };

      // Auto-hide success message after 10 seconds
      setTimeout(() => {
        submitSuccess = false;
      }, 10000);
    } catch (error) {
      console.error('Contact form error:', error);
      errors.submit = 'Failed to send message. Please try again or email us directly.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Contact Us - HirePulse.in</title>
  <meta name="description" content="Get in touch with HirePulse support team" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-16 md:py-20">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-3xl mx-auto text-center">
      <h1 class="text-4xl md:text-5xl font-bold mb-6">Get In Touch</h1>
      <p class="text-xl text-blue-100">
        Have a question or need help? We're here to assist you. Reach out to our team and we'll get back to you as soon as possible.
      </p>
    </div>
  </div>
</section>

<!-- Contact Info Cards -->
<section class="py-12 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
      {#each contactInfo as info}
        <div class="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-8 border border-blue-100 text-center hover:shadow-lg transition-shadow duration-300">
          <div class="flex justify-center mb-4">
            <div class="p-4 bg-blue-600 rounded-full">
              <svelte:component this={info.icon} class="text-white" size={28} />
            </div>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">{info.title}</h3>
          {#if info.link}
            <a href={info.link} class="text-blue-600 hover:text-blue-700 font-semibold text-lg mb-2 block">
              {info.details}
            </a>
          {:else}
            <p class="text-gray-800 font-semibold text-lg mb-2">{info.details}</p>
          {/if}
          <p class="text-sm text-gray-600">{info.description}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-16 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">

      <!-- Contact Form -->
      <div class="lg:col-span-2">
        <div class="bg-white rounded-xl shadow-lg p-8 border border-gray-100">
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-2">Send Us a Message</h2>
            <p class="text-gray-600">Fill out the form below and we'll get back to you shortly</p>
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
            <!-- Name -->
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700 mb-2">
                Your Name *
              </label>
              <input
                id="name"
                type="text"
                bind:value={formData.name}
                placeholder="John Doe"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                class:border-red-500={errors.name}
                disabled={isSubmitting}
              />
              {#if errors.name}
                <p class="mt-1 text-sm text-red-600">{errors.name}</p>
              {/if}
            </div>

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
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-blue-100 rounded-lg">
              <Clock class="text-blue-600" size={20} />
            </div>
            <h3 class="text-lg font-bold text-gray-800">Business Hours</h3>
          </div>

          <div class="space-y-3 text-sm">
            <div class="flex justify-between">
              <span class="text-gray-600">Monday - Friday</span>
              <span class="font-medium text-gray-800">9:00 AM - 6:00 PM</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Saturday</span>
              <span class="font-medium text-gray-800">10:00 AM - 4:00 PM</span>
            </div>
            <div class="flex justify-between">
              <span class="text-gray-600">Sunday</span>
              <span class="font-medium text-gray-800">Closed</span>
            </div>
          </div>

          <p class="text-xs text-gray-500 mt-4">All times are in Indian Standard Time (IST)</p>
        </div>

        <!-- Quick Help -->
        <div class="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-blue-600 rounded-lg">
              <HelpCircle class="text-white" size={20} />
            </div>
            <h3 class="text-lg font-bold text-blue-900">Need Quick Help?</h3>
          </div>

          <p class="text-sm text-blue-800 mb-4">
            Check out our help center for instant answers to common questions.
          </p>

          <a
            href="/help"
            class="block w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition-colors duration-200 text-center text-sm"
          >
            Visit Help Center
          </a>
        </div>

        <!-- FAQs Preview -->
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div class="flex items-center gap-3 mb-4">
            <div class="p-2 bg-purple-100 rounded-lg">
              <MessageCircle class="text-purple-600" size={20} />
            </div>
            <h3 class="text-lg font-bold text-gray-800">Quick FAQs</h3>
          </div>

          <div class="space-y-4">
            {#each faqs as faq}
              <div>
                <h4 class="font-semibold text-gray-800 text-sm mb-1">{faq.question}</h4>
                <p class="text-xs text-gray-600">{faq.answer}</p>
              </div>
            {/each}
          </div>

          <a
            href="/help"
            class="text-blue-600 hover:text-blue-700 font-medium text-sm mt-4 inline-block"
          >
            View all FAQs →
          </a>
        </div>
      </div>

    </div>
  </div>
</section>

<!-- Alternative Contact Methods -->
<section class="py-16 bg-white">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-12">
        <h2 class="text-3xl font-bold text-gray-800 mb-4">Other Ways to Reach Us</h2>
        <p class="text-lg text-gray-600">Choose the method that works best for you</p>
      </div>

      <div class="grid md:grid-cols-2 gap-6">
        <div class="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-8 border border-blue-200">
          <h3 class="text-xl font-bold text-gray-800 mb-3">For Job Seekers</h3>
          <p class="text-gray-700 mb-4">
            Having trouble with your account, applications, or job search?
          </p>
          <a
            href="mailto:jobseekers@hirepulse.in"
            class="text-blue-600 hover:text-blue-700 font-semibold"
          >
            jobseekers@hirepulse.in
          </a>
        </div>

        <div class="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-8 border border-purple-200">
          <h3 class="text-xl font-bold text-gray-800 mb-3">For Employers</h3>
          <p class="text-gray-700 mb-4">
            Questions about posting jobs, managing applicants, or pricing?
          </p>
          <a
            href="mailto:employers@hirepulse.in"
            class="text-purple-600 hover:text-purple-700 font-semibold"
          >
            employers@hirepulse.in
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
