<script lang="ts">
	import { Check, X, Zap, Users, TrendingUp, Shield, Clock, Heart, Award, Target, Sparkles, ArrowRight, BadgeCheck, ChevronRight, ChevronDown } from '@lucide/svelte';

	// Features included in the free plan
	const includedFeatures = [
		{ name: 'Unlimited Job Postings', icon: Zap },
		{ name: 'Access to Entire Candidate Database', icon: Users },
		{ name: 'Advanced Search & Filters', icon: Target },
		{ name: 'Application Tracking System', icon: TrendingUp },
		{ name: 'Email Notifications', icon: Clock },
		{ name: 'Company Profile Page', icon: BadgeCheck },
		{ name: 'Resume Database Access', icon: Users },
		{ name: 'Candidate Messaging', icon: Heart },
		{ name: 'Priority Customer Support', icon: Shield },
		{ name: 'Analytics & Insights', icon: Award }
	];

	// What competitors charge for
	const competitorFeatures = [
		{ name: 'Job Posting Fees', free: true, competitors: false },
		{ name: 'Resume Database Access', free: true, competitors: false },
		{ name: 'Featured Listings', free: true, competitors: false },
		{ name: 'Unlimited Applications', free: true, competitors: false },
		{ name: 'Advanced Analytics', free: true, competitors: false }
	];

	// FAQs
	const faqs = [
		{
			question: 'Is PeelJobs really 100% free?',
			answer: "Yes! We never charge for job postings, candidate access, or any recruiting features. Our mission is to connect employers with the best talent in India at zero cost."
		},
		{
			question: 'Are there any hidden fees or premium plans?',
			answer: "No hidden fees whatsoever. We don't have premium plans because we believe all employers deserve equal access to top talent, regardless of their budget."
		},
		{
			question: 'How do you make money if everything is free?',
			answer: "We're supported by strategic partnerships and display advertising. We never compromise the quality of our platform or charge employers for core recruiting features."
		},
		{
			question: 'Will you start charging in the future?',
			answer: "No. We're committed to keeping PeelJobs free forever. Our goal is to make quality hiring accessible to every employer in India, from startups to enterprises."
		},
		{
			question: 'How many jobs can I post?',
			answer: "There's no limit! Post as many jobs as you need, whenever you need. We want to help you build your entire team without worrying about costs."
		},
		{
			question: 'Can I access the resume database for free?',
			answer: 'Absolutely! You get full access to our database of over 1 million job seekers, including advanced search filters, without paying a single rupee.'
		},
		{
			question: 'How quickly can I start posting jobs?',
			answer: 'You can create an account and post your first job in under 5 minutes. No credit card required, no approval wait times.'
		},
		{
			question: 'What kind of support do I get?',
			answer: "All employers get access to our dedicated support team via email and chat. We're here to help you succeed in finding the right talent."
		}
	];

	let openFaqIndex = $state<number | null>(null);

	function toggleFaq(index: number) {
		openFaqIndex = openFaqIndex === index ? null : index;
	}
</script>

