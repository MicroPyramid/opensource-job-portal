<script>
  import { Bell, Plus, Trash2, Edit, MapPin, DollarSign, Briefcase, ChevronLeft, Save, X } from '@lucide/svelte';

  // Mock existing job alerts
  let jobAlerts = [
    {
      id: 1,
      name: 'Senior Software Engineer - Remote',
      keywords: ['software engineer', 'developer', 'backend'],
      location: 'Remote',
      jobType: 'Full-time',
      salaryMin: 120000,
      salaryMax: 180000,
      experience: 'Senior',
      frequency: 'instant',
      active: true,
      createdDate: '2024-01-15'
    },
    {
      id: 2,
      name: 'Product Manager - San Francisco',
      keywords: ['product manager', 'PM'],
      location: 'San Francisco, CA',
      jobType: 'Full-time',
      salaryMin: 130000,
      salaryMax: 200000,
      experience: 'Mid-Level',
      frequency: 'daily',
      active: true,
      createdDate: '2024-01-10'
    },
    {
      id: 3,
      name: 'UX Designer - Contract',
      keywords: ['UX', 'designer', 'UI/UX'],
      location: 'Anywhere',
      jobType: 'Contract',
      salaryMin: 80000,
      salaryMax: 120000,
      experience: 'Entry Level',
      frequency: 'weekly',
      active: false,
      createdDate: '2024-01-05'
    }
  ];

  let showNewAlertModal = false;
  let editingAlert = null;

  // New alert form data
  let newAlert = {
    name: '',
    keywords: '',
    location: '',
    jobType: 'All',
    salaryMin: '',
    salaryMax: '',
    experience: 'All',
    frequency: 'instant'
  };

  function openNewAlertModal() {
    newAlert = {
      name: '',
      keywords: '',
      location: '',
      jobType: 'All',
      salaryMin: '',
      salaryMax: '',
      experience: 'All',
      frequency: 'instant'
    };
    editingAlert = null;
    showNewAlertModal = true;
  }

  function openEditModal(alert) {
    editingAlert = alert;
    newAlert = {
      name: alert.name,
      keywords: alert.keywords.join(', '),
      location: alert.location,
      jobType: alert.jobType,
      salaryMin: alert.salaryMin.toString(),
      salaryMax: alert.salaryMax.toString(),
      experience: alert.experience,
      frequency: alert.frequency
    };
    showNewAlertModal = true;
  }

  function closeModal() {
    showNewAlertModal = false;
    editingAlert = null;
  }

  async function handleSaveAlert() {
    // TODO: Replace with actual API call
    console.log('Saving alert:', newAlert);

    const alertData = {
      id: editingAlert ? editingAlert.id : Date.now(),
      name: newAlert.name,
      keywords: newAlert.keywords.split(',').map(k => k.trim()).filter(k => k),
      location: newAlert.location,
      jobType: newAlert.jobType,
      salaryMin: parseInt(newAlert.salaryMin) || 0,
      salaryMax: parseInt(newAlert.salaryMax) || 0,
      experience: newAlert.experience,
      frequency: newAlert.frequency,
      active: true,
      createdDate: editingAlert ? editingAlert.createdDate : new Date().toISOString().split('T')[0]
    };

    if (editingAlert) {
      // Update existing alert
      const index = jobAlerts.findIndex(a => a.id === editingAlert.id);
      jobAlerts[index] = alertData;
    } else {
      // Add new alert
      jobAlerts = [...jobAlerts, alertData];
    }

    closeModal();
  }

  function toggleAlert(alert) {
    alert.active = !alert.active;
    jobAlerts = jobAlerts; // Trigger reactivity
    // TODO: Save to API
  }

  function deleteAlert(alert) {
    if (confirm(`Are you sure you want to delete the alert "${alert.name}"?`)) {
      jobAlerts = jobAlerts.filter(a => a.id !== alert.id);
      // TODO: Delete from API
    }
  }

  $: activeAlerts = jobAlerts.filter(a => a.active).length;
</script>

