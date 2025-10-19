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
		Search
	} from '@lucide/svelte';

	const features = [
		{
			icon: Briefcase,
			title: 'For Job Seekers',
			description:
				'Fast and better way to find jobs according to location, skills, qualifications, and experience. Completely free application process.',
			color: 'blue'
		},
		{
			icon: Users,
			title: 'For Recruiters',
			description:
				'Access to a large, continuously refreshed candidate database including Indians, US citizens, Green card holders, and H1B work permit holders.',
			color: 'green'
		},
		{
			icon: Building2,
			title: 'For Agencies',
			description:
				'Integrated technology that reduces over 99% of sourcing time for staffing agencies with multiple recruiters.',
			color: 'purple'
		}
	];

	const industries = [
		{ name: 'Finance', subtitle: '& Accounts' },
		{ name: 'IT', subtitle: '& ITES' },
		{ name: 'Pharma', subtitle: '& Healthcare' },
		{ name: 'Marketing', subtitle: '& Sales' },
		{ name: 'Manufacturing', subtitle: '& Production' },
		{ name: 'Many More', subtitle: 'Sectors' }
	];

	const values = [
		{
			icon: Search,
			title: 'Information Source',
			description: 'Your source for employment information and inspiration'
		},
		{
			icon: TrendingUp,
			title: 'Career Management',
			description: 'The place to manage your career effectively'
		},
		{
			icon: Award,
			title: 'Success Pathway',
			description: 'Your pathway to career success and growth'
		},
		{
			icon: Lightbulb,
			title: 'Professional Tools',
			description: 'Tools to help job seekers and career professionals'
		}
	];

	const stats = [
		{
			number: '10,000+',
			label: 'Active Jobs',
			icon: Briefcase
		},
		{
			number: '50,000+',
			label: 'Job Seekers',
			icon: Users
		},
		{
			number: '5,000+',
			label: 'Companies',
			icon: Building2
		},
		{
			number: '99%',
			label: 'Time Saved',
			icon: Clock
		}
	];

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
	<title>About Us - PeelJobs</title>
	<meta
		name="description"
		content="Online Jobs and Career site in India to build bright career. Read more about PeelJobs - connecting talent with opportunity across diverse industries."
	/>
	<link rel="canonical" href="https://peeljobs.com/about" />
</svelte:head>

<!-- Hero Section -->
<div class="bg-blue-50 py-12 md:py-16">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<!-- Breadcrumb -->
		<nav class="mb-6 md:mb-8" aria-label="Breadcrumb">
			<ol class="flex items-center space-x-2 text-sm text-gray-600">
				<li>
					<a href="/" class="hover:text-blue-600 transition-colors duration-200"> Home </a>
				</li>
				<li class="flex items-center">
					<ChevronRight class="w-4 h-4 mx-1 md:mx-2 text-gray-400" />
					<span class="text-gray-900 font-medium">About Us</span>
				</li>
			</ol>
		</nav>

		<!-- Hero Content -->
		<div class="text-center">
			<h1 class="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 md:mb-6">
				About <span class="text-blue-600">PeelJobs</span>
			</h1>
			<p class="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed px-4">
				Your trusted partner in connecting talent with opportunity. We're revolutionizing the job
				search experience for both candidates and employers.
			</p>
		</div>
	</div>
</div>

