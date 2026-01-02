<script lang="ts">
	import { Shield, ChevronRight, Lock, Database, UserCheck, AlertTriangle, Eye, Cookie, Globe, Users, Bell, MessageCircle, ArrowRight } from '@lucide/svelte';

	const lastUpdated = 'October 19, 2025';

	interface Section {
		id: string;
		title: string;
		icon: typeof Shield;
	}

	const sections: Section[] = [
		{ id: 'introduction', title: 'Introduction', icon: Shield },
		{ id: 'cookies', title: 'Cookies and Tracking', icon: Cookie },
		{ id: 'third-party', title: 'Third Party Services', icon: Globe },
		{ id: 'consent', title: 'Your Consent', icon: UserCheck },
		{ id: 'security', title: 'Information Security', icon: Lock },
		{ id: 'updating', title: 'Updating Information', icon: Database },
		{ id: 'children', title: 'Children', icon: Users },
		{ id: 'sharing', title: 'Information Sharing', icon: Eye },
		{ id: 'confidentiality', title: 'Confidentiality', icon: Shield },
		{ id: 'changes', title: 'Policy Changes', icon: Bell },
		{ id: 'disclaimer', title: 'Disclaimer', icon: AlertTriangle },
		{ id: 'contact', title: 'Contact Information', icon: MessageCircle }
	];

	function scrollToSection(id: string): void {
		const element = document.getElementById(id);
		if (element) {
			element.scrollIntoView({ behavior: 'smooth', block: 'start' });
		}
	}
</script>

<svelte:head>
	<title>Privacy Policy - PeelJobs | How We Protect Your Data</title>
	<meta
		name="description"
		content="PeelJobs privacy policy explains how we collect, use, and protect your personal information. Learn about our commitment to data security, cookies, third-party services, and your privacy rights."
	/>
	<link rel="canonical" href="https://peeljobs.com/privacy/" />

	<!-- Open Graph -->
	<meta property="og:title" content="Privacy Policy - PeelJobs" />
	<meta property="og:description" content="Learn how PeelJobs protects your privacy and personal information." />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://peeljobs.com/privacy/" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary" />
	<meta name="twitter:title" content="Privacy Policy - PeelJobs" />
	<meta name="twitter:description" content="Our commitment to protecting your privacy and data." />
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
					<span class="text-white font-medium">Privacy Policy</span>
				</li>
			</ol>
		</nav>

		<div class="max-w-4xl mx-auto text-center">
			<div class="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-8 animate-fade-in-up" style="opacity: 0;">
				<Shield size={40} class="text-primary" />
			</div>
			<h1 class="text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight mb-6 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
				Privacy Policy
			</h1>
			<p class="text-lg md:text-xl text-gray-300 mb-4 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms;">
				Your privacy is important to us. Learn how we collect, use, and protect your personal information.
			</p>
			<p class="text-sm text-muted animate-fade-in-up" style="opacity: 0; animation-delay: 300ms;">Last Updated: {lastUpdated}</p>
		</div>
	</div>
</section>

