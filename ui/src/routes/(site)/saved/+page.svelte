<script lang="ts">
  import { Bookmark, Calendar, Building2, ExternalLink, Trash2 } from '@lucide/svelte';

  // Mock saved jobs data
  let savedJobs = [
    { id: 1, title: 'Frontend Developer', company: 'TechCorp', location: 'Remote', type: 'Full-time', posted: '2 days ago' },
    { id: 3, title: 'UI/UX Designer', company: 'Designify', location: 'Mumbai', type: 'Contract', posted: '3 days ago' }
  ];

  function handleRemove(jobId: number) {
    // TODO: Implement API call to remove saved job
    console.log('Removing saved job:', jobId);
  }
</script>

<svelte:head>
  <title>Saved Jobs - PeelJobs</title>
  <meta name="description" content="View all your saved jobs in one place" />
</svelte:head>

<section class="py-8 md:py-12 bg-gray-50 min-h-screen">
  <div class="container mx-auto px-4 max-w-5xl">
    <!-- Page Header -->
    <div class="mb-6 md:mb-8">
      <h1 class="text-2xl md:text-3xl font-bold text-gray-900 mb-2">Saved Jobs</h1>
      <p class="text-sm md:text-base text-gray-600">Keep track of jobs you're interested in</p>
    </div>

    <!-- Saved Jobs Grid -->
    <div class="grid gap-4 md:gap-6">
      {#if savedJobs.length === 0}
        <div class="bg-white rounded-xl shadow-sm p-8 md:p-12 border border-gray-200 text-center">
          <Bookmark size={48} class="mx-auto text-gray-300 mb-4" />
          <p class="text-gray-500 text-base md:text-lg">You have not saved any jobs yet.</p>
          <a href="/jobs/" class="inline-block mt-4 px-6 py-2 bg-blue-600 text-white text-sm font-medium rounded hover:bg-blue-700 transition-colors">
            Browse Jobs
          </a>
        </div>
      {:else}
        {#each savedJobs as job}
          <div class="bg-white rounded-xl shadow-sm p-4 md:p-6 border border-gray-200 hover:shadow-md transition-shadow">
            <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <!-- Job Info -->
              <div class="flex gap-3 md:gap-4 flex-1">
                <!-- Company Avatar -->
                <div class="w-12 h-12 md:w-14 md:h-14 rounded-lg bg-blue-100 flex items-center justify-center text-lg md:text-xl font-bold text-blue-700 flex-shrink-0">
                  {job.company.charAt(0)}
                </div>

                <!-- Job Details -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg md:text-xl font-bold text-gray-900 mb-1 truncate">{job.title}</h3>
                  <div class="flex items-center gap-2 text-sm text-gray-600 mb-2">
                    <Building2 size={14} class="flex-shrink-0" />
                    <span class="truncate">{job.company}</span>
                  </div>
                  <div class="flex flex-wrap gap-2 text-xs md:text-sm text-gray-500">
                    <span>{job.location}</span>
                    <span>•</span>
                    <span>{job.type}</span>
                  </div>
                </div>
              </div>

              <!-- Posted Date & Actions -->
              <div class="flex flex-col gap-3 md:items-end">
                <!-- Posted Date -->
                <div class="flex items-center gap-1.5 text-xs text-gray-500">
                  <Calendar size={14} class="flex-shrink-0" />
                  <span>Posted {job.posted}</span>
                </div>

                <!-- Action Buttons -->
                <div class="flex gap-2">
                  <a
                    href="/jobs/{job.id}/"
                    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-blue-600 border border-blue-600 rounded hover:bg-blue-50 transition-colors"
                  >
                    <ExternalLink size={14} />
                    <span class="hidden sm:inline">View Job</span>
                  </a>
                  <button
                    onclick={() => handleRemove(job.id)}
                    class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 border border-red-600 rounded hover:bg-red-50 transition-colors"
                  >
                    <Trash2 size={14} />
                    <span class="hidden sm:inline">Remove</span>
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
