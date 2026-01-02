<script lang="ts">
	import { FileText, ChevronRight, AlertCircle, Building2, Users, Shield, Key, UserCircle, Ban, Scale, RefreshCw, ArrowRight, MessageCircle } from '@lucide/svelte';

	const lastUpdated = 'October 19, 2025';

	interface Section {
		id: string;
		title: string;
		icon: typeof FileText;
	}

	const sections: Section[] = [
		{ id: 'introduction', title: 'Introduction', icon: FileText },
		{ id: 'employer-eligibility', title: 'Employer Eligibility', icon: Building2 },
		{ id: 'subscription-terms', title: 'Subscription Terms', icon: Scale },
		{ id: 'employer-conduct', title: 'Employer Conduct', icon: Building2 },
		{ id: 'prohibited-employer', title: 'Prohibited Employer Conduct', icon: Ban },
		{ id: 'user-conduct', title: 'User Conduct', icon: Users },
		{ id: 'registration', title: 'Registration & Password', icon: Key },
		{ id: 'profile', title: 'Profile Management', icon: UserCircle },
		{ id: 'prohibited-users', title: 'Prohibited User Conduct', icon: Ban },
		{ id: 'rights', title: 'Reservation of Rights', icon: Shield },
		{ id: 'revisions', title: 'Revisions', icon: RefreshCw }
	];

	function scrollToSection(id: string): void {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	}
</script>

