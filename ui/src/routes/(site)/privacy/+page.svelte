<script lang="ts">
	import { Shield, ChevronRight, Lock, Eye, Database, UserCheck, AlertTriangle } from '@lucide/svelte';

	const lastUpdated = 'October 19, 2025';

	const sections = [
		{ id: 'introduction', title: '1. Introduction' },
		{ id: 'cookies', title: '2. Cookies and Tracking' },
		{ id: 'third-party', title: '3. Third Party Services' },
		{ id: 'consent', title: '4. Your Consent' },
		{ id: 'security', title: '5. Information Security' },
		{ id: 'updating', title: '6. Updating Information' },
		{ id: 'children', title: '7. Children' },
		{ id: 'sharing', title: '8. Information Sharing' },
		{ id: 'confidentiality', title: '9. Confidentiality and Security' },
		{ id: 'changes', title: '10. Policy Changes' },
		{ id: 'disclaimer', title: '11. Disclaimer' },
		{ id: 'contact', title: '12. Contact Information' }
	];

	function scrollToSection(id: string): void {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	}
</script>

<svelte:head>
	<title>Privacy Policy - PeelJobs</title>
	<meta
		name="description"
		content="Peeljobs privacy policy - We set our efforts to secure all your confidential information, third party details and more. Read our commitment to protecting your privacy."
	/>
	<link rel="canonical" href="https://peeljobs.com/privacy" />
</svelte:head>

<!-- Hero Section -->
<div class="bg-blue-600 text-white py-12 md:py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-4xl mx-auto text-center">
			<div class="flex justify-center mb-4 md:mb-6">
				<div class="p-3 md:p-4 bg-white/10 rounded-full">
					<Shield class="w-8 h-8 md:w-10 md:h-10" />
				</div>
			</div>
			<h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">Privacy Policy</h1>
			<p class="text-lg md:text-xl text-blue-100">
				Your privacy is important to us. Learn how we collect, use, and protect your personal
				information.
			</p>
			<p class="text-xs md:text-sm text-blue-200 mt-3 md:mt-4">Last Updated: {lastUpdated}</p>
		</div>
	</div>
</div>

