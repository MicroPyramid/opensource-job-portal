<script>
  import { FileText, ChevronRight } from '@lucide/svelte';

  const lastUpdated = 'January 18, 2024';

  const sections = [
    { id: 'acceptance', title: '1. Acceptance of Terms' },
    { id: 'definitions', title: '2. Definitions' },
    { id: 'eligibility', title: '3. Eligibility' },
    { id: 'account', title: '4. Account Registration and Security' },
    { id: 'services', title: '5. Services Provided' },
    { id: 'user-conduct', title: '6. User Conduct and Prohibited Activities' },
    { id: 'content', title: '7. User Content and Intellectual Property' },
    { id: 'job-postings', title: '8. Job Postings and Applications' },
    { id: 'privacy', title: '9. Privacy and Data Protection' },
    { id: 'fees', title: '10. Fees and Payments' },
    { id: 'termination', title: '11. Termination and Suspension' },
    { id: 'disclaimers', title: '12. Disclaimers and Warranties' },
    { id: 'liability', title: '13. Limitation of Liability' },
    { id: 'indemnification', title: '14. Indemnification' },
    { id: 'disputes', title: '15. Dispute Resolution' },
    { id: 'modifications', title: '16. Modifications to Terms' },
    { id: 'general', title: '17. General Provisions' },
    { id: 'contact', title: '18. Contact Information' }
  ];

  function scrollToSection(id) {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
</script>

<svelte:head>
  <title>Terms of Service - HirePulse.in</title>
  <meta name="description" content="Terms of Service and User Agreement for HirePulse" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-16">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto text-center">
      <div class="flex justify-center mb-6">
        <div class="p-4 bg-white/10 rounded-full">
          <FileText size={40} />
        </div>
      </div>
      <h1 class="text-4xl md:text-5xl font-bold mb-4">Terms of Service</h1>
      <p class="text-xl text-blue-100">
        User Agreement and Acceptable Use Policy
      </p>
      <p class="text-sm text-blue-200 mt-4">
        Last Updated: {lastUpdated}
      </p>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-16 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid lg:grid-cols-4 gap-8 max-w-7xl mx-auto">

      <!-- Table of Contents (Sticky Sidebar) -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 lg:sticky lg:top-6">
          <h2 class="text-lg font-bold text-gray-800 mb-4">Table of Contents</h2>
          <nav class="space-y-2">
            {#each sections as section}
              <button
                onclick={() => scrollToSection(section.id)}
                class="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
              >
                <ChevronRight size={14} />
                <span class="flex-1">{section.title}</span>
              </button>
            {/each}
          </nav>
        </div>
      </div>

      <!-- Terms Content -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-8 md:p-12">

          <!-- Introduction -->
          <div class="mb-12 pb-8 border-b border-gray-200">
            <p class="text-gray-700 leading-relaxed mb-4">
              Welcome to HirePulse! These Terms of Service ("Terms") govern your access to and use of the HirePulse website, mobile application, and services (collectively, the "Platform"). By accessing or using our Platform, you agree to be bound by these Terms.
            </p>
            <p class="text-gray-700 leading-relaxed font-semibold">
              Please read these Terms carefully before using our Platform. If you do not agree with these Terms, you may not use our services.
            </p>
          </div>

          <!-- Section 1 -->
          <div id="acceptance" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">1. Acceptance of Terms</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                By creating an account, accessing, or using HirePulse in any manner, you acknowledge that you have read, understood, and agree to be bound by these Terms, as well as our Privacy Policy, which is incorporated herein by reference.
              </p>
              <p>
                These Terms constitute a legally binding agreement between you and HirePulse. If you are using the Platform on behalf of an organization, you represent and warrant that you have the authority to bind that organization to these Terms.
              </p>
            </div>
          </div>

          <!-- Section 2 -->
          <div id="definitions" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">2. Definitions</h2>
            <div class="text-gray-700 leading-relaxed space-y-3">
              <p><strong>"Platform"</strong> refers to the HirePulse website, mobile applications, and all related services.</p>
              <p><strong>"User"</strong> refers to any individual or entity that accesses or uses the Platform.</p>
              <p><strong>"Job Seeker"</strong> refers to individuals using the Platform to search for employment opportunities.</p>
              <p><strong>"Employer"</strong> refers to organizations or individuals posting job listings on the Platform.</p>
              <p><strong>"Content"</strong> refers to all information, data, text, software, graphics, or other materials uploaded, posted, or displayed on the Platform.</p>
            </div>
          </div>

          <!-- Section 3 -->
          <div id="eligibility" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">3. Eligibility</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                To use HirePulse, you must be:
              </p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>At least 18 years of age or the age of majority in your jurisdiction</li>
                <li>Capable of forming a binding contract under applicable law</li>
                <li>Not prohibited from using the Platform under the laws of India or any other applicable jurisdiction</li>
                <li>Not previously suspended or removed from the Platform</li>
              </ul>
              <p>
                By using the Platform, you represent and warrant that you meet all eligibility requirements.
              </p>
            </div>
          </div>

          <!-- Section 4 -->
          <div id="account" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">4. Account Registration and Security</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>4.1 Account Creation:</strong> To access certain features, you must create an account by providing accurate, current, and complete information.</p>
              <p><strong>4.2 Account Security:</strong> You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account. You agree to:</p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Use a strong, unique password</li>
                <li>Not share your password or account access with others</li>
                <li>Immediately notify us of any unauthorized use or security breach</li>
              </ul>
              <p><strong>4.3 Account Verification:</strong> We may verify your account information and may suspend or terminate accounts that provide false or misleading information.</p>
            </div>
          </div>

          <!-- Section 5 -->
          <div id="services" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">5. Services Provided</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>HirePulse provides a platform connecting job seekers with employment opportunities. Our services include:</p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Job search and discovery tools</li>
                <li>Profile creation and resume management</li>
                <li>Job application submission and tracking</li>
                <li>Communication tools between job seekers and employers</li>
                <li>Job posting and applicant management tools for employers</li>
                <li>Personalized job recommendations and alerts</li>
              </ul>
              <p>
                We reserve the right to modify, suspend, or discontinue any aspect of the Platform at any time without prior notice.
              </p>
            </div>
          </div>

          <!-- Section 6 -->
          <div id="user-conduct" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">6. User Conduct and Prohibited Activities</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>You agree NOT to:</p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Post false, inaccurate, misleading, or fraudulent information</li>
                <li>Impersonate any person or entity or misrepresent your affiliation</li>
                <li>Post discriminatory, harassing, or offensive content</li>
                <li>Use the Platform for any illegal purpose or in violation of any laws</li>
                <li>Scrape, copy, or aggregate data from the Platform without authorization</li>
                <li>Interfere with or disrupt the Platform's operation or servers</li>
                <li>Attempt to gain unauthorized access to any portion of the Platform</li>
                <li>Post spam, unsolicited communications, or pyramid schemes</li>
                <li>Use automated systems (bots, scrapers) without our express permission</li>
                <li>Collect or harvest personal information of other users</li>
              </ul>
            </div>
          </div>

          <!-- Section 7 -->
          <div id="content" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">7. User Content and Intellectual Property</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>7.1 Your Content:</strong> You retain ownership of content you post on the Platform (resumes, profiles, applications, etc.). By posting content, you grant HirePulse a worldwide, non-exclusive, royalty-free license to use, display, and distribute your content for the purpose of providing our services.</p>
              <p><strong>7.2 Platform Content:</strong> The Platform and its original content, features, and functionality are owned by HirePulse and are protected by international copyright, trademark, patent, trade secret, and other intellectual property laws.</p>
              <p><strong>7.3 Prohibited Use:</strong> You may not reproduce, distribute, modify, create derivative works, or exploit any part of the Platform without our express written permission.</p>
            </div>
          </div>

          <!-- Section 8 -->
          <div id="job-postings" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">8. Job Postings and Applications</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>8.1 Job Postings:</strong> Employers are solely responsible for the accuracy and legality of their job postings. All job postings must comply with applicable employment and anti-discrimination laws.</p>
              <p><strong>8.2 Applications:</strong> Job seekers are responsible for the accuracy of their application materials. Submitting false information may result in account termination.</p>
              <p><strong>8.3 No Employment Relationship:</strong> HirePulse does not guarantee employment or interviews. We are a platform facilitating connections and do not participate in hiring decisions.</p>
              <p><strong>8.4 Verification:</strong> While we verify company accounts, we cannot guarantee the authenticity of all job postings. Users should exercise due diligence.</p>
            </div>
          </div>

          <!-- Section 9 -->
          <div id="privacy" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">9. Privacy and Data Protection</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                Your privacy is important to us. Our collection, use, and protection of your personal information is governed by our <a href="/privacy" class="text-blue-600 hover:text-blue-700 underline">Privacy Policy</a>, which is incorporated into these Terms by reference.
              </p>
              <p>
                By using the Platform, you consent to the collection and use of your information as described in our Privacy Policy.
              </p>
            </div>
          </div>

          <!-- Section 10 -->
          <div id="fees" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">10. Fees and Payments</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>10.1 Free Services:</strong> Basic job search and application services are free for job seekers.</p>
              <p><strong>10.2 Paid Services:</strong> Certain premium features or employer services may require payment. All fees are disclosed before purchase.</p>
              <p><strong>10.3 Refunds:</strong> Fees are generally non-refundable except as required by law or as expressly stated in our refund policy.</p>
              <p><strong>10.4 Price Changes:</strong> We reserve the right to modify our pricing with 30 days' notice to affected users.</p>
            </div>
          </div>

          <!-- Section 11 -->
          <div id="termination" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">11. Termination and Suspension</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>11.1 By You:</strong> You may terminate your account at any time through your account settings.</p>
              <p><strong>11.2 By Us:</strong> We reserve the right to suspend or terminate your account if you:</p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Violate these Terms or our policies</li>
                <li>Engage in fraudulent or illegal activities</li>
                <li>Provide false or misleading information</li>
                <li>Harm the Platform or other users</li>
              </ul>
              <p><strong>11.3 Effect of Termination:</strong> Upon termination, your right to use the Platform ceases immediately. We may delete your data in accordance with our data retention policies.</p>
            </div>
          </div>

          <!-- Section 12 -->
          <div id="disclaimers" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">12. Disclaimers and Warranties</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p class="font-semibold uppercase">
                THE PLATFORM IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED.
              </p>
              <p>
                We disclaim all warranties, including but not limited to:
              </p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Merchantability, fitness for a particular purpose, and non-infringement</li>
                <li>The accuracy, completeness, or reliability of any content</li>
                <li>The availability of the Platform or that it will be uninterrupted or error-free</li>
                <li>The results that may be obtained from using the Platform</li>
              </ul>
            </div>
          </div>

          <!-- Section 13 -->
          <div id="liability" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">13. Limitation of Liability</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p class="font-semibold uppercase">
                TO THE MAXIMUM EXTENT PERMITTED BY LAW, HIREPULSE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES ARISING FROM YOUR USE OF THE PLATFORM.
              </p>
              <p>
                Our total liability to you for any claims arising from your use of the Platform shall not exceed the amount you paid us in the 12 months preceding the claim, or ₹1,000, whichever is greater.
              </p>
            </div>
          </div>

          <!-- Section 14 -->
          <div id="indemnification" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">14. Indemnification</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                You agree to indemnify, defend, and hold harmless HirePulse, its affiliates, officers, directors, employees, and agents from and against any claims, liabilities, damages, losses, and expenses arising from:
              </p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Your use of the Platform</li>
                <li>Your violation of these Terms</li>
                <li>Your violation of any rights of another party</li>
                <li>Your content posted on the Platform</li>
              </ul>
            </div>
          </div>

          <!-- Section 15 -->
          <div id="disputes" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">15. Dispute Resolution</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>15.1 Governing Law:</strong> These Terms shall be governed by and construed in accordance with the laws of India.</p>
              <p><strong>15.2 Jurisdiction:</strong> Any disputes arising from these Terms or your use of the Platform shall be subject to the exclusive jurisdiction of the courts in Mumbai, Maharashtra, India.</p>
              <p><strong>15.3 Informal Resolution:</strong> Before filing a claim, you agree to attempt to resolve the dispute informally by contacting us at legal@hirepulse.in.</p>
            </div>
          </div>

          <!-- Section 16 -->
          <div id="modifications" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">16. Modifications to Terms</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                We reserve the right to modify these Terms at any time. We will notify users of material changes via email or through a notice on the Platform.
              </p>
              <p>
                Your continued use of the Platform after changes become effective constitutes your acceptance of the revised Terms. If you do not agree to the modified Terms, you must stop using the Platform.
              </p>
            </div>
          </div>

          <!-- Section 17 -->
          <div id="general" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">17. General Provisions</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p><strong>17.1 Entire Agreement:</strong> These Terms, together with our Privacy Policy, constitute the entire agreement between you and HirePulse.</p>
              <p><strong>17.2 Severability:</strong> If any provision of these Terms is found to be unenforceable, the remaining provisions shall remain in full force.</p>
              <p><strong>17.3 Waiver:</strong> Our failure to enforce any right or provision of these Terms shall not constitute a waiver of such right or provision.</p>
              <p><strong>17.4 Assignment:</strong> You may not assign or transfer these Terms without our prior written consent. We may assign these Terms without restriction.</p>
            </div>
          </div>

          <!-- Section 18 -->
          <div id="contact" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">18. Contact Information</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                If you have questions about these Terms, please contact us:
              </p>
              <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-4">
                <p class="font-semibold text-gray-800 mb-2">HirePulse</p>
                <p>Email: <a href="mailto:legal@hirepulse.in" class="text-blue-600 hover:text-blue-700 underline">legal@hirepulse.in</a></p>
                <p>Support: <a href="mailto:support@hirepulse.in" class="text-blue-600 hover:text-blue-700 underline">support@hirepulse.in</a></p>
                <p>Phone: +91 1800-123-4567</p>
                <p>Address: Mumbai, Maharashtra, India</p>
              </div>
            </div>
          </div>

          <!-- Acknowledgment -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
            <p class="text-sm text-blue-900 font-semibold mb-2">
              Acknowledgment
            </p>
            <p class="text-sm text-blue-800">
              By using HirePulse, you acknowledge that you have read, understood, and agree to be bound by these Terms of Service.
            </p>
          </div>

        </div>
      </div>

    </div>
  </div>
</section>

<style>
  .scroll-mt-6 {
    scroll-margin-top: 1.5rem;
  }
</style>
