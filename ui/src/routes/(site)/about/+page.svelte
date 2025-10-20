<script lang="ts">
	import {
		Zap,
		Briefcase,
		Users,
		Building2,
		Target,
		TrendingUp,
		Shield,
		Award,
		Clock,
		CheckCircle2,
		ChevronRight,
		Heart,
		DollarSign,
		Lightbulb,
		Search,
		Globe,
		Rocket,
		Star
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
			description: 'Zero cost for both job posting and candidate access. No hidden fees, no paywalls—just free, accessible hiring for everyone.',
			color: 'blue'
		},
		{
			icon: Zap,
			title: 'Fast & Efficient',
			description: 'Streamlined recruitment process with intuitive tools, intelligent search, and automated workflows that save hours of work.',
			color: 'green'
		},
		{
			icon: Target,
			title: 'Smart Matching',
			description: 'Advanced filters and AI-powered recommendations help you find the perfect match faster.',
			color: 'purple'
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


	function getColorClasses(color: string) {
		const colors = {
			blue: 'bg-blue-50 border-blue-200',
			green: 'bg-green-50 border-green-200',
			purple: 'bg-purple-50 border-purple-200'
		};
		return colors[color as keyof typeof colors] || colors.blue;
	}

	function getIconBgColor(color: string) {
		const colors = {
			blue: 'bg-blue-600',
			green: 'bg-green-600',
			purple: 'bg-purple-600'
		};
		return colors[color as keyof typeof colors] || colors.blue;
	}
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
<div class="bg-blue-600 text-white py-12 md:py-20">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Breadcrumb -->
		<nav class="mb-6 md:mb-8" aria-label="Breadcrumb">
			<ol class="flex items-center space-x-2 text-sm text-blue-100">
				<li>
					<a href="/" class="hover:text-white transition-colors duration-200"> Home </a>
				</li>
				<li class="flex items-center">
					<ChevronRight class="w-4 h-4 mx-1 md:mx-2" />
					<span class="text-white font-medium">About Us</span>
				</li>
			</ol>
		</nav>

		<!-- Hero Content -->
		<div class="text-center">
			<div class="inline-flex items-center justify-center w-16 h-16 md:w-20 md:h-20 bg-white/10 rounded-full mb-6">
				<Rocket class="w-8 h-8 md:w-10 md:h-10" />
			</div>
			<h1 class="text-3xl md:text-5xl lg:text-6xl font-bold mb-4 md:mb-6">
				Democratizing Hiring,<br class="hidden md:block" />
				One Connection at a Time
			</h1>
			<p class="text-lg md:text-xl text-blue-100 max-w-3xl mx-auto leading-relaxed">
				We're on a mission to make exceptional hiring accessible to every organization,
				regardless of size or budget, while empowering job seekers to find meaningful careers.
			</p>
		</div>
	</div>
</div>

<!-- Main Content -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">

	<!-- Vision & Mission -->
	<section class="mb-12 md:mb-16">
		<div class="grid md:grid-cols-2 gap-6 md:gap-8">
			<!-- Vision -->
			<div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
				<div class="flex items-center gap-3 mb-4">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<Globe class="w-6 h-6 text-blue-600" />
					</div>
					<h2 class="text-2xl md:text-3xl font-bold text-gray-900">Our Vision</h2>
				</div>
				<p class="text-base md:text-lg text-gray-700 leading-relaxed">
					To become the leading free job portal that transforms how companies and talent connect,
					building a future where exceptional hiring is accessible to every organization, regardless
					of size or budget.
				</p>
			</div>

			<!-- Aim -->
			<div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
				<div class="flex items-center gap-3 mb-4">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<Target class="w-6 h-6 text-green-600" />
					</div>
					<h2 class="text-2xl md:text-3xl font-bold text-gray-900">Our Aim</h2>
				</div>
				<p class="text-base md:text-lg text-gray-700 leading-relaxed">
					To create a dynamic platform that empowers companies to connect with exceptional talent
					at no cost, fostering opportunities for meaningful employment and driving organizational
					growth through accessible, equitable, and efficient hiring.
				</p>
			</div>
		</div>
	</section>

	<!-- Mission Statement -->
	<section class="bg-blue-50 rounded-xl p-6 md:p-8 mb-12 md:mb-16 border border-blue-100">
		<div class="text-center mb-6 md:mb-8">
			<div class="inline-flex items-center justify-center w-14 h-14 md:w-16 md:h-16 bg-blue-100 rounded-full mb-4">
				<Zap class="w-7 h-7 md:w-8 md:h-8 text-blue-600" />
			</div>
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-3">Our Mission</h2>
			<p class="text-base md:text-lg text-gray-700 max-w-3xl mx-auto">
				We democratize the hiring process by providing a free, user-friendly job portal that
				bridges the gap between companies and talented individuals.
			</p>
		</div>

		<div class="grid md:grid-cols-2 lg:grid-cols-5 gap-4 md:gap-6">
			<div class="bg-white rounded-lg p-4 md:p-6 shadow-sm">
				<div class="flex items-center gap-2 mb-3">
					<DollarSign class="w-5 h-5 text-green-600" />
					<h3 class="font-semibold text-gray-900">Accessibility</h3>
				</div>
				<p class="text-sm text-gray-700">
					Cost-free platform ensuring businesses of all sizes can access top-tier talent without
					financial barriers.
				</p>
			</div>

			<div class="bg-white rounded-lg p-4 md:p-6 shadow-sm">
				<div class="flex items-center gap-2 mb-3">
					<Zap class="w-5 h-5 text-yellow-600" />
					<h3 class="font-semibold text-gray-900">Efficiency</h3>
				</div>
				<p class="text-sm text-gray-700">
					Streamlined recruitment with intuitive tools enabling faster and more effective hiring
					decisions.
				</p>
			</div>

			<div class="bg-white rounded-lg p-4 md:p-6 shadow-sm">
				<div class="flex items-center gap-2 mb-3">
					<Users class="w-5 h-5 text-purple-600" />
					<h3 class="font-semibold text-gray-900">Empowerment</h3>
				</div>
				<p class="text-sm text-gray-700">
					Supporting job seekers with equal access to opportunities and helping companies build
					strong teams.
				</p>
			</div>

			<div class="bg-white rounded-lg p-4 md:p-6 shadow-sm">
				<div class="flex items-center gap-2 mb-3">
					<Lightbulb class="w-5 h-5 text-blue-600" />
					<h3 class="font-semibold text-gray-900">Innovation</h3>
				</div>
				<p class="text-sm text-gray-700">
					Continuously enhancing our platform with cutting-edge features to meet evolving job
					market needs.
				</p>
			</div>

			<div class="bg-white rounded-lg p-4 md:p-6 shadow-sm">
				<div class="flex items-center gap-2 mb-3">
					<Shield class="w-5 h-5 text-red-600" />
					<h3 class="font-semibold text-gray-900">Quality & Trust</h3>
				</div>
				<p class="text-sm text-gray-700">
					Maintaining high standards with verified profiles, authentic listings, and transparent
					communication.
				</p>
			</div>
		</div>
	</section>

	<!-- Core Values -->
	<section class="mb-12 md:mb-16">
		<div class="text-center mb-8 md:mb-12">
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-3">Our Core Values</h2>
			<p class="text-base md:text-lg text-gray-600 max-w-3xl mx-auto">
				These fundamental principles guide everything we do at PeelJobs
			</p>
		</div>

		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each coreValues as value}
				<div class="bg-white rounded-xl p-6 shadow-lg border border-gray-100 hover:shadow-xl transition-shadow">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
						<svelte:component this={value.icon} class="w-6 h-6 text-blue-600" />
					</div>
					<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3">{value.title}</h3>
					<p class="text-sm md:text-base text-gray-600 leading-relaxed">{value.description}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- Key Features -->
	<section class="mb-12 md:mb-16">
		<div class="text-center mb-8 md:mb-12">
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-3">Why Choose PeelJobs?</h2>
			<p class="text-base md:text-lg text-gray-600 max-w-3xl mx-auto">
				We're more than just a job board—we're your partner in building successful careers and teams
			</p>
		</div>

		<div class="grid md:grid-cols-3 gap-6 md:gap-8">
			{#each features as feature}
				<div class="rounded-xl p-6 md:p-8 border {getColorClasses(feature.color)} hover:shadow-lg transition-shadow">
					<div class="w-14 h-14 {getIconBgColor(feature.color)} rounded-xl flex items-center justify-center mb-4">
						<svelte:component this={feature.icon} class="w-7 h-7 text-white" />
					</div>
					<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
					<p class="text-sm md:text-base text-gray-700 leading-relaxed">{feature.description}</p>
				</div>
			{/each}
		</div>
	</section>

	<!-- How We Deliver -->
	<section class="mb-12 md:mb-16">
		<div class="text-center mb-8 md:mb-12">
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-3">How We Deliver Value</h2>
			<p class="text-base md:text-lg text-gray-600 max-w-3xl mx-auto">
				Concrete benefits for both job seekers and companies
			</p>
		</div>

		<div class="grid md:grid-cols-2 gap-6 md:gap-8">
			<!-- For Job Seekers -->
			<div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
						<Users class="w-6 h-6 text-green-600" />
					</div>
					<h3 class="text-xl md:text-2xl font-bold text-gray-900">For Job Seekers</h3>
				</div>
				<ul class="space-y-3">
					{#each benefits.jobSeekers as benefit}
						<li class="flex items-start gap-3">
							<CheckCircle2 class="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
							<span class="text-sm md:text-base text-gray-700">{benefit}</span>
						</li>
					{/each}
				</ul>
			</div>

			<!-- For Companies -->
			<div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
				<div class="flex items-center gap-3 mb-6">
					<div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
						<Building2 class="w-6 h-6 text-blue-600" />
					</div>
					<h3 class="text-xl md:text-2xl font-bold text-gray-900">For Companies</h3>
				</div>
				<ul class="space-y-3">
					{#each benefits.companies as benefit}
						<li class="flex items-start gap-3">
							<CheckCircle2 class="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
							<span class="text-sm md:text-base text-gray-700">{benefit}</span>
						</li>
					{/each}
				</ul>
			</div>
		</div>
	</section>

	<!-- Our Commitment -->
	<section class="bg-gray-50 rounded-xl p-6 md:p-8 mb-12 md:mb-16 border border-gray-100">
		<div class="max-w-4xl mx-auto text-center">
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">Our Commitment</h2>
			<p class="text-base md:text-lg text-gray-700 leading-relaxed mb-6">
				By fostering transparent and collaborative connections, we aim to transform the recruitment
				landscape, making it more equitable, opportunity-driven, and effective for all stakeholders.
			</p>
			<p class="text-sm md:text-base text-gray-600 italic">
				We measure our success not just in numbers, but in the meaningful careers launched and the
				successful teams built on our platform.
			</p>
		</div>
	</section>

	<!-- Call to Action -->
	<section class="bg-blue-600 rounded-xl p-8 md:p-12 text-center text-white">
		<h2 class="text-2xl md:text-3xl font-bold mb-4">
			Ready to Experience the PeelJobs Difference?
		</h2>
		<p class="text-base md:text-lg text-blue-100 mb-6 md:mb-8 max-w-2xl mx-auto">
			Join thousands of job seekers and companies who have discovered a better way to connect.
			It's completely free, always will be.
		</p>
		<div class="flex flex-col sm:flex-row gap-4 justify-center">
			<a
				href="/jobs/"
				class="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 shadow-lg"
			>
				Browse Jobs
			</a>
			<a
				href="/contact/"
				class="inline-block bg-blue-700 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-800 transition-colors duration-200 border-2 border-white/20"
			>
				Get in Touch
			</a>
		</div>
	</section>
</div>
