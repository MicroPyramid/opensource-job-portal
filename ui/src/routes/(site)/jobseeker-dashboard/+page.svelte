<script lang="ts">
    import { User, Briefcase, BookmarkIcon, Search, Settings, Bell, TrendingUp, Clock, CheckCircle, XCircle, AlertCircle } from '@lucide/svelte';
    import type { PageData } from './$types';

    interface DashboardUser {
        name: string;
        profileCompletion: number;
        avatar: string;
    }

    type JobStatus = 'pending' | 'reviewed' | 'interview' | 'rejected';

    interface AppliedJobSummary {
        id: number;
        title: string;
        company: string;
        status: JobStatus;
        appliedDate: string;
    }

    interface SavedJobSummary {
        id: number;
        title: string;
        company: string;
        location: string;
        salary: string;
    }

    const _: { data: PageData } = $props();
    void _;

    // Mock data - replace with actual data from your backend
    const user: DashboardUser = {
        name: 'John Doe',
        profileCompletion: 75,
        avatar: '/api/placeholder/40/40'
    };

    const appliedJobs: AppliedJobSummary[] = [
        { id: 1, title: 'Frontend Developer', company: 'TechCorp', status: 'reviewed', appliedDate: '2024-01-15' },
        { id: 2, title: 'UX Designer', company: 'DesignStudio', status: 'pending', appliedDate: '2024-01-14' },
        { id: 3, title: 'Product Manager', company: 'StartupXYZ', status: 'rejected', appliedDate: '2024-01-10' },
        { id: 4, title: 'Full Stack Developer', company: 'WebSolutions', status: 'interview', appliedDate: '2024-01-12' }
    ];

    const savedJobs: SavedJobSummary[] = [
        { id: 1, title: 'Senior React Developer', company: 'Meta', location: 'Remote', salary: '$120k - $150k' },
        { id: 2, title: 'Backend Engineer', company: 'Google', location: 'Mountain View', salary: '$140k - $180k' },
        { id: 3, title: 'DevOps Engineer', company: 'Amazon', location: 'Seattle', salary: '$130k - $160k' }
    ];

    const statusIconMap: Record<JobStatus, typeof AlertCircle> = {
        pending: AlertCircle,
        reviewed: Clock,
        interview: CheckCircle,
        rejected: XCircle
    };

    const statusColorMap: Record<JobStatus, string> = {
        pending: 'text-yellow-600 bg-yellow-50',
        reviewed: 'text-blue-600 bg-blue-50',
        interview: 'text-green-600 bg-green-50',
        rejected: 'text-red-600 bg-red-50'
    };

    const appliedJobsStats = $derived({
        total: appliedJobs.length,
        pending: appliedJobs.filter(job => job.status === 'pending').length,
        reviewed: appliedJobs.filter(job => job.status === 'reviewed').length,
        interview: appliedJobs.filter(job => job.status === 'interview').length
    });
</script>

<svelte:head>
    <title>Dashboard - PeelJobs</title>
</svelte:head>

