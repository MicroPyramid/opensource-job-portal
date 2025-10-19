<script>
  import { Shield, ChevronRight } from '@lucide/svelte';

  const lastUpdated = 'January 18, 2024';

  const sections = [
    { id: 'introduction', title: '1. Introduction' },
    { id: 'information-collect', title: '2. Information We Collect' },
    { id: 'how-we-use', title: '3. How We Use Your Information' },
    { id: 'information-sharing', title: '4. Information Sharing and Disclosure' },
    { id: 'data-security', title: '5. Data Security' },
    { id: 'data-retention', title: '6. Data Retention' },
    { id: 'your-rights', title: '7. Your Rights and Choices' },
    { id: 'cookies', title: '8. Cookies and Tracking Technologies' },
    { id: 'third-party', title: '9. Third-Party Links and Services' },
    { id: 'children', title: '10. Children\'s Privacy' },
    { id: 'international', title: '11. International Data Transfers' },
    { id: 'changes', title: '12. Changes to Privacy Policy' },
    { id: 'contact', title: '13. Contact Us' }
  ];

  function scrollToSection(id) {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
</script>

<svelte:head>
  <title>Privacy Policy - HirePulse.in</title>
  <meta name="description" content="Privacy Policy and data protection practices for HirePulse" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-16">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="max-w-4xl mx-auto text-center">
      <div class="flex justify-center mb-6">
        <div class="p-4 bg-white/10 rounded-full">
          <Shield size={40} />
        </div>
      </div>
      <h1 class="text-4xl md:text-5xl font-bold mb-4">Privacy Policy</h1>
      <p class="text-xl text-blue-100">
        Your privacy is important to us. Learn how we collect, use, and protect your personal information.
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

      <!-- Privacy Policy Content -->
      <div class="lg:col-span-3">
        <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-8 md:p-12">

          <!-- Introduction -->
          <div id="introduction" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">1. Introduction</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                Welcome to HirePulse! This Privacy Policy explains how HirePulse ("we," "our," or "us") collects, uses, discloses, and protects your personal information when you use our website, mobile application, and services (collectively, the "Platform").
              </p>
              <p>
                We are committed to protecting your privacy and handling your personal information with care and transparency. By using HirePulse, you consent to the data practices described in this policy.
              </p>
              <p class="font-semibold">
                Please read this Privacy Policy carefully. If you do not agree with our practices, please do not use our Platform.
              </p>
            </div>
          </div>

          <!-- Section 2 -->
          <div id="information-collect" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">2. Information We Collect</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>We collect several types of information from and about users of our Platform:</p>

              <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 my-4">
                <h3 class="font-semibold text-blue-900 mb-3">2.1 Information You Provide Directly</h3>
                <ul class="list-disc list-inside space-y-2 text-blue-800">
                  <li><strong>Account Information:</strong> Name, email address, phone number, password</li>
                  <li><strong>Profile Information:</strong> Work experience, education, skills, professional summary, resume, portfolio</li>
                  <li><strong>Application Information:</strong> Job applications, cover letters, responses to employer questions</li>
                  <li><strong>Communication Data:</strong> Messages sent through our platform, support inquiries, feedback</li>
                  <li><strong>Payment Information:</strong> Billing details for premium services (processed securely by third-party payment processors)</li>
                </ul>
              </div>

              <div class="bg-green-50 border border-green-200 rounded-lg p-6 my-4">
                <h3 class="font-semibold text-green-900 mb-3">2.2 Information Collected Automatically</h3>
                <ul class="list-disc list-inside space-y-2 text-green-800">
                  <li><strong>Usage Data:</strong> Pages viewed, features used, time spent on the Platform, search queries</li>
                  <li><strong>Device Information:</strong> IP address, browser type, operating system, device identifiers</li>
                  <li><strong>Location Data:</strong> Approximate location based on IP address (with your consent for precise location)</li>
                  <li><strong>Cookies and Similar Technologies:</strong> Data collected through cookies, web beacons, and similar tracking technologies</li>
                </ul>
              </div>

              <div class="bg-purple-50 border border-purple-200 rounded-lg p-6 my-4">
                <h3 class="font-semibold text-purple-900 mb-3">2.3 Information from Third Parties</h3>
                <ul class="list-disc list-inside space-y-2 text-purple-800">
                  <li><strong>Social Media:</strong> If you register using social media (Google, Facebook), we receive basic profile information</li>
                  <li><strong>Recruiters and Employers:</strong> Information shared when they interact with your profile or applications</li>
                  <li><strong>Background Checks:</strong> If authorized by you, we may receive information from background check providers</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Section 3 -->
          <div id="how-we-use" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">3. How We Use Your Information</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>We use the information we collect for the following purposes:</p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">3.1 To Provide and Improve Our Services</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Create and manage your account</li>
                <li>Enable job search, application, and tracking features</li>
                <li>Match you with relevant job opportunities</li>
                <li>Facilitate communication between job seekers and employers</li>
                <li>Process payments for premium services</li>
                <li>Improve and optimize Platform functionality and user experience</li>
              </ul>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">3.2 To Communicate With You</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Send job alerts and recommendations</li>
                <li>Notify you about application status updates</li>
                <li>Respond to your inquiries and provide customer support</li>
                <li>Send important service announcements and updates</li>
                <li>Send marketing communications (with your consent)</li>
              </ul>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">3.3 For Safety, Security, and Compliance</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Verify user identity and prevent fraud</li>
                <li>Detect and prevent security threats and abuse</li>
                <li>Enforce our Terms of Service and policies</li>
                <li>Comply with legal obligations and respond to lawful requests</li>
                <li>Protect our rights, property, and users</li>
              </ul>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">3.4 For Analytics and Research</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Analyze Platform usage and trends</li>
                <li>Conduct research and develop new features</li>
                <li>Generate anonymized, aggregate statistics</li>
              </ul>
            </div>
          </div>

          <!-- Section 4 -->
          <div id="information-sharing" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">4. Information Sharing and Disclosure</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p class="font-semibold">
                We do not sell your personal information. We only share your information in the following circumstances:
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">4.1 With Employers and Recruiters</h3>
              <p>
                When you apply for a job, we share your application materials (resume, cover letter, profile) with the relevant employer. You control what information is visible in your profile settings.
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">4.2 With Service Providers</h3>
              <p>
                We share information with third-party vendors who perform services on our behalf, including:
              </p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Cloud hosting and storage providers</li>
                <li>Payment processors</li>
                <li>Email and communication services</li>
                <li>Analytics providers</li>
                <li>Customer support tools</li>
              </ul>
              <p>These service providers are contractually obligated to protect your information and use it only for specified purposes.</p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">4.3 For Legal Reasons</h3>
              <p>We may disclose your information if required by law or in good faith belief that such action is necessary to:</p>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Comply with legal obligations, court orders, or government requests</li>
                <li>Enforce our Terms of Service or other agreements</li>
                <li>Protect the rights, property, or safety of HirePulse, our users, or the public</li>
                <li>Investigate fraud, security issues, or technical problems</li>
              </ul>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">4.4 Business Transfers</h3>
              <p>
                If HirePulse is involved in a merger, acquisition, or sale of assets, your information may be transferred to the acquiring entity. We will notify you of any such change and any choices you may have.
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">4.5 With Your Consent</h3>
              <p>
                We may share your information for other purposes with your explicit consent.
              </p>
            </div>
          </div>

          <!-- Section 5 -->
          <div id="data-security" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">5. Data Security</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                We take data security seriously and implement industry-standard technical and organizational measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction.
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">Our security measures include:</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li>Encryption of data in transit and at rest using SSL/TLS</li>
                <li>Secure authentication and password hashing</li>
                <li>Regular security audits and vulnerability assessments</li>
                <li>Access controls limiting employee access to personal data</li>
                <li>Secure backup and disaster recovery procedures</li>
                <li>Monitoring for suspicious activity and security incidents</li>
              </ul>

              <div class="bg-yellow-50 border border-yellow-300 rounded-lg p-6 mt-4">
                <p class="text-sm text-yellow-900">
                  <strong>Important:</strong> While we strive to protect your information, no method of transmission over the Internet or electronic storage is 100% secure. You are responsible for maintaining the confidentiality of your account credentials.
                </p>
              </div>
            </div>
          </div>

          <!-- Section 6 -->
          <div id="data-retention" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">6. Data Retention</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                We retain your personal information for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required or permitted by law.
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">Retention periods:</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li><strong>Active accounts:</strong> Information is retained while your account is active</li>
                <li><strong>Deleted accounts:</strong> Most data is deleted within 90 days, except where required for legal, security, or business purposes</li>
                <li><strong>Application records:</strong> Retained for up to 2 years after application submission</li>
                <li><strong>Communication records:</strong> Retained for up to 1 year</li>
                <li><strong>Legal compliance:</strong> Certain records may be retained longer to comply with legal obligations</li>
              </ul>
            </div>
          </div>

          <!-- Section 7 -->
          <div id="your-rights" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">7. Your Rights and Choices</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                You have the following rights regarding your personal information:
              </p>

              <div class="space-y-4 mt-4">
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Access and Portability</h4>
                  <p class="text-sm">You can access and download your personal data from your account settings.</p>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Correction</h4>
                  <p class="text-sm">You can update or correct your information through your profile settings.</p>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Deletion</h4>
                  <p class="text-sm">You can request deletion of your account and personal data through Settings > Privacy. Some information may be retained as required by law.</p>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Profile Visibility</h4>
                  <p class="text-sm">Control who can see your profile (public, recruiters only, or private) in Settings > Privacy.</p>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Marketing Communications</h4>
                  <p class="text-sm">Opt out of marketing emails by clicking "Unsubscribe" in any email or updating preferences in Settings > Notifications.</p>
                </div>

                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                  <h4 class="font-semibold text-gray-800 mb-2">Cookie Preferences</h4>
                  <p class="text-sm">Manage cookie settings through your browser or our cookie preference center.</p>
                </div>
              </div>

              <p class="mt-6">
                To exercise these rights or if you have questions, contact us at <a href="mailto:privacy@hirepulse.in" class="text-blue-600 hover:text-blue-700 underline">privacy@hirepulse.in</a>.
              </p>
            </div>
          </div>

          <!-- Section 8 -->
          <div id="cookies" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">8. Cookies and Tracking Technologies</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                We use cookies and similar tracking technologies to enhance your experience, analyze usage, and deliver personalized content.
              </p>

              <h3 class="font-semibold text-gray-800 mt-6 mb-3">Types of cookies we use:</h3>
              <ul class="list-disc list-inside space-y-2 ml-4">
                <li><strong>Essential cookies:</strong> Necessary for the Platform to function (e.g., authentication, security)</li>
                <li><strong>Performance cookies:</strong> Help us understand how you use the Platform and improve performance</li>
                <li><strong>Functional cookies:</strong> Remember your preferences and settings</li>
                <li><strong>Advertising cookies:</strong> Deliver relevant ads and measure campaign effectiveness (with your consent)</li>
              </ul>

              <p class="mt-4">
                You can control cookies through your browser settings. Note that disabling certain cookies may limit Platform functionality.
              </p>
            </div>
          </div>

          <!-- Section 9 -->
          <div id="third-party" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">9. Third-Party Links and Services</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                Our Platform may contain links to third-party websites, services, or applications. We are not responsible for the privacy practices of these third parties.
              </p>
              <p>
                We encourage you to read the privacy policies of any third-party services you interact with. This Privacy Policy applies only to information collected by HirePulse.
              </p>
            </div>
          </div>

          <!-- Section 10 -->
          <div id="children" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">10. Children's Privacy</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                HirePulse is not intended for individuals under the age of 18. We do not knowingly collect personal information from children.
              </p>
              <p>
                If we become aware that we have collected information from a child under 18, we will take steps to delete such information promptly. If you believe we have collected information from a child, please contact us immediately.
              </p>
            </div>
          </div>

          <!-- Section 11 -->
          <div id="international" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">11. International Data Transfers</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                Your information may be transferred to and processed in countries other than your country of residence. These countries may have different data protection laws.
              </p>
              <p>
                When we transfer your information internationally, we ensure appropriate safeguards are in place to protect your data in accordance with this Privacy Policy and applicable laws.
              </p>
            </div>
          </div>

          <!-- Section 12 -->
          <div id="changes" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">12. Changes to Privacy Policy</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                We may update this Privacy Policy from time to time to reflect changes in our practices, technology, legal requirements, or other factors.
              </p>
              <p>
                When we make material changes, we will notify you by email or through a prominent notice on the Platform. Your continued use of the Platform after the changes take effect constitutes your acceptance of the revised Privacy Policy.
              </p>
              <p>
                We encourage you to review this Privacy Policy periodically. The "Last Updated" date at the top indicates when this policy was last revised.
              </p>
            </div>
          </div>

          <!-- Section 13 -->
          <div id="contact" class="mb-10 scroll-mt-6">
            <h2 class="text-2xl font-bold text-gray-800 mb-4">13. Contact Us</h2>
            <div class="text-gray-700 leading-relaxed space-y-4">
              <p>
                If you have questions, concerns, or requests regarding this Privacy Policy or our data practices, please contact us:
              </p>

              <div class="bg-gray-50 border border-gray-200 rounded-lg p-6 mt-4">
                <p class="font-semibold text-gray-800 mb-4">HirePulse - Privacy Team</p>
                <div class="space-y-2">
                  <p><strong>Email:</strong> <a href="mailto:privacy@hirepulse.in" class="text-blue-600 hover:text-blue-700 underline">privacy@hirepulse.in</a></p>
                  <p><strong>General Support:</strong> <a href="mailto:support@hirepulse.in" class="text-blue-600 hover:text-blue-700 underline">support@hirepulse.in</a></p>
                  <p><strong>Phone:</strong> +91 1800-123-4567</p>
                  <p><strong>Address:</strong> Mumbai, Maharashtra, India</p>
                </div>
              </div>

              <p class="mt-6 text-sm">
                We will respond to your privacy-related inquiries within 30 days.
              </p>
            </div>
          </div>

          <!-- Acknowledgment -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
            <p class="text-sm text-blue-900 font-semibold mb-2">
              Your Consent
            </p>
            <p class="text-sm text-blue-800">
              By using HirePulse, you acknowledge that you have read and understood this Privacy Policy and consent to the collection, use, and disclosure of your information as described herein.
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
