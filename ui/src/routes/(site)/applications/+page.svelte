<script lang="ts">
  import { FileText, Calendar, Building2, ExternalLink, XCircle } from '@lucide/svelte';

  // Mock applications data
  let applications = [
    { id: 1, jobTitle: 'Frontend Developer', company: 'TechCorp', location: 'Bangalore', type: 'Full-time', status: 'Under Review', applied: '2025-04-15' },
    { id: 2, jobTitle: 'Backend Engineer', company: 'DataSoft', location: 'Remote', type: 'Full-time', status: 'Interview', applied: '2025-04-10' }
  ];

  function getStatusColor(status: string) {
    switch (status) {
      case 'Interview':
        return 'bg-green-100 text-green-700';
      case 'Under Review':
        return 'bg-yellow-100 text-yellow-700';
      case 'Rejected':
        return 'bg-red-100 text-red-700';
      default:
        return 'bg-gray-100 text-gray-700';
    }
  }

  function handleWithdraw(appId: number) {
    // TODO: Implement API call to withdraw application
    console.log('Withdrawing application:', appId);
  }
</script>

<svelte:head>
  <title>My Applications - PeelJobs</title>
  <meta name="description" content="Track all your job applications in one place" />
</svelte:head>

<section class="py-8 md:py-12 bg-gray-50 min-h-screen">
  <div class="container mx-auto px-4 max-w-5xl">
    <!-- Page Header -->
    <div class="mb-6 md:mb-8">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">My Applications</h1>
      <p class="text-sm md:text-base text-gray-600">Track the status of all your job applications</p>
    </div>

    <!-- Applications Grid -->
    <div class="grid gap-4 md:gap-6">
      {#if applications.length === 0}
        <div class="bg-white rounded-xl shadow-sm p-8 md:p-12 border border-gray-200 text-center">
          <FileText size={48} class="mx-auto text-gray-300 mb-4" />
          <p class="text-gray-500 text-base md:text-lg">You have not applied to any jobs yet.</p>
          <a href="/jobs/" class="inline-block mt-4 px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors">
            Browse Jobs
          </a>
        </div>
      {:else}
        {#each applications as app}
          <div class="bg-white rounded-xl shadow-sm p-4 md:p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <!-- Job Info -->
              <div class="flex gap-3 md:gap-4 flex-1">
                <!-- Company Avatar -->
                <div class="w-12 h-12 md:w-14 md:h-14 rounded-lg bg-blue-100 flex items-center justify-center text-lg md:text-xl font-bold text-blue-700 flex-shrink-0">
                  {app.company.charAt(0)}
                </div>

                <!-- Job Details -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg md:text-xl font-bold text-gray-900 mb-1 truncate">{app.jobTitle}</h3>
                  <div class="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <Building2 size={14} class="flex-shrink-0" />
                    <span class="truncate">{app.company}</span>
                  </div>
                  <div class="flex flex-wrap gap-2 text-xs md:text-sm text-gray-500">
                    <span>{app.location}</span>
                    <span>•</span>
                    <span>{app.type}</span>
                  </div>
                </div>
              </div>

              <!-- Status & Actions -->
              <div class="flex flex-col gap-3 md:items-end">
                <!-- Status Badge -->
                <span class="px-3 py-1 rounded-full text-xs font-semibold {getStatusColor(app.status)} w-fit">
                  {app.status}
                </span>

                <!-- Applied Date -->
                <div class="flex items-center gap-1.5 text-xs text-gray-500">
                  <Calendar size={14} class="flex-shrink-0" />
                  <span>Applied on {app.applied}</span>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-2">
                  <a
                    href="/jobs/{app.id}/"
                    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors"
                  >
                    <ExternalLink size={14} />
                    <span class="hidden sm:inline">View Job</span>
                  </a>
                  <button
                    onclick={() => handleWithdraw(app.id)}
                    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded hover:bg-red-50 transition-colors"
                  >
                    <XCircle size={14} />
                    <span class="hidden sm:inline">Withdraw</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</section>