<div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex justify-between items-center py-4">
                <div class="flex items-center space-x-4">
                    <img src={user.avatar} alt="Profile" class="w-10 h-10 rounded-full">
                    <div>
                        <h1 class="text-xl font-semibold text-gray-900">Welcome back, {user.name}!</h1>
                        <p class="text-sm text-gray-600">Ready to find your dream job?</p>
                    </div>
                </div>
                <div class="flex items-center space-x-3">
                    <button class="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                        <Bell class="w-5 h-5" />
                    </button>
                    <button class="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                        <Settings class="w-5 h-5" />
                    </button>
                </div>
            </div>
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Profile Completion Section -->
        <div class="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 mb-8 text-white">
            <div class="flex flex-col md:flex-row md:items-center md:justify-between">
                <div class="mb-4 md:mb-0">
                    <h2 class="text-lg font-semibold mb-2">Complete Your Profile</h2>
                    <p class="text-blue-100">A complete profile gets 3x more views from recruiters</p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="flex-1 md:w-32">
                        <div class="flex justify-between text-sm mb-1">
                            <span>Progress</span>
                            <span>{user.profileCompletion}%</span>
                        </div>
                        <div class="w-full bg-blue-500 rounded-full h-2">
                            <div class="bg-white rounded-full h-2 transition-all duration-300" style="width: {user.profileCompletion}%"></div>
                        </div>
                    </div>
                    <a href="/profile/" class="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-50 transition-colors">
                        Update Profile
                    </a>
                </div>
            </div>
        </div>

        <!-- Quick Stats -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-4">
                    <div class="bg-blue-50 p-3 rounded-lg">
                        <Briefcase class="w-6 h-6 text-blue-600" />
                    </div>
                    <span class="text-2xl font-bold text-gray-900">{appliedJobsStats.total}</span>
                </div>
                <h3 class="font-medium text-gray-900">Applied Jobs</h3>
                <p class="text-sm text-gray-600">Total applications</p>
            </div>

            <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-4">
                    <div class="bg-green-50 p-3 rounded-lg">
                        <TrendingUp class="w-6 h-6 text-green-600" />
                    </div>
                    <span class="text-2xl font-bold text-gray-900">{appliedJobsStats.interview}</span>
                </div>
                <h3 class="font-medium text-gray-900">Interviews</h3>
                <p class="text-sm text-gray-600">Scheduled</p>
            </div>

            <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-4">
                    <div class="bg-purple-50 p-3 rounded-lg">
                        <BookmarkIcon class="w-6 h-6 text-purple-600" />
                    </div>
                    <span class="text-2xl font-bold text-gray-900">{savedJobs.length}</span>
                </div>
                <h3 class="font-medium text-gray-900">Saved Jobs</h3>
                <p class="text-sm text-gray-600">For later</p>
            </div>

            <div class="bg-white rounded-xl p-6 shadow-sm border hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-4">
                    <div class="bg-yellow-50 p-3 rounded-lg">
                        <Clock class="w-6 h-6 text-yellow-600" />
                    </div>
                    <span class="text-2xl font-bold text-gray-900">{appliedJobsStats.pending}</span>
                </div>
                <h3 class="font-medium text-gray-900">Pending</h3>
                <p class="text-sm text-gray-600">Under review</p>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <!-- Recent Applications -->
            <div class="lg:col-span-2">
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="p-6 border-b">
                        <div class="flex items-center justify-between">
                            <h2 class="text-lg font-semibold text-gray-900">Recent Applications</h2>
                            <a href="/applied-jobs/" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                                View All
                            </a>
                        </div>
                    </div>
                    <div class="divide-y">
                        {#each appliedJobs.slice(0, 5) as job}
                            {@const statusIcon = statusIconMap[job.status]}
                            <div class="p-6 hover:bg-gray-50 transition-colors">
                                <div class="flex items-start justify-between">
                                    <div class="flex-1">
                                        <h3 class="font-medium text-gray-900 mb-1">{job.title}</h3>
                                        <p class="text-sm text-gray-600 mb-2">{job.company}</p>
                                        <p class="text-xs text-gray-500">Applied on {new Date(job.appliedDate).toLocaleDateString()}</p>
                                    </div>
                                    <div class="flex items-center space-x-2">
                                        <span class={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${statusColorMap[job.status]}`}>
                                            <statusIcon class="w-3 h-3 mr-1"></statusIcon>
                                            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>

            <!-- Sidebar -->
            <div class="space-y-6">
                <!-- Quick Actions -->
                <div class="bg-white rounded-xl shadow-sm border p-6">
                    <h3 class="font-semibold text-gray-900 mb-4">Quick Actions</h3>
                    <div class="space-y-3">
                        <a href="/jobs/" class="flex items-center p-3 rounded-lg border hover:bg-gray-50 transition-colors group">
                            <div class="bg-blue-50 p-2 rounded-lg mr-3 group-hover:bg-blue-100 transition-colors">
                                <Search class="w-4 h-4 text-blue-600" />
                            </div>
                            <span class="font-medium text-gray-900">Search Jobs</span>
                        </a>
                        <a href="/profile/" class="flex items-center p-3 rounded-lg border hover:bg-gray-50 transition-colors group">
                            <div class="bg-green-50 p-2 rounded-lg mr-3 group-hover:bg-green-100 transition-colors">
                                <User class="w-4 h-4 text-green-600" />
                            </div>
                            <span class="font-medium text-gray-900">Edit Profile</span>
                        </a>
                        <a href="/saved-jobs/" class="flex items-center p-3 rounded-lg border hover:bg-gray-50 transition-colors group">
                            <div class="bg-purple-50 p-2 rounded-lg mr-3 group-hover:bg-purple-100 transition-colors">
                                <BookmarkIcon class="w-4 h-4 text-purple-600" />
                            </div>
                            <span class="font-medium text-gray-900">Saved Jobs</span>
                        </a>
                    </div>
                </div>

                <!-- Saved Jobs Preview -->
                <div class="bg-white rounded-xl shadow-sm border">
                    <div class="p-6 border-b">
                        <div class="flex items-center justify-between">
                            <h3 class="font-semibold text-gray-900">Saved Jobs</h3>
                            <a href="/saved-jobs/" class="text-blue-600 hover:text-blue-700 text-sm font-medium">
                                View All
                            </a>
                        </div>
                    </div>
                    <div class="divide-y">
                        {#each savedJobs.slice(0, 3) as job}
                            <div class="p-4 hover:bg-gray-50 transition-colors">
                                <h4 class="font-medium text-gray-900 text-sm mb-1">{job.title}</h4>
                                <p class="text-xs text-gray-600 mb-1">{job.company}</p>
                                <div class="flex items-center justify-between">
                                    <span class="text-xs text-gray-500">{job.location}</span>
                                    <span class="text-xs font-medium text-green-600">{job.salary}</span>
                                </div>
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
