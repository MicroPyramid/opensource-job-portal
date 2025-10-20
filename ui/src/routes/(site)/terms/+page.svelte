<script lang="ts">
	import { FileText, ChevronRight, AlertCircle } from '@lucide/svelte';

	const lastUpdated = 'October 19, 2025';

	interface TermsSection {
		id: string;
		title: string;
	}

	const sections: TermsSection[] = [
		{ id: 'introduction', title: 'Introduction' },
		{ id: 'employer-eligibility', title: 'Employer Eligibility' },
		{ id: 'subscription-terms', title: 'Subscription Terms' },
		{ id: 'employer-conduct', title: 'Employer Conduct' },
		{ id: 'prohibited-employer', title: 'Prohibited Employer Conduct' },
		{ id: 'user-conduct', title: 'User Conduct' },
		{ id: 'registration', title: 'Registration and Password' },
		{ id: 'profile', title: 'Profile Management' },
		{ id: 'prohibited-users', title: 'Prohibited User Conduct' },
		{ id: 'rights', title: 'Reservation of Rights' },
		{ id: 'revisions', title: 'Revisions' }
	];

	function scrollToSection(id: string): void {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	}
</script>

<svelte:head>
	<title>Terms & Conditions - PeelJobs</title>
	<meta
		name="description"
		content="Terms of Service and User Agreement for PeelJobs - Bound to terms and conditions to get all the facilities of PeelJobs for your needs."
	/>
	<link rel="canonical" href="https://peeljobs.com/terms" />
</svelte:head>