<!-- Main Content -->
<div class="bg-gray-50 py-12 md:py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Breadcrumb -->
		<nav class="mb-6 md:mb-8" aria-label="Breadcrumb">
			<ol class="flex items-center space-x-2 text-sm text-gray-600">
				<li>
					<a href="/" class="hover:text-blue-600 transition-colors duration-200"> Home </a>
				</li>
				<li class="flex items-center">
					<ChevronRight class="w-4 h-4 mx-1 md:mx-2 text-gray-400" />
					<span class="text-gray-900 font-medium">Privacy Policy</span>
				</li>
			</ol>
		</nav>

		<div class="grid lg:grid-cols-4 gap-6 md:gap-8">
			<!-- Table of Contents (Sticky Sidebar) - Hidden on mobile -->
			<div class="lg:col-span-1 hidden lg:block">
				<div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 sticky top-6">
					<h2 class="text-lg font-bold text-gray-800 mb-4">Table of Contents</h2>
					<nav class="space-y-2">
						{#each sections as section}
							<button
								onclick={() => scrollToSection(section.id)}
								class="w-full text-left text-sm text-gray-600 hover:text-blue-600 hover:bg-blue-50 px-3 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
							>
								<ChevronRight class="w-3 h-3 flex-shrink-0" />
								<span class="flex-1">{section.title}</span>
							</button>
						{/each}
					</nav>
				</div>
			</div>

			<!-- Privacy Policy Content -->
			<div class="lg:col-span-3">
				<div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 md:p-8 lg:p-12">
					<!-- Introduction -->
					<div id="introduction" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							1. Introduction
						</h2>
						<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
							<p>
								At PeelJobs, we are committed to respecting your online privacy and recognize your need
								for appropriate protection and management of any personally identifiable information
								("Personal Information") you share with us.
							</p>
							<p>
								"Personal Information" means any information that may be used to identify an individual,
								including, but not limited to, a first and last name, a home or other physical address
								and an email address or other contact information, whether at work or at home. In
								general, you can visit PeelJobs without telling us who you are or revealing any Personal
								Information about yourself.
							</p>
						</div>
					</div>

					<!-- Cookies Section -->
					<div id="cookies" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							2. Cookies and Tracking Technologies
						</h2>
						<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
							<div class="bg-purple-50 border border-purple-200 rounded-lg p-4 md:p-6">
								<div class="flex items-start gap-3">
									<Database class="w-5 h-5 md:w-6 md:h-6 text-purple-600 flex-shrink-0 mt-0.5" />
									<div>
										<p class="mb-3 md:mb-4">
											Some of our web pages utilize "cookies" and other tracking technologies. A
											"cookie" is a small text file that may be used, for example, to collect
											information about website activity. Some cookies and other technologies may serve
											to recall Personal Information previously indicated by a web user.
										</p>
										<p class="mb-3 md:mb-4">
											Most browsers allow you to control cookies, including whether or not to accept
											them and how to remove them. You may set most browsers to notify you if you
											receive a cookie, or you may choose to block cookies with your browser, but please
											note that if you choose to erase or block your cookies, you will need to re-enter
											your original user ID and password to gain access to certain parts of the website.
										</p>
										<p>
											Tracking technologies may record information such as Internet domain and host
											names; Internet protocol (IP) addresses; browser software and operating system
											types; clickstream patterns; and dates and times that our site is accessed. Our
											use of cookies and other tracking technologies allows us to improve our website
											and your web experience.
										</p>
									</div>
								</div>
							</div>
						</div>
					</div>

					<!-- Third Party Services -->
					<div id="third-party" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							3. Third Party Services
						</h2>
						<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
							<p>
								Third parties provide certain services available on PeelJobs. We may provide
								information, including Personal Information, that we collect to third-party service
								providers to help us deliver programs, products, information, and services. Service
								providers are also an important means by which we maintain our website and mailing
								lists.
							</p>
							<p>
								We will take reasonable steps to ensure that these third-party service providers are
								obligated to protect Personal Information on our behalf. We do not intend to transfer
								Personal Information without your consent to third parties who are not bound to act on
								our behalf unless such transfer is legally required.
							</p>
						</div>
					</div>

					<!-- Your Consent -->
					<div id="consent" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							4. Your Consent
						</h2>
						<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 md:p-6">
							<div class="flex items-start gap-3">
								<UserCheck class="w-5 h-5 md:w-6 md:h-6 text-blue-600 flex-shrink-0 mt-0.5" />
								<p class="text-sm md:text-base text-gray-700 leading-relaxed">
									By using this website, you consent to the terms of our Privacy Policy and to our
									processing of Personal Information for the purposes given above as well as those
									explained where we collect Personal Information on the web.
								</p>
							</div>
						</div>
					</div>

					<!-- Information Security -->
					<div id="security" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							5. Information Security
						</h2>
						<div class="space-y-4">
							<div class="bg-green-50 border border-green-200 rounded-lg p-4 md:p-6">
								<div class="flex items-start gap-3">
									<Lock class="w-5 h-5 md:w-6 md:h-6 text-green-600 flex-shrink-0 mt-0.5" />
									<ul class="space-y-3 text-sm md:text-base text-gray-700">
										<li class="flex items-start">
											<span class="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
											We take appropriate security measures to protect against unauthorized access to or
											unauthorized alteration, disclosure or destruction of data.
										</li>
										<li class="flex items-start">
											<span class="w-2 h-2 bg-green-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
											We restrict access to your personally identifying information to employees who need
											to know that information in order to operate, develop or improve our services.
										</li>
									</ul>
								</div>
							</div>
						</div>
					</div>

					<!-- Updating Information -->
					<div id="updating" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							6. Updating Your Information
						</h2>
						<ul class="space-y-3 text-sm md:text-base text-gray-700">
							<li class="flex items-start">
								<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
								We provide mechanisms for updating and correcting your personally identifying
								information for many of our services. For more information, please see the help
								documentation for each service.
							</li>
						</ul>
					</div>

					<!-- Children -->
					<div id="children" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">7. Children</h2>
						<ul class="space-y-3 text-sm md:text-base text-gray-700">
							<li class="flex items-start">
								<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
								PeelJobs will not contact children under age 13 about special offers or for marketing
								purposes without a parent's permission.
							</li>
						</ul>
					</div>

					<!-- Information Sharing -->
					<div id="sharing" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							8. Information Sharing and Disclosure
						</h2>
						<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
							<div class="bg-blue-50 border border-blue-200 rounded-lg p-4 md:p-6 mb-4 md:mb-6">
								<p class="mb-4 font-semibold text-blue-900">
									PeelJobs does not rent, sell, or share personal information about you with other
									people (save with your consent) or non-affiliated companies except to provide products
									or services you've requested, when we have your permission, or under the following
									circumstances:
								</p>
								<ol class="space-y-3 text-blue-800 list-decimal list-inside ml-2 md:ml-4">
									<li>
										We provide the information to trusted partners who work on behalf of or with
										PeelJobs under confidentiality agreements.
									</li>
									<li>
										We respond to subpoenas, court orders, or legal process, or to establish or
										exercise our legal rights or defend against legal claims.
									</li>
									<li>
										We believe it is necessary to share information in order to investigate, prevent, or
										take action regarding illegal activities, suspected fraud, or violations of our terms
										of use.
									</li>
									<li>
										We transfer information about you if PeelJobs is acquired by or merged with another
										company.
									</li>
								</ol>
							</div>
							<ul class="space-y-3 text-gray-700">
								<li class="flex items-start">
									<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
									PeelJobs does not provide any personal information to advertisers when you interact
									with or view a targeted ad.
								</li>
								<li class="flex items-start">
									<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
									Our advertisers include financial service providers and non-financial companies.
								</li>
							</ul>
						</div>
					</div>

					<!-- Confidentiality -->
					<div id="confidentiality" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							9. Confidentiality and Security
						</h2>
						<ul class="space-y-3 text-sm md:text-base text-gray-700">
							<li class="flex items-start">
								<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
								We limit access to personal information about you to employees who we believe reasonably
								need to come into contact with that information.
							</li>
							<li class="flex items-start">
								<span class="w-2 h-2 bg-blue-600 rounded-full mt-2 mr-3 flex-shrink-0"></span>
								We have physical, electronic, and procedural safeguards that comply with Indian laws to
								protect personal information about you.
							</li>
						</ul>
					</div>

					<!-- Policy Changes -->
					<div id="changes" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							10. Changes to This Privacy Policy
						</h2>
						<div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4 md:p-6">
							<div class="flex items-start gap-3">
								<AlertTriangle class="w-5 h-5 md:w-6 md:h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
								<p class="text-sm md:text-base text-gray-700 leading-relaxed">
									PeelJobs reserves the right to update, change or modify this policy at any time. The
									policy shall come into effect from the date of such update, change or modification.
								</p>
							</div>
						</div>
					</div>

					<!-- Disclaimer -->
					<div id="disclaimer" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							11. Disclaimer
						</h2>
						<div class="bg-red-50 border border-red-200 rounded-lg p-4 md:p-6">
							<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
								<p>
									PeelJobs does not store or keep credit card data in a location that is accessible via
									the Internet. Once a credit card transaction has been completed, all credit card data
									is moved offline to ensure maximum security.
								</p>
								<p class="font-semibold text-red-900">
									PeelJobs shall not be liable for any loss or damage sustained by reason of any
									disclosure of any information concerning the user's account and/or information
									relating to online transactions using credit cards/debit cards.
								</p>
							</div>
						</div>
					</div>

					<!-- Contact Information -->
					<div id="contact" class="mb-10 scroll-mt-6">
						<h2 class="text-2xl md:text-3xl font-bold text-gray-800 mb-4 md:mb-6">
							12. Contact Information
						</h2>
						<div class="bg-gray-50 border border-gray-200 rounded-lg p-4 md:p-6">
							<p class="text-sm md:text-base text-gray-700 leading-relaxed mb-4">
								PeelJobs welcomes your comments regarding this privacy statement. Should there be any
								concerns about contravention of this Privacy Policy, we will employ all commercially
								reasonable efforts to address the same.
							</p>
							<div class="flex items-center gap-2 mb-4">
								<Eye class="w-5 h-5 text-gray-600" />
								<p class="text-sm md:text-base text-gray-600 font-medium">
									You can reach us at:
									<a
										href="/contact/"
										class="text-blue-600 hover:text-blue-700 underline ml-1">Contact Page</a
									>
								</p>
							</div>
							<p class="text-xs md:text-sm text-gray-600">
								<strong>Note:</strong> The terms in this agreement may be changed by PeelJobs at any time.
								PeelJobs is free to offer its services to any client/prospective client without restriction.
							</p>
						</div>
					</div>

					<!-- Acknowledgment -->
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
						<p class="text-sm md:text-base text-blue-900 font-semibold mb-2">Your Consent</p>
						<p class="text-sm md:text-base text-blue-800">
							By using PeelJobs, you acknowledge that you have read and understood this Privacy Policy
							and consent to the collection, use, and disclosure of your information as described
							herein.
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>

<style>
	.scroll-mt-6 {
		scroll-margin-top: 1.5rem;
	}
</style>
