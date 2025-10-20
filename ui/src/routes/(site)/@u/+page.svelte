<script lang="ts">
    import { Download, Mail, MapPin, Calendar, ExternalLink, Award, Briefcase, GraduationCap, Github } from '@lucide/svelte';
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

    const { data } = $props<{ data: PageData }>();
    void data;

    // Mock data - replace with actual data from your backend
    const profile: Profile = {
        name: "Sarah Johnson",
        title: "Senior Frontend Developer",
        location: "San Francisco, CA",
        profileImage: "/api/placeholder/200/200",
        bio: "Passionate frontend developer with 5+ years of experience building scalable web applications using React, Vue, and Svelte. I love creating intuitive user experiences and writing clean, maintainable code.",
        email: "sarah.johnson@email.com",
        joinDate: "March 2024",
        isContactEnabled: true,
        isResumePublic: true,
        resumeUrl: "/resumes/sarah-johnson-resume.pdf",
        socialLinks: {
            github: "https://github.com/sarahjohnson",
            linkedin: "https://linkedin.com/in/sarahjohnson",
            twitter: "https://twitter.com/sarahjohnson"
        },
        skills: [
            "JavaScript", "TypeScript", "React", "Vue.js", "Svelte", "Node.js", 
            "HTML5", "CSS3", "Tailwind CSS", "Git", "Docker", "AWS"
        ],
        experience: [
            {
                title: "Senior Frontend Developer",
                company: "TechCorp Inc.",
                location: "San Francisco, CA",
                duration: "Jan 2022 - Present",
                description: "Lead frontend development for enterprise SaaS platform serving 10k+ users. Implemented modern React architecture and improved performance by 40%."
            },
            {
                title: "Frontend Developer",
                company: "StartupXYZ",
                location: "Remote",
                duration: "Jun 2020 - Dec 2021",
                description: "Built responsive web applications using Vue.js and Node.js. Collaborated with design team to implement pixel-perfect UI components."
            },
            {
                title: "Junior Web Developer",
                company: "Digital Agency",
                location: "San Francisco, CA",
                duration: "Aug 2019 - May 2020",
                description: "Developed custom WordPress themes and plugins. Maintained multiple client websites and improved site performance."
            }
        ],
        education: [
            {
                degree: "Bachelor of Science in Computer Science",
                institution: "University of California, Berkeley",
                year: "2019",
                gpa: "3.8/4.0"
            },
            {
                degree: "Full Stack Web Development Bootcamp",
                institution: "Tech Academy",
                year: "2019",
                certification: "Certificate of Completion"
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
    <title>{profile.name} - {profile.title} | HirePulse.in</title>
    <meta name="description" content="{profile.name} - {profile.title}. {profile.bio}" />
</svelte:head>

<div class="min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-4xl">
        <!-- Header Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex flex-col md:flex-row items-start gap-6">
                <div class="flex-shrink-0">
                    <img 
                        src={profile.profileImage} 
                        alt="{profile.name}'s profile picture"
                        class="w-32 h-32 rounded-full object-cover border-4 border-blue-100"
                    />
                </div>
                
                <div class="flex-1 min-w-0">
                    <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4">
                        <div>
                            <h1 class="text-3xl font-bold text-gray-900 mb-2" role="banner">
                                {profile.name}
                            </h1>
                            <h2 class="text-xl text-blue-600 font-medium mb-3">
                                {profile.title}
                            </h2>
                            <div class="flex flex-wrap items-center gap-4 text-gray-600 mb-4">
                                <div class="flex items-center gap-1" aria-label="Location">
                                    <MapPin size={16} />
                                    <span>{profile.location}</span>
                                </div>
                                <div class="flex items-center gap-1" aria-label="Join date">
                                    <Calendar size={16} />
                                    <span>Joined {profile.joinDate}</span>
                                </div>
                            </div>
                            
                            <!-- Social Links -->
                            {#if profile.socialLinks && (profile.socialLinks.github || profile.socialLinks.linkedin || profile.socialLinks.twitter)}
                                <div class="flex items-center gap-3 mb-4">
                                    {#if profile.socialLinks.github}
                                        <button
                                            onclick={() => openSocialLink(profile.socialLinks.github)}
                                            class="flex items-center gap-1 text-gray-600 hover:text-gray-900 transition-colors"
                                            aria-label="Visit {profile.name}'s GitHub profile"
                                        >
                                            <Github size={18} />
                                            <ExternalLink size={12} />
                                        </button>
                                    {/if}
                                    
                                    {#if profile.socialLinks.linkedin}
                                        <button
                                            onclick={() => openSocialLink(profile.socialLinks.linkedin)}
                                            class="flex items-center gap-1 text-gray-600 hover:text-blue-600 transition-colors"
                                            aria-label="Visit {profile.name}'s LinkedIn profile"
                                        >
                                            <Linkedin size={18} />
                                            <ExternalLink size={12} />
                                        </button>
                                    {/if}
                                    
                                    {#if profile.socialLinks.twitter}
                                        <button
                                            onclick={() => openSocialLink(profile.socialLinks.twitter)}
                                            class="flex items-center gap-1 text-gray-600 hover:text-sky-500 transition-colors"
                                            aria-label="Visit {profile.name}'s Twitter profile"
                                        >
                                            <Twitter size={18} />
                                            <ExternalLink size={12} />
                                        </button>
                                    {/if}
                                </div>
                            {/if}
                            
                            <p class="text-gray-700 leading-relaxed">
                                {profile.bio}
                            </p>
                        </div>
                        
                        <div class="flex flex-col sm:flex-row gap-3">
                            {#if profile.isContactEnabled}
                                <button 
                                    onclick={openContactModal}
                                    class="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                                    aria-label="Contact {profile.name}"
                                >
                                    <Mail size={16} />
                                    Contact
                                </button>
                            {/if}
                            
                            {#if profile.isResumePublic}
                                <button 
                                    onclick={downloadResume}
                                    class="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
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
        </div>

        <!-- Skills Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Award size={20} class="text-blue-600" />
                Skills
            </h3>
            <div class="flex flex-wrap gap-2" role="list" aria-label="Skills">
                {#each profile.skills as skill}
                    <span 
                        class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium"
                        role="listitem"
                    >
                        {skill}
                    </span>
                {/each}
            </div>
        </div>

        <!-- Experience Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <Briefcase size={20} class="text-blue-600" />
                Experience
            </h3>
            <div class="space-y-6" role="list" aria-label="Work experience">
                {#each profile.experience as job}
                    <div class="border-l-2 border-blue-200 pl-6 relative" role="listitem">
                        <div class="absolute w-3 h-3 bg-blue-600 rounded-full -left-2 top-1"></div>
                        <div class="mb-2">
                            <h4 class="text-lg font-semibold text-gray-900">{job.title}</h4>
                            <div class="flex flex-col sm:flex-row sm:items-center gap-2 text-gray-600">
                                <span class="font-medium">{job.company}</span>
                                <span class="hidden sm:inline">•</span>
                                <span>{job.location}</span>
                                <span class="hidden sm:inline">•</span>
                                <span>{job.duration}</span>
                            </div>
                        </div>
                        <p class="text-gray-700 leading-relaxed">{job.description}</p>
                    </div>
                {/each}
            </div>
        </div>

        <!-- Education Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 class="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <GraduationCap size={20} class="text-blue-600" />
                Education
            </h3>
            <div class="space-y-4" role="list" aria-label="Education">
                {#each profile.education as edu}
                    <div class="border-l-2 border-green-200 pl-6 relative" role="listitem">
                        <div class="absolute w-3 h-3 bg-green-600 rounded-full -left-2 top-1"></div>
                        <h4 class="text-lg font-semibold text-gray-900">{edu.degree}</h4>
                        <div class="flex flex-col sm:flex-row sm:items-center gap-2 text-gray-600">
                            <span class="font-medium">{edu.institution}</span>
                            <span class="hidden sm:inline">•</span>
                            <span>{edu.year}</span>
                            {#if edu.gpa}
                                <span class="hidden sm:inline">•</span>
                                <span>GPA: {edu.gpa}</span>
                            {/if}
                        </div>
                        {#if edu.certification}
                            <p class="text-sm text-green-600 mt-1">{edu.certification}</p>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    </div>
</div>

<!-- Contact Modal -->
{#if showContactModal}
    <div 
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
        role="dialog"
        aria-labelledby="contact-modal-title"
        aria-modal="true"
    >
        <div class="bg-white rounded-lg max-w-md w-full p-6">
            <h4 id="contact-modal-title" class="text-xl font-semibold text-gray-900 mb-4">
                Contact {profile.name}
            </h4>
            
            <form onsubmit={(e) => { e.preventDefault(); sendMessage(); }}>
                <div class="mb-4">
                    <label for="contact-subject" class="block text-sm font-medium text-gray-700 mb-2">
                        Subject
                    </label>
                    <input 
                        id="contact-subject"
                        type="text" 
                        bind:value={contactSubject}
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Job Opportunity"
                        required
                    />
                </div>
                
                <div class="mb-6">
                    <label for="contact-message" class="block text-sm font-medium text-gray-700 mb-2">
                        Message
                    </label>
                    <textarea 
                        id="contact-message"
                        bind:value={contactMessage}
                        rows="4"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="Hi Sarah, I came across your profile and would like to discuss a potential opportunity..."
                        required
                    ></textarea>
                </div>
                
                <div class="flex gap-3 justify-end">
                    <button 
                        type="button"
                        onclick={closeContactModal}
                        class="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button 
                        type="submit"
                        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                    >
                        Send Message
                    </button>
                </div>
            </form>
        </div>
    </div>
{/if}