<svelte:head>
  <title>Job Alerts - HirePulse.in</title>
  <meta name="description" content="Manage your custom job alerts" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center gap-4 mb-4">
      <a
        href="/settings"
        class="p-2 hover:bg-white/10 rounded-lg transition-colors duration-200"
      >
        <ChevronLeft size={24} />
      </a>
      <div class="flex items-center gap-3 flex-1">
        <div class="p-3 bg-white/10 rounded-lg">
          <Bell size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Job Alerts</h1>
          <p class="text-blue-100 mt-1">Create and manage custom job alerts</p>
        </div>
      </div>
      <button
        type="button"
        onclick={openNewAlertModal}
        class="bg-white text-blue-600 hover:bg-blue-50 font-semibold py-3 px-6 rounded-lg transition-colors duration-200 shadow-lg flex items-center gap-2"
      >
        <Plus size={20} />
        <span class="hidden md:inline">New Alert</span>
      </button>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6 max-w-5xl">

    <!-- Stats -->
    <div class="grid md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Total Alerts</p>
            <p class="text-3xl font-bold text-gray-800">{jobAlerts.length}</p>
          </div>
          <div class="p-3 bg-blue-100 rounded-full">
            <Bell class="text-blue-600" size={24} />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Active Alerts</p>
            <p class="text-3xl font-bold text-green-600">{activeAlerts}</p>
          </div>
          <div class="p-3 bg-green-100 rounded-full">
            <Bell class="text-green-600" size={24} />
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-600 mb-1">Paused Alerts</p>
            <p class="text-3xl font-bold text-yellow-600">{jobAlerts.length - activeAlerts}</p>
          </div>
          <div class="p-3 bg-yellow-100 rounded-full">
            <Bell class="text-yellow-600" size={24} />
          </div>
        </div>
      </div>
    </div>

    <!-- Job Alerts List -->
    <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
      <h2 class="text-2xl font-bold text-gray-800 mb-6">Your Job Alerts</h2>

      {#if jobAlerts.length === 0}
        <div class="text-center py-12">
          <div class="flex justify-center mb-4">
            <div class="p-4 bg-gray-100 rounded-full">
              <Bell class="text-gray-400" size={48} />
            </div>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">No Job Alerts Yet</h3>
          <p class="text-gray-600 mb-6">Create your first job alert to get notified about relevant opportunities</p>
          <button
            type="button"
            onclick={openNewAlertModal}
            class="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
          >
            <Plus size={20} />
            Create Job Alert
          </button>
        </div>
      {:else}
        <div class="space-y-4">
          {#each jobAlerts as alert (alert.id)}
            <div class="border border-gray-200 rounded-lg p-6 hover:border-blue-200 transition-all duration-200">
              <div class="flex items-start justify-between mb-4">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-lg font-bold text-gray-800">{alert.name}</h3>
                    {#if alert.active}
                      <span class="bg-green-100 text-green-700 text-xs px-2 py-1 rounded-full font-medium">Active</span>
                    {:else}
                      <span class="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-full font-medium">Paused</span>
                    {/if}
                  </div>
                  <p class="text-sm text-gray-500">Created on {new Date(alert.createdDate).toLocaleDateString()}</p>
                </div>

                <div class="flex items-center gap-2">
                  <!-- Toggle Active -->
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={alert.active}
                      onchange={() => toggleAlert(alert)}
                      class="sr-only peer"
                    />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
                  </label>

                  <!-- Edit Button -->
                  <button
                    type="button"
                    onclick={() => openEditModal(alert)}
                    class="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                    title="Edit alert"
                  >
                    <Edit size={18} />
                  </button>

                  <!-- Delete Button -->
                  <button
                    type="button"
                    onclick={() => deleteAlert(alert)}
                    class="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                    title="Delete alert"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>

              <!-- Alert Details -->
              <div class="grid md:grid-cols-2 gap-4 text-sm">
                <div class="flex items-start gap-2">
                  <Briefcase size={16} class="text-gray-400 mt-0.5 flex-shrink-0" />
                  <div>
                    <span class="text-gray-600">Keywords:</span>
                    <div class="flex flex-wrap gap-1 mt-1">
                      {#each alert.keywords as keyword}
                        <span class="bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full text-xs">{keyword}</span>
                      {/each}
                    </div>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <MapPin size={16} class="text-gray-400 flex-shrink-0" />
                  <div>
                    <span class="text-gray-600">Location:</span>
                    <span class="text-gray-800 ml-1 font-medium">{alert.location}</span>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <DollarSign size={16} class="text-gray-400 flex-shrink-0" />
                  <div>
                    <span class="text-gray-600">Salary:</span>
                    <span class="text-gray-800 ml-1 font-medium">
                      ${(alert.salaryMin / 1000).toFixed(0)}k - ${(alert.salaryMax / 1000).toFixed(0)}k
                    </span>
                  </div>
                </div>

                <div class="flex items-center gap-2">
                  <Bell size={16} class="text-gray-400 flex-shrink-0" />
                  <div>
                    <span class="text-gray-600">Frequency:</span>
                    <span class="text-gray-800 ml-1 font-medium capitalize">{alert.frequency}</span>
                  </div>
                </div>
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Info Box -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-6">
      <h3 class="font-bold text-blue-900 mb-2">How Job Alerts Work</h3>
      <ul class="text-sm text-blue-800 space-y-1 list-disc list-inside">
        <li>Create alerts based on your job preferences</li>
        <li>Get notified when new jobs match your criteria</li>
        <li>Choose from instant, daily, or weekly notifications</li>
        <li>Pause or edit alerts anytime</li>
      </ul>
    </div>

  </div>
</section>

<!-- New/Edit Alert Modal -->
{#if showNewAlertModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onclick={closeModal}>
    <div class="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
      <!-- Modal Header -->
      <div class="sticky top-0 bg-white border-b border-gray-200 p-6 flex items-center justify-between">
        <h2 class="text-2xl font-bold text-gray-800">
          {editingAlert ? 'Edit Job Alert' : 'Create New Job Alert'}
        </h2>
        <button
          type="button"
          onclick={closeModal}
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
        >
          <X size={24} class="text-gray-600" />
        </button>
      </div>

      <!-- Modal Content -->
      <div class="p-6 space-y-5">
        <!-- Alert Name -->
        <div>
          <label for="alertName" class="block text-sm font-medium text-gray-700 mb-2">
            Alert Name *
          </label>
          <input
            id="alertName"
            type="text"
            bind:value={newAlert.name}
            placeholder="e.g., Senior Engineer - Remote"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">Give your alert a descriptive name</p>
        </div>

        <!-- Keywords -->
        <div>
          <label for="keywords" class="block text-sm font-medium text-gray-700 mb-2">
            Keywords *
          </label>
          <input
            id="keywords"
            type="text"
            bind:value={newAlert.keywords}
            placeholder="e.g., software engineer, developer, backend"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="text-xs text-gray-500 mt-1">Separate multiple keywords with commas</p>
        </div>

        <!-- Location -->
        <div>
          <label for="location" class="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <input
            id="location"
            type="text"
            bind:value={newAlert.location}
            placeholder="e.g., San Francisco, CA or Remote"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- Job Type -->
        <div>
          <label for="jobType" class="block text-sm font-medium text-gray-700 mb-2">
            Job Type
          </label>
          <select
            id="jobType"
            bind:value={newAlert.jobType}
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="All">All Types</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
            <option value="Internship">Internship</option>
          </select>
        </div>

        <!-- Salary Range -->
        <div class="grid md:grid-cols-2 gap-4">
          <div>
            <label for="salaryMin" class="block text-sm font-medium text-gray-700 mb-2">
              Min Salary ($/year)
            </label>
            <input
              id="salaryMin"
              type="number"
              bind:value={newAlert.salaryMin}
              placeholder="60000"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label for="salaryMax" class="block text-sm font-medium text-gray-700 mb-2">
              Max Salary ($/year)
            </label>
            <input
              id="salaryMax"
              type="number"
              bind:value={newAlert.salaryMax}
              placeholder="120000"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>

        <!-- Experience Level -->
        <div>
          <label for="experience" class="block text-sm font-medium text-gray-700 mb-2">
            Experience Level
          </label>
          <select
            id="experience"
            bind:value={newAlert.experience}
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="All">All Levels</option>
            <option value="Entry Level">Entry Level</option>
            <option value="Mid-Level">Mid-Level</option>
            <option value="Senior">Senior</option>
            <option value="Lead">Lead</option>
            <option value="Executive">Executive</option>
          </select>
        </div>

        <!-- Frequency -->
        <div>
          <label for="frequency" class="block text-sm font-medium text-gray-700 mb-2">
            Notification Frequency *
          </label>
          <select
            id="frequency"
            bind:value={newAlert.frequency}
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="instant">Instant - As jobs are posted</option>
            <option value="daily">Daily Digest - Once per day</option>
            <option value="weekly">Weekly Digest - Once per week</option>
          </select>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="sticky bottom-0 bg-gray-50 border-t border-gray-200 p-6 flex justify-end gap-3">
        <button
          type="button"
          onclick={closeModal}
          class="px-6 py-3 border border-gray-300 text-gray-700 hover:bg-gray-100 font-semibold rounded-lg transition-colors duration-200"
        >
          Cancel
        </button>
        <button
          type="button"
          onclick={handleSaveAlert}
          disabled={!newAlert.name || !newAlert.keywords}
          class="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          <Save size={20} />
          {editingAlert ? 'Update Alert' : 'Create Alert'}
        </button>
      </div>
    </div>
  </div>
{/if}
