<script lang="ts">
	import {
		Zap,
		Users,
		Building2,
		Target,
		Shield,
		Award,
		CheckCircle2,
		ChevronRight,
		Heart,
		DollarSign,
		Lightbulb,
		Globe,
		Rocket,
		ArrowRight,
		Sparkles
	} from '@lucide/svelte';

	const coreValues = [
		{
			icon: Shield,
			title: 'Equity',
			description: 'Every company deserves access to great talent, and every job seeker deserves access to great opportunities—without paywalls or artificial barriers.'
		},
		{
			icon: Shield,
			title: 'Transparency',
			description: 'We foster open, honest communication between employers and candidates, with clear expectations and straightforward processes.'
		},
		{
			icon: Users,
			title: 'User-Centricity',
			description: 'Our platform is designed with deep empathy for both recruiters and job seekers, continuously refined based on real user feedback.'
		},
		{
			icon: Award,
			title: 'Excellence',
			description: 'We pursue technical excellence, operational efficiency, and exceptional user experiences in everything we build and deliver.'
		},
		{
			icon: Heart,
			title: 'Community Impact',
			description: 'We\'re committed to making a positive social impact by connecting people with meaningful work and helping businesses thrive.'
		}
	];

	const features = [
		{
			icon: DollarSign,
			title: 'Completely Free',
			description: 'Zero cost for both job posting and candidate access. No hidden fees, no paywalls—just free, accessible hiring for everyone.'
		},
		{
			icon: Zap,
			title: 'Fast & Efficient',
			description: 'Streamlined recruitment process with intuitive tools, intelligent search, and automated workflows that save hours of work.'
		},
		{
			icon: Target,
			title: 'Smart Matching',
			description: 'Advanced filters and AI-powered recommendations help you find the perfect match faster.'
		}
	];

	const benefits = {
		jobSeekers: [
			'Access to diverse jobs across all industries and locations',
			'Advanced filters by skill, location, experience, and job type',
			'Comprehensive profiles to showcase your achievements',
			'Real-time notifications for relevant job matches',
			'Completely free—no charges for applying or searching'
		],
		companies: [
			'Post unlimited jobs at zero cost',
			'Access to a large, continuously refreshed candidate database',
			'Professional company profiles to attract top talent',
			'Analytics and reporting to optimize hiring strategies',
			'Efficient applicant tracking and communication tools'
		]
	};

	const missionPillars = [
		{ icon: DollarSign, title: 'Accessibility', description: 'Cost-free platform ensuring businesses of all sizes can access top-tier talent without financial barriers.' },
		{ icon: Zap, title: 'Efficiency', description: 'Streamlined recruitment with intuitive tools enabling faster and more effective hiring decisions.' },
		{ icon: Users, title: 'Empowerment', description: 'Supporting job seekers with equal access to opportunities and helping companies build strong teams.' },
		{ icon: Lightbulb, title: 'Innovation', description: 'Continuously enhancing our platform with cutting-edge features to meet evolving job market needs.' },
		{ icon: Shield, title: 'Quality & Trust', description: 'Maintaining high standards with verified profiles, authentic listings, and transparent communication.' }
	];
</script>

<svelte:head>
	<title>About Us - PeelJobs | Free Job Portal Democratizing Hiring</title>
	<meta
		name="description"
		content="PeelJobs is a free job portal connecting talent with opportunity. Learn about our mission to democratize hiring, making exceptional recruitment accessible to businesses of all sizes without financial barriers."
	/>
	<link rel="canonical" href="https://peeljobs.com/about/" />

	<!-- Open Graph -->
	<meta property="og:title" content="About PeelJobs - Democratizing Hiring, One Connection at a Time" />
	<meta property="og:description" content="Discover how PeelJobs is transforming recruitment with our free, accessible platform that empowers companies and job seekers alike." />
	<meta property="og:type" content="website" />
	<meta property="og:url" content="https://peeljobs.com/about/" />

	<!-- Twitter Card -->
	<meta name="twitter:card" content="summary_large_image" />
	<meta name="twitter:title" content="About PeelJobs - Free Job Portal" />
	<meta name="twitter:description" content="Learn about our mission to democratize hiring for all." />
</svelte:head>

<!-- Hero Section -->
<section class="bg-[#1D2226] text-white py-16 lg:py-24 relative overflow-hidden">
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
					<span class="text-white font-medium">About Us</span>
				</li>
			</ol>
		</nav>

		<!-- Hero Content -->
		<div class="text-center max-w-4xl mx-auto">
			<div class="inline-flex items-center gap-2 px-4 py-2 bg-primary/20 text-white/80 rounded-full text-sm font-medium mb-6 animate-fade-in-down" style="opacity: 0;">
				<Sparkles size={16} />
				<span>100% Free Forever</span>
			</div>

			<div class="w-20 h-20 bg-white/10 rounded-full flex items-center justify-center mx-auto mb-8 animate-fade-in-up" style="opacity: 0; animation-delay: 100ms;">
				<Rocket size={40} class="text-primary" />
			</div>

			<h1 class="text-4xl md:text-5xl lg:text-6xl font-semibold tracking-tight mb-6 animate-fade-in-up" style="opacity: 0; animation-delay: 200ms;">
				Democratizing Hiring,<br class="hidden md:block" />
				One Connection at a Time
			</h1>

			<p class="text-lg md:text-xl text-gray-300 max-w-3xl mx-auto leading-relaxed animate-fade-in-up" style="opacity: 0; animation-delay: 300ms;">
				We're on a mission to make exceptional hiring accessible to every organization,
				regardless of size or budget, while empowering job seekers to find meaningful careers.
			</p>
		</div>
	</div>
