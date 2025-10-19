<script>
  // Mock applications data
  let applications = [
    { id: 1, jobTitle: 'Frontend Developer', company: 'TechCorp', status: 'Under Review', applied: '2025-04-15' },
    { id: 2, jobTitle: 'Backend Engineer', company: 'DataSoft', status: 'Interview', applied: '2025-04-10' }
  ];
</script>

<section class="py-12 bg-gray-50 dark:bg-gray-900 min-h-screen">
  <div class="container mx-auto px-4 max-w-3xl">
    <h1 class="text-2xl font-bold mb-6 text-primary-700 dark:text-primary-200">My Applications</h1>
    <div class="bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8 border border-gray-100 dark:border-gray-800">
      {#if applications.length === 0}
        <div class="text-center text-gray-500 dark:text-gray-400 py-12">You have not applied to any jobs yet.</div>
      {:else}
        <table class="w-full text-left">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="py-2 px-3">Job Title</th>
              <th class="py-2 px-3">Company</th>
              <th class="py-2 px-3">Status</th>
              <th class="py-2 px-3">Applied On</th>
              <th class="py-2 px-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {#each applications as app}
              <tr class="border-b border-gray-100 dark:border-gray-800 hover:bg-primary-50 dark:hover:bg-gray-800 transition">
                <td class="py-2 px-3 font-semibold">{app.jobTitle}</td>
                <td class="py-2 px-3">{app.company}</td>
                <td class="py-2 px-3">
                  <span class="px-2 py-1 rounded text-xs font-semibold {app.status === 'Interview' ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-200'}">{app.status}</span>
                </td>
                <td class="py-2 px-3">{app.applied}</td>
                <td class="py-2 px-3">
                  <button class="btn btn-outline-primary btn-xs">Withdraw</button>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      {/if}
    </div>
  </div>
</section>