<svelte:head>
	<title>Terms & Conditions - PeelJobs | User Agreement and Acceptable Use Policy</title>
	<meta
		name="description"
		content="Read PeelJobs' Terms of Service, user agreement, and acceptable use policy. Understand your rights and responsibilities when using our free job portal platform for job seekers and employers."
	/>
	<link rel="canonical" href="https://peeljobs.com/terms/" />

	<!-- Open Graph -->
	<meta property="og:title" content="Terms & Conditions - PeelJobs" />
	<meta property="og:description" content="User agreement and terms of service for using PeelJobs platform." />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://peeljobs.com/terms/" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Terms & Conditions - PeelJobs" />
	<meta name="twitter:description" content="Our terms of service and user agreement." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-[#1D2226] text-white py-16 lg:py-20 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-primary/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<!-- Breadcrumb -->
		<nav class="mb-8" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2 text-sm text-muted">
				<li>
					<a href="/" class="hover:text-white transition-colors">Home</a>
				</li>
				<li class="flex items-center gap-2">
					<ChevronRight size={14} />
					<span class="text-white font-medium">Terms & Conditions</span>
				</li>
			</ol>
		</nav>

		<div class="max-w-4xl mx-auto text-center">
			<div class="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-8 animate-fade-in-up" style="opacity: 0;">
				<FileText size={40} class="text-primary" />
			</div>
			<h1 class="text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight mb-6 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
				Terms & Conditions
			</h1>
			<p class="text-lg md:text-xl text-gray-300 mb-4 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms;">
				User Agreement and Acceptable Use Policy
			</p>
			<p class="text-sm text-muted animate-fade-in-up" style="opacity: 0; animation-delay: 300ms;">Last Updated: {lastUpdated}</p>
		</div>
	</div>
</section>

<!-- Important Notice -->
<section class="py-12 lg:py-16 bg-surface">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="max-w-4xl mx-auto">
			<div class="bg-warning-light rounded-lg p-6 lg:p-8 border border-warning/20">
				<div class="flex items-start gap-4">
					<div class="w-12 h-12 bg-warning-light rounded-xl flex items-center justify-center flex-shrink-0">
						<AlertCircle size={24} class="text-warning" />
					</div>
					<div>
						<h2 class="text-xl font-semibold text-black mb-3">Important Notice</h2>
						<div class="space-y-4 text-muted leading-relaxed">
							<p>
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
		</div>
	</div>
</section>

<!-- Main Content -->
<section class="py-12 lg:py-20 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="grid lg:grid-cols-4 gap-8 max-w-7xl mx-auto">
			<!-- Sticky Sidebar -->
			<div class="lg:col-span-1 hidden lg:block">
				<div class="bg-surface rounded-lg p-6 border border-border sticky top-6">
					<h2 class="text-lg font-semibold text-black mb-5">Table of Contents</h2>
					<nav class="space-y-1">
						{#each sections as section}
							<button
								onclick={() => scrollToSection(section.id)}
								class="w-full text-left text-sm text-muted hover:text-primary hover:bg-primary/10 px-3 py-2.5 rounded-xl transition-colors flex items-center gap-3"
							>
								<svelte:component this={section.icon} size={14} class="text-muted" />
								<span>{section.title}</span>
							</button>
						{/each}
					</nav>
				</div>
			</div>

			<!-- Terms Content -->
			<div class="lg:col-span-3">
				<div class="bg-white rounded-lg shadow-sm border border-border p-6 lg:p-10">

					<!-- EMPLOYER TERMS HEADER -->
					<div class="bg-primary/10 rounded-lg p-6 border border-primary/20 mb-10">
						<div class="flex items-center gap-3">
							<div class="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-sm">
								<Building2 size={20} class="text-white" />
							</div>
							<h2 class="text-xl lg:text-2xl font-semibold text-black">Terms Applicable to Employers</h2>
						</div>
					</div>

					<!-- Employer Eligibility -->
					<article id="employer-eligibility" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Building2 size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Eligible Subscribers of PeelJobs</h2>
						</div>
						<p class="text-muted leading-relaxed">
							PeelJobs reserves the right to determine, in its sole discretion, whether a firm
							meets the eligibility requirements for subscriptions. PeelJobs asks for company's
							social pages information to display your job posting on your social pages which we
							think is amazing as it maximizes the reach of your jobs post.
						</p>
					</article>

					<!-- Subscription Terms -->
					<article id="subscription-terms" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Scale size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Subscription Terms</h2>
						</div>
						<p class="text-muted leading-relaxed">
							All subscription offers are made to eligible, qualified, Employers. As the expiration
							date of an Employer's subscription term approaches, the Employer may be invoiced for a
							new subscription term. If the invoice is paid, the subscription and its associated
							benefits will continue; otherwise, the subscription will become inactive on its
							expiration date. When a subscription becomes inactive, all features, services, and
							benefits of the subscription cease. These may include but are not limited to: jobs
							entered in the System, distribution of jobs, web pages maintained by the System,
							resume-forwarding services.
						</p>
					</article>

					<!-- Employer Conduct -->
					<article id="employer-conduct" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Building2 size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Employer Conduct</h2>
						</div>
						<div class="space-y-4 text-muted leading-relaxed">
							<p>
								Employer agrees that all the information accessed by Employer will be used only to
								allow the Employer to use the services offered by PeelJobs. Employers seeking to
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
								defamation laws. Employer hereby grants PeelJobs a non-exclusive, worldwide,
								royalty-free license to use these materials and to hyperlink to Employer's website.
							</p>
						</div>
					</article>

					<!-- Prohibited Employer Conduct -->
					<article id="prohibited-employer" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-error-light rounded-xl flex items-center justify-center">
								<Ban size={24} class="text-error" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Specific Prohibited Conduct of Employers</h2>
						</div>
						<p class="text-muted mb-6">Prohibited Uses of the System include:</p>

						<div class="space-y-4">
							<div class="bg-surface rounded-lg p-5 border border-border">
								<h4 class="font-semibold text-black mb-2 flex items-center gap-2">
									<Key size={16} class="text-error" />
									Password Sharing
								</h4>
								<p class="text-sm text-muted leading-relaxed">
									Use of the System is limited to registered and authorized account holders.
									Employers can modify the profile and change the authorized person anytime during the
									valid subscription period. The sharing of passwords or login information is
									forbidden. Violation of this prohibition will result in an immediate cancellation,
									without refund, of any remaining portion of the subscription amount.
								</p>
							</div>

							<div class="bg-surface rounded-lg p-5 border border-border">
								<h4 class="font-semibold text-black mb-2 flex items-center gap-2">
									<Scale size={16} class="text-error" />
									Commercial Use of System
								</h4>
								<p class="text-sm text-muted leading-relaxed">
									The reselling of any part of the System or the services or benefits provided by the
									System is expressly forbidden. All usage of the System must be contracted directly
									via PeelJobs or one of our authorized affiliates. Reselling of the PeelJobs
									System or any of its components without prior, written permission from PeelJobs will
									result in an immediate cancellation, without refund, of any remaining portion of the
									subscription amount.
								</p>
							</div>

							<div class="bg-surface rounded-lg p-5 border border-border">
								<h4 class="font-semibold text-black mb-2 flex items-center gap-2">
									<Shield size={16} class="text-error" />
									Automatic Searching & Robots
								</h4>
								<p class="text-sm text-muted leading-relaxed">
									An Employer shall not use or attempt to use any engine, software, tool, agent, or
									other device or mechanism (including browsers, spiders, robots, avatars, or
									intelligent agents) to navigate or search the System.
								</p>
							</div>

							<div class="bg-surface rounded-lg p-5 border border-border">
								<h4 class="font-semibold text-black mb-2 flex items-center gap-2">
									<Ban size={16} class="text-error" />
									Multiple or Duplicate Postings
								</h4>
								<p class="text-sm text-muted leading-relaxed">
									An Employer shall not post duplicate positions, multiple positions within one
									advertisement, or copy (plagiarize) other employment advertisements or candidate
									profiles.
								</p>
							</div>
						</div>
					</article>

					<!-- ALL USERS TERMS HEADER -->
					<div class="bg-success-light rounded-lg p-6 border border-success/20 mb-10 mt-16">
						<div class="flex items-center gap-3">
							<div class="w-10 h-10 bg-success rounded-xl flex items-center justify-center shadow-sm">
								<Users size={20} class="text-white" />
							</div>
							<h2 class="text-xl lg:text-2xl font-semibold text-black">Terms Applicable to All Users</h2>
						</div>
					</div>

					<!-- User Conduct -->
					<article id="user-conduct" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Users size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">User Conduct</h2>
						</div>
						<p class="text-muted leading-relaxed">
							You must be 18 years of age or older to visit or use PeelJobs in any manner. By
							visiting PeelJobs or accepting these Terms of Use, You represent and warrant to the
							Company that You are 18 years of age or older, and that You have the right, authority
							and capacity to use the Web Site and agree to and abide by these Terms of Use. You also
							represent and warrant to the Company that You will use PeelJobs in a manner
							consistent with any and all applicable laws and regulations.
						</p>
					</article>

					<!-- Registration and Password -->
					<article id="registration" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Key size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Registration and Password</h2>
						</div>
						<p class="text-muted leading-relaxed">
							You are responsible for maintaining the confidentiality of your account access
							information and passwords. You shall be responsible for all uses of your Web Site
							registrations and passwords, whether or not authorized by You. You are not authorized to
							share your password or other account access information with any other party, temporarily
							or permanently, and breach of this obligation may tantamount to disabling the
							PeelJobs account and PeelJobs Services. You agree to immediately notify the Company
							of any unauthorized use of your Account, and passwords. You will receive job posting
							mail and other promotional mails to your inbox when you register with PeelJobs.
						</p>
					</article>

					<!-- Profile -->
					<article id="profile" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<UserCircle size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Profile Management</h2>
						</div>
						<div class="space-y-4 text-muted leading-relaxed">
							<p>
								Any Profile/Resume You submit must be accurate and describe You, an individual person.
								The Profile requires standard fields to be completed.
							</p>
							<p>
								You acknowledge and agree that You are solely responsible for the form, content and
								accuracy of any resume or material contained therein placed by You on PeelJobs.
							</p>
							<p>
								PeelJobs reserves the right to offer third party services and products to You
								based on the preferences that You identify in Your registration and at any time
								thereafter or you have agreed to receive, such offers may be made by PeelJobs or
								by third parties.
							</p>
							<p>
								You understand and acknowledge that You have no ownership rights in Your account and
								that if You cancel/terminate Your PeelJobs account, all Your account information from
								PeelJobs, including resumes, Profiles, cover letters, saved jobs, questionnaires
								will be marked as deleted in and may be deleted from our databases. Information may
								continue to be available for some period of time because of delays in propagating such
								deletion through PeelJobs's web servers. In addition, third parties may retain saved
								copies of Your Information.
							</p>
							<p>
								PeelJobs reserves the right to delete Your account and all of Your Information
								after a significant duration of inactivity.
							</p>
						</div>
					</article>

					<!-- Prohibited User Conduct -->
					<article id="prohibited-users" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-error-light rounded-xl flex items-center justify-center">
								<Ban size={24} class="text-error" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Specific Prohibited Conduct of Users</h2>
						</div>
						<p class="text-muted mb-4">Prohibited Uses of the System include:</p>
						<div class="bg-error-light rounded-lg p-6 border border-error/20">
							<ul class="space-y-3 text-muted">
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Post any resume or apply for any job on behalf of another party</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Set more than one copy of the same resume to public at any one time</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Post or submit to PeelJobs any incomplete, false or inaccurate biographical
									information or information which is not your own</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Delete or revise any material posted by any other person or entity</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Take any action that imposes an unreasonable or disproportionately large load on
									PeelJobs's infrastructure</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-error rounded-full mt-2 flex-shrink-0"></div>
									<span>Use PeelJobs Services for any unlawful purpose or any illegal activity, or post
									or submit any content, resume that is defamatory, libelous, implicitly or explicitly
									offensive, vulgar, obscene, threatening, abusive, hateful, racist, discriminatory, of
									a menacing character or likely to cause annoyance, inconvenience, embarrassment,
									anxiety or could cause harassment to any person or include any links to pornographic,
									indecent or sexually explicit material of any kind</span>
								</li>
							</ul>
						</div>
					</article>

					<!-- Reservation of Rights -->
					<article id="rights" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Shield size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Reservation of Rights</h2>
						</div>
						<p class="text-muted leading-relaxed">
							Any rights not expressly granted herein are reserved.
						</p>
					</article>

					<!-- Revisions -->
					<article id="revisions" class="mb-10 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<RefreshCw size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">Revisions</h2>
						</div>
						<p class="text-muted leading-relaxed">
							PeelJobs may revise these Terms at any time by posting an updated version to
							https://www.peeljobs.com. You should visit this page periodically to review the most
							current Agreement because it is binding on Users.
						</p>
					</article>

					<!-- Contact CTA -->
					<div class="bg-primary/10 rounded-lg p-6 border border-primary/20">
						<div class="flex items-start gap-4">
							<div class="w-12 h-12 bg-primary rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm">
								<MessageCircle size={24} class="text-white" />
							</div>
							<div>
								<h3 class="text-lg font-semibold text-black mb-2">Questions?</h3>
								<p class="text-muted mb-4">
									For any questions, or legal concerns, please email Support at PeelJobs.
								</p>
								<a
									href="/contact/"
									class="inline-flex items-center gap-2 px-6 py-2.5 bg-primary hover:bg-primary-hover text-white font-medium rounded-full transition-colors shadow-sm"
								>
									Contact Support
									<ArrowRight size={16} />
								</a>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- CTA Section -->
<section class="py-12 lg:py-16 bg-[#1D2226] text-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8 text-center">
		<div class="max-w-2xl mx-auto">
			<h2 class="text-2xl font-semibold tracking-tight mb-4">Have Questions About Our Terms?</h2>
			<p class="text-gray-300 mb-8">
				We're here to help. Reach out to our team for any questions or clarifications about our terms of service.
			</p>
			<a
				href="/contact/"
				class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-black font-medium rounded-full hover:bg-gray-100 transition-colors shadow-sm"
			>
				Contact Support
				<ArrowRight size={18} />
			</a>
		</div>
	</div>
</section>