<!-- Quick Summary -->
<section class="py-12 lg:py-16 bg-surface">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="max-w-4xl mx-auto">
			<div class="bg-primary/10 rounded-lg p-6 lg:p-8 border border-primary/20">
				<div class="flex items-start gap-4">
					<div class="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center flex-shrink-0">
						<Shield size={24} class="text-primary" />
					</div>
					<div>
						<h2 class="text-xl font-semibold text-black mb-3">Privacy at a Glance</h2>
						<ul class="space-y-2 text-muted">
							<li class="flex items-center gap-2">
								<Lock size={16} class="text-primary flex-shrink-0" />
								We use industry-standard encryption to protect your data
							</li>
							<li class="flex items-center gap-2">
								<Eye size={16} class="text-primary flex-shrink-0" />
								We don't sell your personal information to third parties
							</li>
							<li class="flex items-center gap-2">
								<UserCheck size={16} class="text-primary flex-shrink-0" />
								You control what information is visible on your profile
							</li>
							<li class="flex items-center gap-2">
								<Database size={16} class="text-primary flex-shrink-0" />
								You can request deletion of your data at any time
							</li>
						</ul>
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

			<!-- Privacy Policy Content -->
			<div class="lg:col-span-3">
				<div class="bg-white rounded-lg shadow-sm border border-border p-6 lg:p-10">
					<!-- Introduction -->
					<article id="introduction" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Shield size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">1. Introduction</h2>
						</div>
						<div class="space-y-4 text-muted leading-relaxed">
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
					</article>

					<!-- Cookies Section -->
					<article id="cookies" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Cookie size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">2. Cookies and Tracking Technologies</h2>
						</div>
						<div class="bg-surface rounded-lg p-6 border border-border">
							<div class="space-y-4 text-muted leading-relaxed">
								<p>
									Some of our web pages utilize "cookies" and other tracking technologies. A
									"cookie" is a small text file that may be used, for example, to collect
									information about website activity. Some cookies and other technologies may serve
									to recall Personal Information previously indicated by a web user.
								</p>
								<p>
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
					</article>

					<!-- Third Party Services -->
					<article id="third-party" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Globe size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">3. Third Party Services</h2>
						</div>
						<div class="space-y-4 text-muted leading-relaxed">
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
					</article>

					<!-- Your Consent -->
					<article id="consent" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<UserCheck size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">4. Your Consent</h2>
						</div>
						<div class="bg-primary/10 rounded-lg p-6 border border-primary/20">
							<p class="text-muted leading-relaxed">
								By using this website, you consent to the terms of our Privacy Policy and to our
								processing of Personal Information for the purposes given above as well as those
								explained where we collect Personal Information on the web.
							</p>
						</div>
					</article>

					<!-- Information Security -->
					<article id="security" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-success-light rounded-xl flex items-center justify-center">
								<Lock size={24} class="text-success" />
							</div>
							<h2 class="text-2xl font-semibold text-black">5. Information Security</h2>
						</div>
						<div class="bg-success-light rounded-lg p-6 border border-success/20">
							<ul class="space-y-4 text-muted">
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-success rounded-full mt-2 flex-shrink-0"></div>
									<span>We take appropriate security measures to protect against unauthorized access to or
									unauthorized alteration, disclosure or destruction of data.</span>
								</li>
								<li class="flex items-start gap-3">
									<div class="w-2 h-2 bg-success rounded-full mt-2 flex-shrink-0"></div>
									<span>We restrict access to your personally identifying information to employees who need
									to know that information in order to operate, develop or improve our services.</span>
								</li>
							</ul>
						</div>
					</article>

					<!-- Updating Information -->
					<article id="updating" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Database size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">6. Updating Your Information</h2>
						</div>
						<p class="text-muted leading-relaxed">
							We provide mechanisms for updating and correcting your personally identifying
							information for many of our services. For more information, please see the help
							documentation for each service.
						</p>
					</article>

					<!-- Children -->
					<article id="children" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Users size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">7. Children</h2>
						</div>
						<p class="text-muted leading-relaxed">
							PeelJobs will not contact children under age 13 about special offers or for marketing
							purposes without a parent's permission.
						</p>
					</article>

					<!-- Information Sharing -->
					<article id="sharing" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Eye size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">8. Information Sharing and Disclosure</h2>
						</div>
						<div class="bg-surface rounded-lg p-6 border border-border mb-6">
							<p class="font-semibold text-black mb-4">
								PeelJobs does not rent, sell, or share personal information about you with other
								people (save with your consent) or non-affiliated companies except to provide products
								or services you've requested, when we have your permission, or under the following
								circumstances:
							</p>
							<ol class="space-y-3 text-muted list-decimal list-inside">
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
						<ul class="space-y-3 text-muted">
							<li class="flex items-start gap-3">
								<div class="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
								<span>PeelJobs does not provide any personal information to advertisers when you interact
								with or view a targeted ad.</span>
							</li>
							<li class="flex items-start gap-3">
								<div class="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
								<span>Our advertisers include financial service providers and non-financial companies.</span>
							</li>
						</ul>
					</article>

					<!-- Confidentiality -->
					<article id="confidentiality" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<Shield size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">9. Confidentiality and Security</h2>
						</div>
						<ul class="space-y-3 text-muted leading-relaxed">
							<li class="flex items-start gap-3">
								<div class="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
								<span>We limit access to personal information about you to employees who we believe reasonably
								need to come into contact with that information.</span>
							</li>
							<li class="flex items-start gap-3">
								<div class="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
								<span>We have physical, electronic, and procedural safeguards that comply with Indian laws to
								protect personal information about you.</span>
							</li>
						</ul>
					</article>

					<!-- Policy Changes -->
					<article id="changes" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-warning-light rounded-xl flex items-center justify-center">
								<Bell size={24} class="text-warning" />
							</div>
							<h2 class="text-2xl font-semibold text-black">10. Changes to This Privacy Policy</h2>
						</div>
						<div class="bg-warning-light rounded-lg p-6 border border-warning/20">
							<p class="text-muted leading-relaxed">
								PeelJobs reserves the right to update, change or modify this policy at any time. The
								policy shall come into effect from the date of such update, change or modification.
							</p>
						</div>
					</article>

					<!-- Disclaimer -->
					<article id="disclaimer" class="mb-12 scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-error-light rounded-xl flex items-center justify-center">
								<AlertTriangle size={24} class="text-error" />
							</div>
							<h2 class="text-2xl font-semibold text-black">11. Disclaimer</h2>
						</div>
						<div class="bg-error-light rounded-lg p-6 border border-error/20">
							<div class="space-y-4 text-muted leading-relaxed">
								<p>
									PeelJobs does not store or keep credit card data in a location that is accessible via
									the Internet. Once a credit card transaction has been completed, all credit card data
									is moved offline to ensure maximum security.
								</p>
								<p class="font-semibold text-black">
									PeelJobs shall not be liable for any loss or damage sustained by reason of any
									disclosure of any information concerning the user's account and/or information
									relating to online transactions using credit cards/debit cards.
								</p>
							</div>
						</div>
					</article>

					<!-- Contact Information -->
					<article id="contact" class="scroll-mt-6">
						<div class="flex items-center gap-4 mb-6">
							<div class="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center">
								<MessageCircle size={24} class="text-primary" />
							</div>
							<h2 class="text-2xl font-semibold text-black">12. Contact Information</h2>
						</div>
						<div class="bg-surface rounded-lg p-6 border border-border">
							<p class="text-muted leading-relaxed mb-4">
								PeelJobs welcomes your comments regarding this privacy statement. Should there be any
								concerns about contravention of this Privacy Policy, we will employ all commercially
								reasonable efforts to address the same.
							</p>
							<a
								href="/contact/"
								class="inline-flex items-center gap-2 text-primary hover:text-primary-hover font-medium"
							>
								Contact Us
								<ArrowRight size={16} />
							</a>
							<p class="text-sm text-muted mt-4">
								<strong>Note:</strong> The terms in this agreement may be changed by PeelJobs at any time.
								PeelJobs is free to offer its services to any client/prospective client without restriction.
							</p>
						</div>
					</article>

					<!-- Acknowledgment -->
					<div class="bg-primary/10 rounded-lg p-6 mt-10 border border-primary/20">
						<h3 class="font-semibold text-primary mb-2">Your Consent</h3>
						<p class="text-primary/80">
							By using PeelJobs, you acknowledge that you have read and understood this Privacy Policy
							and consent to the collection, use, and disclosure of your information as described
							herein.
						</p>
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
			<h2 class="text-2xl font-semibold tracking-tight mb-4">Have Questions About Your Privacy?</h2>
			<p class="text-gray-300 mb-8">
				We're here to help. Reach out to our team for any privacy-related questions or concerns.
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