</section>

<!-- Vision & Mission Cards -->
<section class="py-16 lg:py-24 bg-surface">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="grid md:grid-cols-2 gap-6 lg:gap-8">
			<!-- Vision -->
			<div class="bg-white rounded-lg p-6 lg:p-8 shadow-sm hover:shadow-lg transition-all border border-border">
				<div class="flex items-center gap-4 mb-5">
					<div class="w-14 h-14 rounded-lg bg-primary/20 flex items-center justify-center">
						<Globe size={28} class="text-primary" />
					</div>
					<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight">Our Vision</h2>
				</div>
				<p class="text-base lg:text-lg text-muted leading-relaxed">
					To become the leading free job portal that transforms how companies and talent connect,
					building a future where exceptional hiring is accessible to every organization, regardless
					of size or budget.
				</p>
			</div>

			<!-- Aim -->
			<div class="bg-white rounded-lg p-6 lg:p-8 shadow-sm hover:shadow-lg transition-all border border-border">
				<div class="flex items-center gap-4 mb-5">
					<div class="w-14 h-14 rounded-lg bg-success-light flex items-center justify-center">
						<Target size={28} class="text-success" />
					</div>
					<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight">Our Aim</h2>
				</div>
				<p class="text-base lg:text-lg text-muted leading-relaxed">
					To create a dynamic platform that empowers companies to connect with exceptional talent
					at no cost, fostering opportunities for meaningful employment and driving organizational
					growth through accessible, equitable, and efficient hiring.
				</p>
			</div>
		</div>
	</div>
</section>

<!-- Mission Section -->
<section class="py-16 lg:py-24 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="bg-primary/10 rounded-lg p-8 lg:p-12 border border-primary/20">
			<div class="text-center mb-10 lg:mb-12">
				<div class="w-16 h-16 bg-primary/20 rounded-full flex items-center justify-center mx-auto mb-6">
					<Zap size={32} class="text-primary" />
				</div>
				<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-4">Our Mission</h2>
				<p class="text-base lg:text-lg text-muted max-w-3xl mx-auto">
					We democratize the hiring process by providing a free, user-friendly job portal that
					bridges the gap between companies and talented individuals.
				</p>
			</div>

			<div class="grid sm:grid-cols-2 lg:grid-cols-5 gap-4 lg:gap-6">
				{#each missionPillars as pillar, i}
					<div
						class="bg-white rounded-lg p-5 lg:p-6 shadow-sm hover:shadow-lg transition-all animate-fade-in-up"
						style="opacity: 0; animation-delay: {i * 100}ms;"
					>
						<div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center mb-4">
							<svelte:component this={pillar.icon} size={20} class="text-primary" />
						</div>
						<h3 class="font-semibold text-black mb-2">{pillar.title}</h3>
						<p class="text-sm text-muted leading-relaxed">{pillar.description}</p>
					</div>
				{/each}
			</div>
		</div>
	</div>
</section>

<!-- Core Values -->
<section class="py-16 lg:py-24 bg-surface">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-10 lg:mb-12">
			<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-4">Our Core Values</h2>
			<p class="text-base lg:text-lg text-muted max-w-3xl mx-auto">
				These fundamental principles guide everything we do at PeelJobs
			</p>
		</div>

		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each coreValues as value, i}
				<div
					class="group bg-white rounded-lg p-6 shadow-sm hover:shadow-lg transition-all border border-border animate-fade-in-up"
					style="opacity: 0; animation-delay: {i * 100}ms;"
				>
					<div class="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-5 group-hover:bg-primary/20 transition-colors">
						<svelte:component this={value.icon} size={24} class="text-primary" />
					</div>
					<h3 class="text-lg lg:text-xl font-semibold text-black mb-3">{value.title}</h3>
					<p class="text-sm lg:text-base text-muted leading-relaxed">{value.description}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- Key Features -->
