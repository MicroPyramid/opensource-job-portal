<script lang="ts">
	import {
		Download,
		Mail,
		MapPin,
		Calendar,
		ExternalLink,
		Award,
		Briefcase,
		GraduationCap,
		Github,
		X
	} from '@lucide/svelte';
	import { Linkedin, Twitter } from '@lucide/svelte';
	import type { PageData } from './$types';

	interface SocialLinks {
		github?: string;
		linkedin?: string;
		twitter?: string;
	}

	interface ExperienceItem {
		title: string;
		company: string;
		location: string;
		duration: string;
		description: string;
	}

	interface EducationItem {
		degree: string;
		institution: string;
		year: string;
		gpa?: string;
		certification?: string;
	}

	interface Profile {
		name: string;
		title: string;
		location: string;
		profileImage: string;
		bio: string;
		email: string;
		joinDate: string;
		isContactEnabled: boolean;
		isResumePublic: boolean;
		resumeUrl: string;
		socialLinks: SocialLinks;
		skills: string[];
		experience: ExperienceItem[];
		education: EducationItem[];
	}

	const _: { data: PageData } = $props();
	void _;

	// Mock data - replace with actual data from your backend
	const profile: Profile = {
		name: 'Sarah Johnson',
		title: 'Senior Frontend Developer',
		location: 'San Francisco, CA',
		profileImage: '/api/placeholder/200/200',
		bio: "Passionate frontend developer with 5+ years of experience building scalable web applications using React, Vue, and Svelte. I love creating intuitive user experiences and writing clean, maintainable code.",
		email: 'sarah.johnson@email.com',
		joinDate: 'March 2024',
		isContactEnabled: true,
		isResumePublic: true,
		resumeUrl: '/resumes/sarah-johnson-resume.pdf',
		socialLinks: {
			github: 'https://github.com/sarahjohnson',
			linkedin: 'https://linkedin.com/in/sarahjohnson',
			twitter: 'https://twitter.com/sarahjohnson'
		},
		skills: [
			'JavaScript',
			'TypeScript',
			'React',
			'Vue.js',
			'Svelte',
			'Node.js',
			'HTML5',
			'CSS3',
			'Tailwind CSS',
			'Git',
			'Docker',
			'AWS'
		],
		experience: [
			{
				title: 'Senior Frontend Developer',
				company: 'TechCorp Inc.',
				location: 'San Francisco, CA',
				duration: 'Jan 2022 - Present',
				description:
					'Lead frontend development for enterprise SaaS platform serving 10k+ users. Implemented modern React architecture and improved performance by 40%.'
			},
			{
				title: 'Frontend Developer',
				company: 'StartupXYZ',
				location: 'Remote',
				duration: 'Jun 2020 - Dec 2021',
				description:
					'Built responsive web applications using Vue.js and Node.js. Collaborated with design team to implement pixel-perfect UI components.'
			},
			{
				title: 'Junior Web Developer',
				company: 'Digital Agency',
				location: 'San Francisco, CA',
				duration: 'Aug 2019 - May 2020',
				description:
					'Developed custom WordPress themes and plugins. Maintained multiple client websites and improved site performance.'
			}
		],
		education: [
			{
				degree: 'Bachelor of Science in Computer Science',
				institution: 'University of California, Berkeley',
				year: '2019',
				gpa: '3.8/4.0'
			},
			{
				degree: 'Full Stack Web Development Bootcamp',
				institution: 'Tech Academy',
				year: '2019',
				certification: 'Certificate of Completion'
			}
		]
	};

	let showContactModal = $state(false);
	let contactMessage = $state('');
	let contactSubject = $state('');

	function openContactModal(): void {
		showContactModal = true;
	}

	function closeContactModal(): void {
		showContactModal = false;
		contactMessage = '';
		contactSubject = '';
	}

	function sendMessage(): void {
		// Handle message sending logic here
		console.log('Sending message:', { subject: contactSubject, message: contactMessage });
		closeContactModal();
	}

	function downloadResume(): void {
		window.open(profile.resumeUrl, '_blank');
	}

	function openSocialLink(url?: string): void {
		if (!url) {
			return;
		}
		window.open(url, '_blank', 'noopener,noreferrer');
	}
</script>

<svelte:head>
	<title>{profile.name} - {profile.title} | PeelJobs</title>
	<meta name="description" content="{profile.name} - {profile.title}. {profile.bio}" />
</svelte:head>