<!-- Hero Section -->
<div class="bg-blue-600 text-white py-12 md:py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="max-w-4xl mx-auto text-center">
			<div class="flex justify-center mb-4 md:mb-6">
				<div class="p-3 md:p-4 bg-white/10 rounded-full">
					<FileText class="w-8 h-8 md:w-10 md:h-10" />
				</div>
			</div>
			<h1 class="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 md:mb-4">Terms & Conditions</h1>
			<p class="text-lg md:text-xl text-blue-100">User Agreement and Acceptable Use Policy</p>
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
					<span class="text-gray-900 font-medium">Terms & Conditions</span>
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

			<!-- Terms Content -->
			<div class="lg:col-span-3">
				<div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 md:p-8 lg:p-12">
					<!-- Introduction -->
					<div id="introduction" class="mb-10 scroll-mt-6">
						<div
							class="bg-yellow-50 border-l-4 border-yellow-400 p-4 md:p-6 mb-6 md:mb-8 rounded-r-lg"
						>
							<div class="flex items-start gap-3">
								<AlertCircle class="w-5 h-5 md:w-6 md:h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
								<div class="text-sm md:text-base text-gray-700 leading-relaxed">
									<p class="font-semibold text-gray-900 mb-2">Important Notice</p>
									<p class="mb-3 md:mb-4">
										This Terms of Use & Subscriber Agreement is a legally binding agreement between
										Peeljobs.com, Employer (including employers, recruiting firms, staffing agencies, and
										recruiters) and Job Candidate/User of this website, including all information,
										products, services, software, databases, and website available from Peeljobs.com.
									</p>
									<p>
										By accessing information on Peeljobs.com, User acknowledges that he/she has read,
										understood and agrees to comply with the terms of this Agreement. By using
										Peeljobs.com as a Job Candidate, Employer, and/or submitting any content, User
										agrees to be bound by and comply with this Agreement. You understand and agree that
										Peeljobs.com is provided to you on an <span class="font-semibold">AS IS</span> and
										<span class="font-semibold">AS AVAILABLE</span> basis. Peeljobs.com reserves the right
										to modify, suspend or discontinue the System with or without notice at any time and without
										any liability to you.
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- EMPLOYER TERMS -->
					<div class="mb-12">
						<div class="bg-blue-50 border-l-4 border-blue-600 p-4 mb-6 rounded-r-lg">
							<h2 class="text-xl md:text-2xl font-bold text-gray-900">
								Terms Applicable to Employers
							</h2>
						</div>

						<!-- Eligible Subscribers -->
						<div id="employer-eligibility" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Eligible Subscribers of Peeljobs.com
							</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								Peeljobs.com reserves the right to determine, in its sole discretion, whether a firm
								meets the eligibility requirements for subscriptions. Peeljobs.com asks for company's
								social pages information to display your job posting on your social pages which we
								think is amazing as it maximizes the reach of your jobs post.
							</p>
						</div>

						<!-- Subscription Terms -->
						<div id="subscription-terms" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Subscription Terms
							</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								All subscription offers are made to eligible, qualified, Employers. As the expiration
								date of an Employer's subscription term approaches, the Employer may be invoiced for a
								new subscription term. If the invoice is paid, the subscription and its associated
								benefits will continue; otherwise, the subscription will become inactive on its
								expiration date. When a subscription becomes inactive, all features, services, and
								benefits of the subscription cease. These may include but are not limited to: jobs
								entered in the System, distribution of jobs, web pages maintained by the System,
								resume-forwarding services.
							</p>
						</div>

						<!-- Employer Conduct -->
						<div id="employer-conduct" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Employer Conduct
							</h3>
							<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
								<p>
									Employer agrees that all the information accessed by Employer will be used only to
									allow the Employer to use the services offered by Peeljobs.com. Employers seeking to
									fill open, verifiable job positions on behalf of their client or vendor companies may
									use the System only for lawful purposes.
								</p>
								<p>
									Employers shall upload in the System only genuine, verifiable employment
									advertisements from Employer's company or from verifiable companies with which
									Employer has a direct, explicit, agency relationship. Each Employer shall be
									responsible for the accuracy, timeliness, and completeness of any employment
									advertisements or candidate profiles its users place in the System.
								</p>
								<p>
									Employer represents, warrants and covenants that any information or materials
									uploaded to the System by Employer for use in connection with the System will not
									violate any laws or regulations or third-party proprietary rights, including, without
									limitation, copyright, trademark, obscenity, rights of publicity or privacy, and
									defamation laws. Employer hereby grants Peeljobs.com a non-exclusive, worldwide,
									royalty-free license to use these materials and to hyperlink to Employer's website.
								</p>
							</div>
						</div>

						<!-- Prohibited Employer Conduct -->
						<div id="prohibited-employer" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Specific Prohibited Conduct of Employers
							</h3>
							<p class="text-sm md:text-base text-gray-700 mb-4">
								Prohibited Uses of the System include:
							</p>

							<div class="space-y-4">
								<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
									<h4 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">
										Password Sharing
									</h4>
									<p class="text-xs md:text-sm text-gray-700 leading-relaxed">
										Use of the System is limited to registered and authorized account holders.
										Employers can modify the profile and change the authorized person anytime during the
										valid subscription period. The sharing of passwords or login information is
										forbidden. Violation of this prohibition will result in an immediate cancellation,
										without refund, of any remaining portion of the subscription amount.
									</p>
								</div>

								<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
									<h4 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">
										Commercial Use of System
									</h4>
									<p class="text-xs md:text-sm text-gray-700 leading-relaxed">
										The reselling of any part of the System or the services or benefits provided by the
										System is expressly forbidden. All usage of the System must be contracted directly
										via Peeljobs.com or one of our authorized affiliates. Reselling of the Peeljobs.com
										System or any of its components without prior, written permission from Peeljobs will
										result in an immediate cancellation, without refund, of any remaining portion of the
										subscription amount.
									</p>
								</div>

								<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
									<h4 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">
										Automatic Searching & Robots
									</h4>
									<p class="text-xs md:text-sm text-gray-700 leading-relaxed">
										An Employer shall not use or attempt to use any engine, software, tool, agent, or
										other device or mechanism (including browsers, spiders, robots, avatars, or
										intelligent agents) to navigate or search the System.
									</p>
								</div>

								<div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
									<h4 class="font-semibold text-gray-900 mb-2 text-sm md:text-base">
										Multiple or Duplicate Postings
									</h4>
									<p class="text-xs md:text-sm text-gray-700 leading-relaxed">
										An Employer shall not post duplicate positions, multiple positions within one
										advertisement, or copy (plagiarize) other employment advertisements or candidate
										profiles.
									</p>
								</div>
							</div>
						</div>
					</div>

					<!-- ALL USERS TERMS -->
					<div class="mb-12">
						<div class="bg-green-50 border-l-4 border-green-600 p-4 mb-6 rounded-r-lg">
							<h2 class="text-xl md:text-2xl font-bold text-gray-900">
								Terms Applicable to All Users
							</h2>
						</div>

						<!-- User Conduct -->
						<div id="user-conduct" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								User Conduct
							</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								You must be 18 years of age or older to visit or use Peeljobs.com in any manner. By
								visiting Peeljobs.com or accepting these Terms of Use, You represent and warrant to the
								Company that You are 18 years of age or older, and that You have the right, authority
								and capacity to use the Web Site and agree to and abide by these Terms of Use. You also
								represent and warrant to the Company that You will use Peeljobs.com in a manner
								consistent with any and all applicable laws and regulations.
							</p>
						</div>

						<!-- Registration and Password -->
						<div id="registration" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Registration and Password
							</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								You are responsible for maintaining the confidentiality of your account access
								information and passwords. You shall be responsible for all uses of your Web Site
								registrations and passwords, whether or not authorized by You. You are not authorized to
								share your password or other account access information with any other party, temporarily
								or permanently, and breach of this obligation may tantamount to disabling the
								Peeljobs.com account and Peeljobs Services. You agree to immediately notify the Company
								of any unauthorized use of your Account, and passwords. You will receive job posting
								mail and other promotional mails to your inbox when you register with Peeljobs.com.
							</p>
						</div>

						<!-- Profile -->
						<div id="profile" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Profile Management
							</h3>
							<div class="space-y-4 text-sm md:text-base text-gray-700 leading-relaxed">
								<p>
									Any Profile/Resume You submit must be accurate and describe You, an individual person.
									The Profile requires standard fields to be completed.
								</p>
								<p>
									You acknowledge and agree that You are solely responsible for the form, content and
									accuracy of any resume or material contained therein placed by You on the Peeljobs.com.
								</p>
								<p>
									Peeljobs.com reserves the right to offer third party services and products to You
									based on the preferences that You identify in Your registration and at any time
									thereafter or you have agreed to receive, such offers may be made by Peeljobs.com or
									by third parties.
								</p>
								<p>
									You understand and acknowledge that You have no ownership rights in Your account and
									that if You cancel/terminate Your Peeljobs account, all Your account information from
									Peeljobs.com, including resumes, Profiles, cover letters, saved jobs, questionnaires
									will be marked as deleted in and may be deleted from our databases. Information may
									continue to be available for some period of time because of delays in propagating such
									deletion through Peeljobs's web servers. In addition, third parties may retain saved
									copies of Your Information.
								</p>
								<p>
									Peeljobs.com reserves the right to delete Your account and all of Your Information
									after a significant duration of inactivity.
								</p>
							</div>
						</div>

						<!-- Prohibited User Conduct -->
						<div id="prohibited-users" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Specific Prohibited Conduct of Users
							</h3>
							<p class="text-sm md:text-base text-gray-700 mb-4">
								Prohibited Uses of the System include:
							</p>
							<ul class="space-y-2 text-xs md:text-sm text-gray-700 list-disc list-inside ml-2 md:ml-4">
								<li>Post any resume or apply for any job on behalf of another party</li>
								<li>Set more than one copy of the same resume to public at any one time</li>
								<li>
									Post or submit to Peeljobs.com any incomplete, false or inaccurate biographical
									information or information which is not your own
								</li>
								<li>Delete or revise any material posted by any other person or entity</li>
								<li>
									Take any action that imposes an unreasonable or disproportionately large load on
									peeljobs Site's infrastructure
								</li>
								<li>
									Use the Peeljobs Services for any unlawful purpose or any illegal activity, or post
									or submit any content, resume that is defamatory, libelous, implicitly or explicitly
									offensive, vulgar, obscene, threatening, abusive, hateful, racist, discriminatory, of
									a menacing character or likely to cause annoyance, inconvenience, embarrassment,
									anxiety or could cause harassment to any person or include any links to pornographic,
									indecent or sexually explicit material of any kind
								</li>
							</ul>
						</div>

						<!-- Reservation of Rights -->
						<div id="rights" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">
								Reservation of Rights
							</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								Any rights not expressly granted herein are reserved.
							</p>
						</div>

						<!-- Revisions -->
						<div id="revisions" class="mb-8 md:mb-10 scroll-mt-6">
							<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3 md:mb-4">Revisions</h3>
							<p class="text-sm md:text-base text-gray-700 leading-relaxed">
								Peeljobs.com may revise these Terms at any time by posting an updated version to
								http://www.peeljobs.com. You should visit this page periodically to review the most
								current Agreement because it is binding on Users.
							</p>
						</div>
					</div>

					<!-- Contact -->
					<div class="bg-blue-50 border border-blue-200 rounded-lg p-6">
						<h3 class="text-lg font-semibold text-blue-900 mb-3">Questions?</h3>
						<p class="text-sm text-blue-800 mb-4">
							For any questions, or legal concerns, please email Support at Peeljobs.com
						</p>
						<a
							href="/contact/"
							class="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg text-sm font-semibold transition-colors duration-200"
						>
							Contact Support
						</a>
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
