<script>
    import { Calendar, MapPin, Building2, Filter, SortAsc, Eye, Clock, CheckCircle, XCircle, AlertCircle } from '@lucide/svelte';
    import { onMount } from 'svelte';

    /** @type {{ data: import('./$types').PageData }} */
    let { data } = $props();

    // Sample data - replace with actual data from your backend
    let appliedJobs = [
        {
            id: 1,
            title: "Senior Frontend Developer",
            company: "TechCorp Solutions",
            location: "San Francisco, CA",
            appliedDate: "2024-01-15",
            status: "pending",
            salary: "$120,000 - $150,000",
            applicationDetails: {
                resume: "john_doe_resume.pdf",
                coverLetter: "Passionate about creating exceptional user experiences...",
                submittedAt: "2024-01-15T10:30:00Z"
            }
        },
        {
            id: 2,
            title: "Full Stack Engineer",
            company: "StartupXYZ",
            location: "Remote",
            appliedDate: "2024-01-12",
            status: "reviewed",
            salary: "$100,000 - $130,000",
            applicationDetails: {
                resume: "john_doe_resume.pdf",
                coverLetter: "Excited to contribute to your innovative platform...",
                submittedAt: "2024-01-12T14:20:00Z"
            }
        },
        {
            id: 3,
            title: "React Developer",
            company: "Digital Agency Pro",
            location: "New York, NY",
            appliedDate: "2024-01-08",
            status: "rejected",
            salary: "$90,000 - $110,000",
            applicationDetails: {
                resume: "john_doe_resume.pdf",
                coverLetter: "Looking forward to working with your creative team...",
                submittedAt: "2024-01-08T09:15:00Z"
            }
        }
    ];

    let filteredJobs = appliedJobs;
    let selectedStatus = 'all';
    let sortBy = 'date';
    let sortOrder = 'desc';
    let selectedJob = null;
    let showModal = false;

    const statusConfig = {
        pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-800', icon: Clock },
        reviewed: { label: 'Under Review', color: 'bg-blue-100 text-blue-800', icon: AlertCircle },
        rejected: { label: 'Rejected', color: 'bg-red-100 text-red-800', icon: XCircle },
        accepted: { label: 'Accepted', color: 'bg-green-100 text-green-800', icon: CheckCircle }
    };

    function filterJobs() {
        filteredJobs = selectedStatus === 'all' 
            ? appliedJobs 
            : appliedJobs.filter(job => job.status === selectedStatus);
        sortJobs();
    }

    function sortJobs() {
        filteredJobs = [...filteredJobs].sort((a, b) => {
            let comparison = 0;
            
            if (sortBy === 'date') {
                comparison = new Date(a.appliedDate) - new Date(b.appliedDate);
            } else if (sortBy === 'status') {
                comparison = a.status.localeCompare(b.status);
            } else if (sortBy === 'company') {
                comparison = a.company.localeCompare(b.company);
            }
            
            return sortOrder === 'desc' ? -comparison : comparison;
        });
    }

    function openApplicationDetails(job) {
        selectedJob = job;
        showModal = true;
    }

    function closeModal() {
        showModal = false;
        selectedJob = null;
    }

    function formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    onMount(() => {
        filterJobs();
    });

    $effect(() => {
        filterJobs();
    });
</script>

<svelte:head>
    <title>Applied Jobs - HirePulse.in</title>
    <meta name="description" content="Track your job applications and their status on HirePulse.in" />
</svelte:head>