<svelte:head>
	<title>Pricing - 100% Free Forever | PeelJobs - India's Free Job Posting Platform</title>
	<meta name="description" content="Post unlimited jobs for FREE. No hidden costs, no premium plans. Access 1M+ candidates, advanced hiring tools, and unlimited job postings at zero cost. Join 50K+ employers hiring on PeelJobs." />
	<meta property="og:title" content="100% Free Job Posting Platform - PeelJobs Pricing" />
	<meta property="og:description" content="Never pay for job postings again. Unlimited free access to India's largest talent pool. Post jobs, search resumes, and hire the best candidates - all for free." />
	<meta property="og:type" content="website" />
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="100% Free Job Posting Platform - PeelJobs Pricing" />
	<meta name="twitter:description" content="Unlimited job postings, resume database access, and hiring tools - all FREE forever." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-gray-900 text-white py-16 lg:py-24 relative overflow-hidden">
	<!-- Decorative Elements -->
	<div class="absolute inset-0 overflow-hidden">
		<div class="absolute top-0 left-1/4 w-96 h-96 bg-success-500/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 right-1/4 w-80 h-80 bg-primary-500/10 rounded-full blur-3xl"></div>
	</div>

	<div class="max-w-7xl mx-auto px-4 lg:px-8 relative">
		<!-- Breadcrumb -->
		<nav class="mb-8" aria-label="Breadcrumb">
			<ol class="flex items-center gap-2 text-sm text-gray-400">
				<li>
					<a href="/" class="hover:text-white transition-colors">Home</a>
				</li>
				<li class="flex items-center gap-2">
					<ChevronRight size={14} />
					<span class="text-white font-medium">Pricing</span>
				</li>
			</ol>
		</nav>

		<div class="max-w-4xl mx-auto text-center">
			<!-- Free Badge -->
			<div class="inline-flex items-center gap-2 px-4 py-2 bg-success-500/20 text-success-500 rounded-full text-sm font-medium mb-6 animate-fade-in-down" style="opacity: 0;">
				<Sparkles size={16} />
				<span>100% Free Forever</span>
			</div>

			<h1 class="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
				Hire the Best Talent in India
				<span class="block text-success-500 mt-2">Without Spending a Rupee</span>
			</h1>

			<p class="text-lg md:text-xl text-gray-300 leading-relaxed mb-10 max-w-3xl mx-auto animate-fade-in-up" style="opacity: 0; animation-delay: 200ms;">
				Join 50,000+ employers who trust PeelJobs for their hiring needs. Post unlimited jobs, access 1 million+ candidates, and build your dream team - all for <strong class="text-white">FREE</strong>.
			</p>

			<!-- CTA Buttons -->
			<div class="flex flex-col sm:flex-row gap-4 justify-center mb-10 animate-fade-in-up" style="opacity: 0; animation-delay: 300ms;">
				<a href="/employer/" class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-gray-900 font-medium rounded-full hover:bg-gray-100 transition-colors elevation-1">
					Start Hiring Free
					<ArrowRight size={18} />
				</a>
				<a href="#features" class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 text-white font-medium rounded-full hover:bg-white/20 transition-colors border border-white/20">
					See What's Included
				</a>
			</div>

			<!-- Trust Indicators -->
			<div class="flex flex-wrap justify-center gap-6 text-sm text-gray-400 animate-fade-in-up" style="opacity: 0; animation-delay: 400ms;">
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>No Credit Card Required</span>
				</div>
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>No Hidden Fees</span>
				</div>
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>Setup in 5 Minutes</span>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Pricing Card Section -->
<section id="features" class="py-16 lg:py-24 bg-surface-50">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-4">One Simple Plan. Everything Included.</h2>
			<p class="text-base lg:text-lg text-gray-600 max-w-3xl mx-auto">
				No tiers, no upsells, no complicated pricing. Just one powerful platform with everything you need to hire great people.
			</p>
		</div>

		<!-- Main Pricing Card -->
		<div class="max-w-2xl mx-auto">
			<div class="bg-white rounded-2xl elevation-3 overflow-hidden border-2 border-primary-600 relative">
				<!-- Popular Badge -->
				<div class="absolute top-0 right-0 bg-primary-600 text-white px-5 py-2 text-sm font-medium rounded-bl-2xl">
					Most Popular
				</div>

				<div class="p-8 lg:p-10">
					<!-- Plan Header -->
					<div class="text-center mb-8">
						<h3 class="text-2xl lg:text-3xl font-bold text-gray-900 mb-4">Free Forever Plan</h3>
						<div class="mb-4">
							<span class="text-6xl lg:text-7xl font-bold text-primary-600">₹0</span>
							<span class="text-2xl text-gray-500 ml-2">forever</span>
						</div>
						<p class="text-gray-600 text-lg">Everything you need to build your team. No catch.</p>
					</div>

					<!-- Features List -->
					<div class="space-y-4 mb-8">
						{#each includedFeatures as feature, i}
							{@const FeatureIcon = feature.icon}
							<div class="flex items-start gap-3 animate-fade-in-up" style="opacity: 0; animation-delay: {i * 50}ms;">
								<div class="w-6 h-6 rounded-full bg-success-500/10 flex items-center justify-center flex-shrink-0 mt-0.5">
									<Check size={14} class="text-success-600" />
								</div>
								<div class="flex items-center gap-3 flex-1">
									<FeatureIcon size={18} class="text-primary-600 flex-shrink-0" />
									<span class="text-gray-700 font-medium">{feature.name}</span>
								</div>
							</div>
						{/each}
					</div>

					<!-- CTA Button -->
					<a href="/employer/" class="w-full flex items-center justify-center gap-2 px-8 py-4 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-full transition-colors elevation-1 hover:elevation-2">
						Get Started Free
						<ArrowRight size={18} />
					</a>
				</div>
			</div>
		</div>
	</div>
</section>

<!-- Comparison Section -->
<section class="py-16 lg:py-24 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-4">How We Compare</h2>
			<p class="text-base lg:text-lg text-gray-600 max-w-3xl mx-auto">
				See what other platforms charge thousands for - and what we give you for free.
			</p>
		</div>

		<div class="max-w-4xl mx-auto">
			<div class="bg-white rounded-2xl elevation-1 overflow-hidden border border-gray-100">
				<!-- Header Row -->
				<div class="grid grid-cols-3 bg-surface-50 border-b border-gray-100">
					<div class="p-4 lg:p-6"></div>
					<div class="p-4 lg:p-6 text-center border-l border-gray-100">
						<div class="font-bold text-primary-600 text-lg lg:text-xl">PeelJobs</div>
						<div class="text-xs lg:text-sm text-gray-500 mt-1">Free Forever</div>
					</div>
					<div class="p-4 lg:p-6 text-center border-l border-gray-100">
						<div class="font-bold text-gray-900 text-lg lg:text-xl">Competitors</div>
						<div class="text-xs lg:text-sm text-gray-500 mt-1">₹10K-50K/month</div>
					</div>
				</div>

				<!-- Feature Rows -->
				{#each competitorFeatures as feature}
					<div class="grid grid-cols-3 border-b border-gray-100 last:border-b-0 hover:bg-surface-50 transition-colors">
						<div class="p-4 lg:p-6 font-medium text-gray-700 text-sm lg:text-base">{feature.name}</div>
						<div class="p-4 lg:p-6 text-center border-l border-gray-100">
							{#if feature.free}
								<div class="inline-flex items-center justify-center w-8 h-8 bg-success-500/10 rounded-full">
									<Check size={16} class="text-success-600" />
								</div>
							{:else}
								<div class="inline-flex items-center justify-center w-8 h-8 bg-error-500/10 rounded-full">
									<X size={16} class="text-error-600" />
								</div>
							{/if}
						</div>
						<div class="p-4 lg:p-6 text-center border-l border-gray-100">
							{#if feature.competitors}
								<div class="inline-flex items-center justify-center w-8 h-8 bg-success-500/10 rounded-full">
									<Check size={16} class="text-success-600" />
								</div>
							{:else}
								<div class="inline-flex items-center justify-center w-8 h-8 bg-error-500/10 rounded-full">
									<X size={16} class="text-error-600" />
								</div>
								<div class="text-xs text-gray-500 mt-1 hidden lg:block">Extra Cost</div>
							{/if}
						</div>
					</div>
				{/each}
			</div>
		</div>
	</div>
</section>

<!-- Why Free Section -->
<section class="py-16 lg:py-24 bg-surface-50">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-4">Why Is PeelJobs Free?</h2>
			<p class="text-base lg:text-lg text-gray-600 max-w-3xl mx-auto">
				Our mission is simple: connect employers with the best talent in India without financial barriers.
			</p>
		</div>

		<div class="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
			<div class="bg-white rounded-2xl p-8 elevation-1 hover:elevation-3 transition-all border border-gray-100">
				<div class="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center mb-6">
					<Heart size={28} class="text-primary-600" />
				</div>
				<h3 class="text-xl font-bold text-gray-900 mb-4">Our Mission</h3>
				<p class="text-gray-600 leading-relaxed">
					We believe every company, from startups to enterprises, deserves access to top talent without budget constraints limiting their growth.
				</p>
			</div>

			<div class="bg-white rounded-2xl p-8 elevation-1 hover:elevation-3 transition-all border border-gray-100">
				<div class="w-14 h-14 bg-success-500/20 rounded-2xl flex items-center justify-center mb-6">
					<Users size={28} class="text-success-600" />
				</div>
				<h3 class="text-xl font-bold text-gray-900 mb-4">More Opportunities</h3>
				<p class="text-gray-600 leading-relaxed">
					By eliminating posting fees, we create more job opportunities for seekers and help employers find candidates they otherwise couldn't afford to reach.
				</p>
			</div>

			<div class="bg-white rounded-2xl p-8 elevation-1 hover:elevation-3 transition-all border border-gray-100">
				<div class="w-14 h-14 bg-primary-50 rounded-2xl flex items-center justify-center mb-6">
					<TrendingUp size={28} class="text-primary-600" />
				</div>
				<h3 class="text-xl font-bold text-gray-900 mb-4">Better Outcomes</h3>
				<p class="text-gray-600 leading-relaxed">
					When more employers can afford to post jobs and more candidates apply, everyone wins. We measure success by successful hires, not revenue.
				</p>
			</div>
		</div>
	</div>
</section>

<!-- FAQ Section -->
<section class="py-16 lg:py-24 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-12">
			<h2 class="text-2xl lg:text-3xl font-bold text-gray-900 tracking-tight mb-4">Frequently Asked Questions</h2>
			<p class="text-base lg:text-lg text-gray-600 max-w-3xl mx-auto">
				Everything you need to know about our free platform
			</p>
		</div>

		<div class="max-w-3xl mx-auto space-y-3">
			{#each faqs as faq, index}
				<div class="bg-surface-50 rounded-2xl border border-gray-100 hover:border-primary-200 transition-colors overflow-hidden">
					<button onclick={() => toggleFaq(index)} class="w-full px-6 py-5 text-left flex justify-between items-center gap-4">
						<span class="font-semibold text-gray-900 text-base lg:text-lg">{faq.question}</span>
						<div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary-50 flex items-center justify-center">
							<ChevronDown size={18} class="text-primary-600 transform transition-transform {openFaqIndex === index ? 'rotate-180' : ''}" />
						</div>
					</button>
					{#if openFaqIndex === index}
						<div class="px-6 pb-5 text-gray-600 leading-relaxed animate-fade-in">
							{faq.answer}
						</div>
					{/if}
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Final CTA Section -->
<section class="py-16 lg:py-24 bg-gray-900 text-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8 text-center">
		<div class="max-w-3xl mx-auto">
			<h2 class="text-2xl lg:text-3xl font-bold tracking-tight mb-6">Ready to Start Hiring?</h2>
			<p class="text-lg text-gray-300 mb-10 leading-relaxed">
				Join thousands of employers who are building amazing teams without spending a rupee. Create your free account in minutes and post your first job today.
			</p>

			<div class="flex flex-col sm:flex-row gap-4 justify-center mb-10">
				<a href="/employer/" class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-gray-900 font-medium rounded-full hover:bg-gray-100 transition-colors elevation-1">
					Create Free Account
					<ArrowRight size={18} />
				</a>
				<a href="/contact/" class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 text-white font-medium rounded-full hover:bg-white/20 transition-colors border border-white/20">
					Talk to Our Team
				</a>
			</div>

			<div class="flex flex-wrap justify-center gap-6 text-sm text-gray-400">
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>Free Forever</span>
				</div>
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>No Credit Card</span>
				</div>
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>5 Minute Setup</span>
				</div>
				<div class="flex items-center gap-2">
					<Check size={16} class="text-success-500" />
					<span>Unlimited Postings</span>
				</div>
			</div>
		</div>
	</div>
</section>