<div class="min-h-screen bg-surface-50">
	<!-- Hero Section -->
	<section class="relative bg-gray-900 text-white py-12 lg:py-16 overflow-hidden">
		<!-- Decorative elements -->
		<div class="absolute top-0 right-0 w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
		<div class="absolute bottom-0 left-0 w-64 h-64 bg-primary-500/10 rounded-full blur-2xl"></div>

		<div class="container mx-auto px-4 lg:px-6 max-w-4xl relative z-10">
			<div
				class="flex flex-col md:flex-row items-center md:items-start gap-6 animate-fade-in-up"
				style="opacity: 0;"
			>
				<!-- Profile Image -->
				<div class="flex-shrink-0">
					<img
						src={profile.profileImage}
						alt="{profile.name}'s profile picture"
						class="w-28 h-28 lg:w-32 lg:h-32 rounded-2xl object-cover border-4 border-white/20"
					/>
				</div>

				<!-- Profile Info -->
				<div class="flex-1 text-center md:text-left">
					<h1 class="text-2xl lg:text-3xl font-bold mb-1" role="banner">
						{profile.name}
					</h1>
					<h2 class="text-lg lg:text-xl text-primary-300 font-medium mb-4">
						{profile.title}
					</h2>

					<div class="flex flex-wrap items-center justify-center md:justify-start gap-4 text-gray-300 text-sm mb-4">
						<div class="flex items-center gap-1.5" aria-label="Location">
							<MapPin size={16} class="text-gray-400" />
							<span>{profile.location}</span>
						</div>
						<div class="flex items-center gap-1.5" aria-label="Join date">
							<Calendar size={16} class="text-gray-400" />
							<span>Joined {profile.joinDate}</span>
						</div>
					</div>

					<!-- Social Links -->
					{#if profile.socialLinks && (profile.socialLinks.github || profile.socialLinks.linkedin || profile.socialLinks.twitter)}
						<div class="flex items-center justify-center md:justify-start gap-2 mb-4">
							{#if profile.socialLinks.github}
								<button
									type="button"
									onclick={() => openSocialLink(profile.socialLinks.github)}
									class="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-gray-300 hover:bg-white/20 hover:text-white transition-colors"
									aria-label="Visit {profile.name}'s GitHub profile"
								>
									<Github size={18} />
								</button>
							{/if}

							{#if profile.socialLinks.linkedin}
								<button
									type="button"
									onclick={() => openSocialLink(profile.socialLinks.linkedin)}
									class="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-gray-300 hover:bg-white/20 hover:text-white transition-colors"
									aria-label="Visit {profile.name}'s LinkedIn profile"
								>
									<Linkedin size={18} />
								</button>
							{/if}

							{#if profile.socialLinks.twitter}
								<button
									type="button"
									onclick={() => openSocialLink(profile.socialLinks.twitter)}
									class="w-9 h-9 rounded-xl bg-white/10 flex items-center justify-center text-gray-300 hover:bg-white/20 hover:text-white transition-colors"
									aria-label="Visit {profile.name}'s Twitter profile"
								>
									<Twitter size={18} />
								</button>
							{/if}
						</div>
					{/if}

					<!-- Action Buttons -->
					<div class="flex flex-wrap items-center justify-center md:justify-start gap-3">
						{#if profile.isContactEnabled}
							<button
								type="button"
								onclick={openContactModal}
								class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1"
								aria-label="Contact {profile.name}"
							>
								<Mail size={16} />
								Contact
							</button>
						{/if}

						{#if profile.isResumePublic}
							<button
								type="button"
								onclick={downloadResume}
								class="inline-flex items-center gap-2 px-5 py-2.5 bg-white/10 text-white rounded-full font-medium hover:bg-white/20 transition-colors"
								aria-label="Download {profile.name}'s resume"
							>
								<Download size={16} />
								Resume
							</button>
						{/if}
					</div>
				</div>
			</div>
		</div>
	</section>

	<!-- Main Content -->
	<section class="py-8 lg:py-12">
		<div class="container mx-auto px-4 lg:px-6 max-w-4xl">
			<!-- Bio Section -->
			<div
				class="bg-white rounded-2xl p-5 lg:p-6 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
				style="opacity: 0; animation-delay: 100ms;"
			>
				<p class="text-gray-700 leading-relaxed">
					{profile.bio}
				</p>
			</div>

			<!-- Skills Section -->
			<div
				class="bg-white rounded-2xl p-5 lg:p-6 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
				style="opacity: 0; animation-delay: 150ms;"
			>
				<div class="flex items-center gap-3 mb-4">
					<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
						<Award size={20} class="text-primary-600" />
					</div>
					<h3 class="text-lg font-semibold text-gray-900">Skills</h3>
				</div>
				<div class="flex flex-wrap gap-2" role="list" aria-label="Skills">
					{#each profile.skills as skill}
						<span
							class="px-3 py-1.5 bg-primary-50 text-primary-700 rounded-full text-sm font-medium"
							role="listitem"
						>
							{skill}
						</span>
					{/each}
				</div>
			</div>

			<!-- Experience Section -->
			<div
				class="bg-white rounded-2xl p-5 lg:p-6 elevation-1 border border-gray-100 mb-6 animate-fade-in-up"
				style="opacity: 0; animation-delay: 200ms;"
			>
				<div class="flex items-center gap-3 mb-6">
					<div class="w-10 h-10 rounded-xl bg-primary-50 flex items-center justify-center">
						<Briefcase size={20} class="text-primary-600" />
					</div>
					<h3 class="text-lg font-semibold text-gray-900">Experience</h3>
				</div>
				<div class="space-y-6" role="list" aria-label="Work experience">
					{#each profile.experience as job, i}
						<div class="relative pl-6" role="listitem">
							<!-- Timeline -->
							<div class="absolute left-0 top-2 w-2 h-2 rounded-full bg-primary-600"></div>
							{#if i < profile.experience.length - 1}
								<div class="absolute left-[3px] top-4 w-0.5 h-full bg-gray-200"></div>
							{/if}

							<div class="pb-2">
								<h4 class="text-base font-semibold text-gray-900">{job.title}</h4>
								<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-gray-600 mt-1 mb-2">
									<span class="font-medium text-gray-700">{job.company}</span>
									<span class="text-gray-300">•</span>
									<span>{job.location}</span>
									<span class="text-gray-300">•</span>
									<span class="text-gray-500">{job.duration}</span>
								</div>
								<p class="text-sm text-gray-600 leading-relaxed">{job.description}</p>
							</div>
						</div>
					{/each}
				</div>
			</div>

			<!-- Education Section -->
			<div
				class="bg-white rounded-2xl p-5 lg:p-6 elevation-1 border border-gray-100 animate-fade-in-up"
				style="opacity: 0; animation-delay: 250ms;"
			>
				<div class="flex items-center gap-3 mb-6">
					<div class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center">
						<GraduationCap size={20} class="text-green-600" />
					</div>
					<h3 class="text-lg font-semibold text-gray-900">Education</h3>
				</div>
				<div class="space-y-6" role="list" aria-label="Education">
					{#each profile.education as edu, i}
						<div class="relative pl-6" role="listitem">
							<!-- Timeline -->
							<div class="absolute left-0 top-2 w-2 h-2 rounded-full bg-green-600"></div>
							{#if i < profile.education.length - 1}
								<div class="absolute left-[3px] top-4 w-0.5 h-full bg-gray-200"></div>
							{/if}

							<div class="pb-2">
								<h4 class="text-base font-semibold text-gray-900">{edu.degree}</h4>
								<div class="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-gray-600 mt-1">
									<span class="font-medium text-gray-700">{edu.institution}</span>
									<span class="text-gray-300">•</span>
									<span>{edu.year}</span>
									{#if edu.gpa}
										<span class="text-gray-300">•</span>
										<span>GPA: {edu.gpa}</span>
									{/if}
								</div>
								{#if edu.certification}
									<p class="text-sm text-green-600 mt-1 font-medium">{edu.certification}</p>
								{/if}
							</div>
						</div>
					{/each}
				</div>
			</div>
		</div>
	</section>
</div>

<!-- Contact Modal -->
{#if showContactModal}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4">
		<button
			type="button"
			class="absolute inset-0 bg-gray-900/60 backdrop-blur-sm cursor-default"
			onclick={closeContactModal}
			onkeydown={(event) => {
				if (event.key === 'Escape') {
					event.preventDefault();
					closeContactModal();
				}
			}}
			aria-label="Close contact modal"
		></button>
		<div
			class="relative bg-white rounded-2xl elevation-3 max-w-md w-full animate-fade-in-up"
			style="opacity: 0;"
			role="dialog"
			aria-labelledby="contact-modal-title"
			aria-modal="true"
		>
			<!-- Modal Header -->
			<div class="flex items-center justify-between p-5 lg:p-6 border-b border-gray-100">
				<h4 id="contact-modal-title" class="text-xl font-semibold text-gray-900">
					Contact {profile.name}
				</h4>
				<button
					type="button"
					onclick={closeContactModal}
					class="w-10 h-10 rounded-xl flex items-center justify-center text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors"
				>
					<X size={20} />
				</button>
			</div>

			<form
				onsubmit={(e) => {
					e.preventDefault();
					sendMessage();
				}}
				class="p-5 lg:p-6"
			>
				<div class="space-y-4">
					<div>
						<label for="contact-subject" class="block text-sm font-medium text-gray-700 mb-2">
							Subject
						</label>
						<input
							id="contact-subject"
							type="text"
							bind:value={contactSubject}
							class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
							placeholder="Job Opportunity"
							required
						/>
					</div>

					<div>
						<label for="contact-message" class="block text-sm font-medium text-gray-700 mb-2">
							Message
						</label>
						<textarea
							id="contact-message"
							bind:value={contactMessage}
							rows="4"
							class="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors resize-none"
							placeholder="Hi {profile.name.split(' ')[0]}, I came across your profile and would like to discuss a potential opportunity..."
							required
						></textarea>
					</div>
				</div>

				<div class="flex justify-end gap-3 mt-6">
					<button
						type="button"
						onclick={closeContactModal}
						class="px-5 py-2.5 border border-gray-200 text-gray-700 hover:bg-gray-50 font-medium rounded-full transition-colors"
					>
						Cancel
					</button>
					<button
						type="submit"
						class="inline-flex items-center gap-2 px-5 py-2.5 bg-primary-600 text-white rounded-full font-medium hover:bg-primary-700 transition-colors elevation-1"
					>
						<Mail size={16} />
						Send Message
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