<div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <!-- Header -->
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-gray-900 mb-2">Applied Jobs</h1>
            <p class="text-gray-600">Track your job applications and their progress</p>
        </div>

        <!-- Filters and Sorting -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div class="flex flex-col sm:flex-row gap-4">
                    <!-- Status Filter -->
                    <div class="flex items-center gap-2">
                        <Filter class="w-4 h-4 text-gray-500" />
                        <select 
                            bind:value={selectedStatus}
                            class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="all">All Status</option>
                            <option value="pending">Pending</option>
                            <option value="reviewed">Under Review</option>
                            <option value="rejected">Rejected</option>
                            <option value="accepted">Accepted</option>
                        </select>
                    </div>

                    <!-- Sort By -->
                    <div class="flex items-center gap-2">
                        <SortAsc class="w-4 h-4 text-gray-500" />
                        <select 
                            bind:value={sortBy}
                            class="border border-gray-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="date">Application Date</option>
                            <option value="status">Status</option>
                            <option value="company">Company</option>
                        </select>
                        <button 
                            onclick={() => sortOrder = sortOrder === 'asc' ? 'desc' : 'asc'}
                            class="px-3 py-2 text-sm border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                        >
                            {sortOrder === 'asc' ? '↑' : '↓'}
                        </button>
                    </div>
                </div>

                <div class="text-sm text-gray-600">
                    {filteredJobs.length} application{filteredJobs.length !== 1 ? 's' : ''}
                </div>
            </div>
        </div>

        <!-- Jobs Grid -->
        {#if filteredJobs.length === 0}
            <div class="text-center py-12">
                <div class="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                    <Building2 class="w-12 h-12 text-gray-400" />
                </div>
                <h3 class="text-lg font-medium text-gray-900 mb-2">No applications found</h3>
                <p class="text-gray-600">
                    {selectedStatus === 'all' 
                        ? "You haven't applied to any jobs yet." 
                        : `No applications with ${selectedStatus} status found.`}
                </p>
            </div>
        {:else}
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {#each filteredJobs as job (job.id)}
                    <div class="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                        <div class="p-6">
                            <!-- Status Badge -->
                            <div class="flex items-center justify-between mb-4">
                                <span class="px-2 py-1 rounded-full text-xs font-medium {statusConfig[job.status].color}">
                                    <svelte:component this={statusConfig[job.status].icon} class="w-3 h-3 inline mr-1" />
                                    {statusConfig[job.status].label}
                                </span>
                                <span class="text-xs text-gray-500 flex items-center">
                                    <Calendar class="w-3 h-3 mr-1" />
                                    {formatDate(job.appliedDate)}
                                </span>
                            </div>

                            <!-- Job Details -->
                            <h3 class="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">{job.title}</h3>
                            
                            <div class="space-y-2 mb-4">
                                <div class="flex items-center text-sm text-gray-600">
                                    <Building2 class="w-4 h-4 mr-2 text-gray-400" />
                                    {job.company}
                                </div>
                                <div class="flex items-center text-sm text-gray-600">
                                    <MapPin class="w-4 h-4 mr-2 text-gray-400" />
                                    {job.location}
                                </div>
                            </div>

                            <div class="text-sm font-medium text-gray-900 mb-4">{job.salary}</div>

                            <!-- View Details Button -->
                            <button 
                                onclick={() => openApplicationDetails(job)}
                                class="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-md hover:bg-blue-700 transition-colors"
                            >
                                <Eye class="w-4 h-4 mr-2" />
                                View Application Details
                            </button>
                        </div>
                    </div>
                {/each}
            </div>
        {/if}
    </div>
</div>

<!-- Application Details Modal -->
{#if showModal && selectedJob}
    <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50" onclick={closeModal}>
        <div class="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
            <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
                <div class="flex items-center justify-between">
                    <h2 class="text-xl font-semibold text-gray-900">Application Details</h2>
                    <button 
                        onclick={closeModal}
                        class="text-gray-400 hover:text-gray-600 transition-colors"
                    >
                        <XCircle class="w-6 h-6" />
                    </button>
                </div>
            </div>

            <div class="p-6">
                <!-- Job Information -->
                <div class="mb-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">{selectedJob.title}</h3>
                    <div class="space-y-2">
                        <div class="flex items-center text-gray-600">
                            <Building2 class="w-4 h-4 mr-2" />
                            {selectedJob.company}
                        </div>
                        <div class="flex items-center text-gray-600">
                            <MapPin class="w-4 h-4 mr-2" />
                            {selectedJob.location}
                        </div>
                        <div class="flex items-center justify-between">
                            <span class="font-medium text-gray-900">{selectedJob.salary}</span>
                            <span class="px-2 py-1 rounded-full text-xs font-medium {statusConfig[selectedJob.status].color}">
                                <svelte:component this={statusConfig[selectedJob.status].icon} class="w-3 h-3 inline mr-1" />
                                {statusConfig[selectedJob.status].label}
                            </span>
                        </div>
                    </div>
                </div>

                <!-- Application Information -->
                <div class="border-t border-gray-200 pt-6">
                    <h4 class="text-md font-semibold text-gray-900 mb-4">Application Information</h4>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Applied Date</label>
                            <p class="text-sm text-gray-900">{formatDate(selectedJob.appliedDate)}</p>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Submitted Resume</label>
                            <p class="text-sm text-blue-600 hover:text-blue-800 cursor-pointer underline">
                                {selectedJob.applicationDetails.resume}
                            </p>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Cover Letter</label>
                            <div class="bg-gray-50 rounded-md p-3">
                                <p class="text-sm text-gray-700">{selectedJob.applicationDetails.coverLetter}</p>
                            </div>
                        </div>

                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-1">Submission Time</label>
                            <p class="text-sm text-gray-900">
                                {new Date(selectedJob.applicationDetails.submittedAt).toLocaleString()}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
{/if}