<!-- Stats Section -->
<div class="bg-white py-8 md:py-12 border-b border-gray-100">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-8">
			{#each stats as stat}
				<div class="text-center p-4 md:p-6 bg-gray-50 rounded-lg">
					<div
						class="inline-flex items-center justify-center w-10 h-10 md:w-12 md:h-12 bg-blue-100 rounded-full mb-3"
					>
						<svelte:component this={stat.icon} class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
					</div>
					<div class="text-2xl md:text-3xl font-bold text-gray-900 mb-1">{stat.number}</div>
					<div class="text-xs md:text-sm text-gray-600">{stat.label}</div>
				</div>
			{/each}
		</div>
	</div>
</div>

<!-- Main Content -->
<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
	<!-- Mission Statement Card -->
	<div class="bg-white rounded-xl shadow-lg p-6 md:p-8 mb-12 border border-gray-100">
		<div class="text-center mb-6 md:mb-8">
			<div
				class="inline-flex items-center justify-center w-14 h-14 md:w-16 md:h-16 bg-blue-100 rounded-full mb-4"
			>
				<Zap class="w-7 h-7 md:w-8 md:h-8 text-blue-600" />
			</div>
			<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-4">Our Mission</h2>
		</div>

		<div class="prose prose-lg max-w-none text-gray-600 leading-relaxed space-y-6">
			<blockquote
				class="text-center text-lg md:text-xl font-medium text-gray-700 mb-6 md:mb-8 border-l-4 border-blue-600 pl-4 md:pl-6 py-2 bg-blue-50 rounded"
			>
				"What you want is what you get at the right time with right information at the right place"
			</blockquote>

			<div class="grid md:grid-cols-2 gap-6 md:gap-8">
				<div class="space-y-4">
					<p class="text-base md:text-lg">
						<CheckCircle2 class="w-5 h-5 text-green-600 inline-block mr-2 mb-1" />
						Peeljobs.com is one of the leading job boards today, attracting thousands of job seekers
						every month searching through hundreds of live job opportunities. We serve as the bridge
						between talented professionals and leading companies across various industries.
					</p>

					<p class="text-base md:text-lg">
						<Heart class="w-5 h-5 text-red-500 inline-block mr-2 mb-1" />
						Our platform caters to both IT and non-IT sectors, helping companies find the perfect candidates
						while assisting professionals in discovering their ideal career opportunities. We're proud
						to help thousands of tech professionals find meaningful employment every day.
					</p>
				</div>

				<div class="space-y-4">
					<p class="text-base md:text-lg">
						<Clock class="w-5 h-5 text-blue-600 inline-block mr-2 mb-1" />
						As a comprehensive online job portal, Peeljobs.com provides a one-stop platform for all
						job market participants. Whether you're a job seeker, recruiter, or employer, our user-friendly
						interface makes your search effortless and simple.
					</p>

					<p class="text-base md:text-lg">
						<TrendingUp class="w-5 h-5 text-purple-600 inline-block mr-2 mb-1" />
						We continuously work on improving job coverage and result relevance to meet the ever-changing
						needs of our users. Every visitor to our platform is assured of finding their perfect match.
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Features Grid -->
	<div class="grid md:grid-cols-3 gap-6 md:gap-8 mb-12 md:mb-16">
		{#each features as feature}
			<div class="rounded-xl p-6 border {getColorClasses(feature.color)}">
				<div class="w-12 h-12 {getIconBgColor(feature.color)} rounded-lg flex items-center justify-center mb-4">
					<svelte:component this={feature.icon} class="w-6 h-6 text-white" />
				</div>
				<h3 class="text-lg md:text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
				<p class="text-sm md:text-base text-gray-600 leading-relaxed">{feature.description}</p>
			</div>
		{/each}
	</div>

	<!-- Industry Coverage -->
	<div class="bg-gray-50 rounded-xl p-6 md:p-8 mb-12">
		<h2 class="text-2xl md:text-3xl font-bold text-center text-gray-900 mb-6 md:mb-8">
			Industry Coverage
		</h2>
		<p class="text-center text-gray-600 mb-6 md:mb-8 max-w-3xl mx-auto text-sm md:text-base">
			We provide the perfect platform for candidates from diverse backgrounds to seize the best job
			opportunities by screening through our vast database of available positions.
		</p>

		<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
			{#each industries as industry}
				<div
					class="bg-white rounded-lg p-3 md:p-4 text-center shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
				>
					<div class="text-sm md:text-base text-blue-600 font-semibold">{industry.name}</div>
					<div class="text-xs md:text-sm text-gray-500">{industry.subtitle}</div>
				</div>
			{/each}
		</div>
	</div>

	<!-- What Makes Us Special -->
	<div class="text-center mb-12">
		<h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6 md:mb-8">
			In Short, PeelJobs.com is...
		</h2>

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6">
			{#each values as value}
				<div
					class="bg-white rounded-lg p-4 md:p-6 shadow-md border border-gray-100 hover:shadow-lg transition-shadow"
				>
					<div
						class="w-10 h-10 md:w-12 md:h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3 md:mb-4"
					>
						<svelte:component this={value.icon} class="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
					</div>
					<h3 class="text-sm md:text-base font-semibold text-gray-900 mb-2">{value.title}</h3>
					<p class="text-xs md:text-sm text-gray-600">{value.description}</p>
				</div>
			{/each}
		</div>
	</div>

	<!-- Call to Action -->
	<div class="bg-blue-600 rounded-xl p-6 md:p-8 text-center text-white">
		<h2 class="text-xl md:text-2xl font-bold mb-3 md:mb-4">
			Ready to Find Your Next Opportunity?
		</h2>
		<p class="text-sm md:text-base text-blue-100 mb-4 md:mb-6 max-w-2xl mx-auto">
			Peeljobs.com is the fastest online recruitment platform that attracts a huge number of job
			seekers, generating tremendous applications. Join thousands of professionals who have found
			their dream jobs through our platform.
		</p>
		<div class="flex flex-col sm:flex-row gap-3 md:gap-4 justify-center">
			<a
				href="/jobs"
				class="inline-block bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 text-sm md:text-base"
			>
				Browse Jobs
			</a>
			<a
				href="/contact"
				class="inline-block bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-800 transition-colors duration-200 text-sm md:text-base"
			>
				Contact Us
			</a>
		</div>
	</div>
</div>
