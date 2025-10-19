<script>
  // Mock saved jobs data
  let savedJobs = [
    { id: 1, title: 'Frontend Developer', company: 'TechCorp', location: 'Remote', type: 'Full-time', posted: '2 days ago' },
    { id: 3, title: 'UI/UX Designer', company: 'Designify', location: 'Mumbai', type: 'Contract', posted: '3 days ago' }
  ];
</script>

<section class="py-12 bg-gray-50 dark:bg-gray-900 min-h-screen">
  <div class="container mx-auto px-4 max-w-3xl">
    <h1 class="text-2xl font-bold mb-6 text-primary-700 dark:text-primary-200">Saved Jobs</h1>
    <div class="grid gap-6 sm:grid-cols-2">
      {#if savedJobs.length === 0}
        <div class="text-center text-gray-500 dark:text-gray-400 py-12 col-span-2">You have not saved any jobs yet.</div>
      {:else}
        {#each savedJobs as job}
          <div class="bg-white dark:bg-gray-900 rounded-xl shadow p-6 border border-gray-100 dark:border-gray-800 flex flex-col">
            <div class="flex items-center gap-3 mb-2">
              <div class="w-10 h-10 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center text-lg font-bold text-primary-700 dark:text-primary-200">{job.company.charAt(0)}</div>
              <div>
                <h3 class="text-xl font-bold mb-1">{job.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm">{job.company}</p>
              </div>
            </div>
            <p class="text-sm text-gray-500 dark:text-gray-400 mb-2">{job.location} • {job.type}</p>
            <span class="text-xs text-gray-400 dark:text-gray-500 mb-4">{job.posted}</span>
            <div class="flex gap-2 mt-auto">
              <a href={`/jobs/${job.id}`} class="btn btn-primary btn-sm flex-1">View</a>
              <button class="btn btn-outline-primary btn-sm flex-1">Remove</button>
            </div>
          </div>
        {/each}
      {/if}
    </div>
  </div>
</section>
