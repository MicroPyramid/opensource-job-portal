<script>
  import { Bell, Mail, Smartphone, Save, ChevronLeft, Check } from '@lucide/svelte';

  // Mock notification settings - will be replaced with API data
  let emailNotifications = {
    jobAlerts: true,
    applicationUpdates: true,
    messageNotifications: true,
    weeklyDigest: false,
    companyUpdates: true,
    tipsAndResources: false
  };

  let pushNotifications = {
    enabled: false,
    jobAlerts: true,
    applicationUpdates: true,
    messageNotifications: true
  };

  let frequency = {
    jobAlerts: 'instant', // instant, daily, weekly
    digest: 'weekly' // daily, weekly, monthly
  };

  let isSaving = false;
  let saveSuccess = false;

  async function handleSave() {
    isSaving = true;
    saveSuccess = false;

    try {
      // TODO: Replace with actual API call
      console.log('Saving notification settings:', {
        emailNotifications,
        pushNotifications,
        frequency
      });

      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      saveSuccess = true;
      setTimeout(() => {
        saveSuccess = false;
      }, 3000);
    } catch (error) {
      console.error('Save error:', error);
    } finally {
      isSaving = false;
    }
  }

  function handleTogglePush() {
    if (!pushNotifications.enabled) {
      // Request notification permission
      if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
          if (permission === 'granted') {
            pushNotifications.enabled = true;
          }
        });
      }
    } else {
      pushNotifications.enabled = false;
    }
  }
</script>

<svelte:head>
  <title>Notification Settings - PeelJobs</title>
  <meta name="description" content="Manage your notification preferences" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center gap-4 mb-4">
      <a
        href="/settings/"
        class="p-2 hover:bg-white/10 rounded-lg transition-colors duration-200"
      >
        <ChevronLeft size={24} />
      </a>
      <div class="flex items-center gap-3">
        <div class="p-3 bg-white/10 rounded-lg">
          <Bell size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Notifications</h1>
          <p class="text-blue-100 mt-1">Manage your notification preferences</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6 max-w-4xl">

    {#if saveSuccess}
      <div class="mb-6 bg-green-50 border border-green-200 rounded-lg p-4 flex items-center gap-3 animate-fade-in">
        <Check class="text-green-600" size={20} />
        <p class="text-green-700 font-medium">Your notification settings have been saved!</p>
      </div>
    {/if}

    <div class="space-y-6">

      <!-- Email Notifications -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
          <div class="p-3 bg-blue-100 rounded-lg">
            <Mail class="text-blue-600" size={24} />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">Email Notifications</h2>
            <p class="text-sm text-gray-600 mt-1">Choose what updates you want to receive via email</p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Job Alerts -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Job Alerts</h3>
              <p class="text-sm text-gray-600">Get notified when new jobs match your preferences</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.jobAlerts}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <!-- Application Updates -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Application Updates</h3>
              <p class="text-sm text-gray-600">Status changes on your job applications</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.applicationUpdates}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <!-- Message Notifications -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Messages</h3>
              <p class="text-sm text-gray-600">New messages from recruiters</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.messageNotifications}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <!-- Weekly Digest -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Weekly Digest</h3>
              <p class="text-sm text-gray-600">Summary of new jobs and activity</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.weeklyDigest}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <!-- Company Updates -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Company Updates</h3>
              <p class="text-sm text-gray-600">News from companies you follow</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.companyUpdates}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>

          <!-- Tips and Resources -->
          <div class="flex items-center justify-between py-3">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Career Tips & Resources</h3>
              <p class="text-sm text-gray-600">Helpful articles and job search tips</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={emailNotifications.tipsAndResources}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Notification Frequency -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <h2 class="text-2xl font-bold text-gray-800 mb-6">Notification Frequency</h2>

        <div class="space-y-6">
          <!-- Job Alerts Frequency -->
          <div>
            <label for="jobAlertsFrequency" class="block text-sm font-medium text-gray-700 mb-2">
              Job Alerts Frequency
            </label>
            <select
              id="jobAlertsFrequency"
              bind:value={frequency.jobAlerts}
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-700 transition-colors duration-200"
            >
              <option value="instant">Instant - As jobs are posted</option>
              <option value="daily">Daily Digest - Once per day</option>
              <option value="weekly">Weekly Digest - Once per week</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">How often you want to receive job alerts</p>
          </div>

          <!-- Digest Frequency -->
          <div>
            <label for="digestFrequency" class="block text-sm font-medium text-gray-700 mb-2">
              Activity Digest Frequency
            </label>
            <select
              id="digestFrequency"
              bind:value={frequency.digest}
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-700 transition-colors duration-200"
            >
              <option value="daily">Daily - Every day</option>
              <option value="weekly">Weekly - Every Monday</option>
              <option value="monthly">Monthly - First of month</option>
            </select>
            <p class="text-xs text-gray-500 mt-1">Frequency for activity summaries and updates</p>
          </div>
        </div>
      </div>

      <!-- Push Notifications -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
          <div class="p-3 bg-purple-100 rounded-lg">
            <Smartphone class="text-purple-600" size={24} />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">Push Notifications</h2>
            <p class="text-sm text-gray-600 mt-1">Get instant updates on your device (coming soon)</p>
          </div>
        </div>

        <div class="space-y-4">
          <!-- Enable Push Notifications -->
          <div class="flex items-center justify-between py-3 bg-blue-50 rounded-lg px-4">
            <div class="flex-1">
              <h3 class="font-semibold text-gray-800">Enable Push Notifications</h3>
              <p class="text-sm text-gray-600">Allow browser notifications</p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={pushNotifications.enabled}
                onchange={handleTogglePush}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>

          {#if pushNotifications.enabled}
            <div class="space-y-4 pl-4">
              <!-- Job Alerts Push -->
              <div class="flex items-center justify-between py-2">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-800">Job Alerts</h4>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={pushNotifications.jobAlerts}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <!-- Application Updates Push -->
              <div class="flex items-center justify-between py-2">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-800">Application Updates</h4>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={pushNotifications.applicationUpdates}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>

              <!-- Messages Push -->
              <div class="flex items-center justify-between py-2">
                <div class="flex-1">
                  <h4 class="font-medium text-gray-800">Messages</h4>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={pushNotifications.messageNotifications}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
                </label>
              </div>
            </div>
          {/if}
        </div>
      </div>

      <!-- Save Button -->
      <div class="flex justify-between items-center pt-4">
        <a
          href="/settings/"
          class="text-gray-600 hover:text-blue-600 font-medium"
        >
          ← Back to Settings
        </a>

        <button
          type="button"
          onclick={handleSave}
          disabled={isSaving}
          class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {#if isSaving}
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Saving...
          {:else}
            <Save size={20} />
            Save Changes
          {/if}
        </button>
      </div>

    </div>
  </div>
</section>

<style>
  @keyframes fade-in {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fade-in {
    animation: fade-in 0.3s ease-out;
  }
</style>