<section class="py-16 lg:py-24 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-10 lg:mb-12">
			<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-4">Why Choose PeelJobs?</h2>
			<p class="text-base lg:text-lg text-muted max-w-3xl mx-auto">
				We're more than just a job board—we're your partner in building successful careers and teams
			</p>
		</div>

		<div class="grid md:grid-cols-3 gap-6 lg:gap-8">
			{#each features as feature, i}
				<div
					class="bg-surface rounded-lg p-6 lg:p-8 border border-border hover:border-primary/30 hover:bg-primary/10 transition-all animate-fade-in-up"
					style="opacity: 0; animation-delay: {i * 100}ms;"
				>
					<div class="w-14 h-14 bg-primary rounded-lg flex items-center justify-center mb-5 shadow-sm">
						<svelte:component this={feature.icon} size={28} class="text-white" />
					</div>
					<h3 class="text-lg lg:text-xl font-semibold text-black mb-3">{feature.title}</h3>
					<p class="text-sm lg:text-base text-muted leading-relaxed">{feature.description}</p>
				</div>
			{/each}
		</div>
	</div>
</section>

<!-- How We Deliver Value -->
<section class="py-16 lg:py-24 bg-surface">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="text-center mb-10 lg:mb-12">
			<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-4">How We Deliver Value</h2>
			<p class="text-base lg:text-lg text-muted max-w-3xl mx-auto">
				Concrete benefits for both job seekers and companies
			</p>
		</div>

		<div class="grid md:grid-cols-2 gap-6 lg:gap-8">
			<!-- For Job Seekers -->
			<div class="bg-white rounded-lg p-6 lg:p-8 shadow-sm hover:shadow-lg transition-all border border-border">
				<div class="flex items-center gap-4 mb-6">
					<div class="w-12 h-12 bg-success-light rounded-xl flex items-center justify-center">
						<Users size={24} class="text-success" />
					</div>
					<h3 class="text-xl lg:text-2xl font-semibold text-black">For Job Seekers</h3>
				</div>
				<ul class="space-y-4">
					{#each benefits.jobSeekers as benefit}
						<li class="flex items-start gap-3">
							<div class="w-5 h-5 rounded-full bg-success-light flex items-center justify-center flex-shrink-0 mt-0.5">
								<CheckCircle2 size={14} class="text-success" />
							</div>
							<span class="text-sm lg:text-base text-muted">{benefit}</span>
						</li>
					{/each}
				</ul>
			</div>

			<!-- For Companies -->
			<div class="bg-white rounded-lg p-6 lg:p-8 shadow-sm hover:shadow-lg transition-all border border-border">
				<div class="flex items-center gap-4 mb-6">
					<div class="w-12 h-12 bg-primary/20 rounded-xl flex items-center justify-center">
						<Building2 size={24} class="text-primary" />
					</div>
					<h3 class="text-xl lg:text-2xl font-semibold text-black">For Companies</h3>
				</div>
				<ul class="space-y-4">
					{#each benefits.companies as benefit}
						<li class="flex items-start gap-3">
							<div class="w-5 h-5 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
								<CheckCircle2 size={14} class="text-primary" />
							</div>
							<span class="text-sm lg:text-base text-muted">{benefit}</span>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	</div>
</section>

<!-- Our Commitment -->
<section class="py-16 lg:py-24 bg-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8">
		<div class="bg-surface rounded-lg p-8 lg:p-12 border border-border text-center max-w-4xl mx-auto">
			<div class="w-14 h-14 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
				<Heart size={28} class="text-primary" />
			</div>
			<h2 class="text-2xl lg:text-3xl font-semibold text-black tracking-tight mb-4">Our Commitment</h2>
			<p class="text-base lg:text-lg text-muted leading-relaxed mb-6">
				By fostering transparent and collaborative connections, we aim to transform the recruitment
				landscape, making it more equitable, opportunity-driven, and effective for all stakeholders.
			</p>
			<p class="text-sm lg:text-base text-muted italic">
				We measure our success not just in numbers, but in the meaningful careers launched and the
				successful teams built on our platform.
			</p>
		</div>
	</div>
</section>

<!-- Call to Action -->
<section class="py-16 lg:py-24 bg-[#1D2226] text-white">
	<div class="max-w-7xl mx-auto px-4 lg:px-8 text-center">
		<div class="max-w-3xl mx-auto">
			<h2 class="text-2xl lg:text-3xl font-semibold tracking-tight mb-4">
				Ready to Experience the PeelJobs Difference?
			</h2>
			<p class="text-base lg:text-lg text-gray-300 mb-8 lg:mb-10">
				Join thousands of job seekers and companies who have discovered a better way to connect.
				It's completely free, always will be.
			</p>
			<div class="flex flex-col sm:flex-row gap-4 justify-center">
				<a
					href="/jobs/"
					class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white text-black font-medium rounded-full hover:bg-gray-100 transition-colors shadow-sm"
				>
					Browse Jobs
					<ArrowRight size={18} />
				</a>
				<a
					href="/contact/"
					class="inline-flex items-center justify-center gap-2 px-8 py-4 bg-white/10 text-white font-medium rounded-full hover:bg-white/20 transition-colors border border-white/20"
				>
					Get in Touch
				</a>
			</div>
		</div>
	</div>
</section>
