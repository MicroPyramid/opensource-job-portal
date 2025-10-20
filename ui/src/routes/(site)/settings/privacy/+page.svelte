<script>
  import { Shield, Eye, FileText, Database, Download, Trash2, ChevronLeft, Save, Check, AlertCircle } from '@lucide/svelte';

  // Mock privacy settings - will be replaced with API data
  let privacySettings = {
    profileVisibility: 'recruiters', // public, private, recruiters
    resumeVisibility: 'recruiters', // public, private, recruiters
    showEmail: false,
    showPhone: false,
    showSocialLinks: true,
    allowMessagesFrom: 'verified', // anyone, verified, none
    showApplicationHistory: false,
    allowProfileIndexing: true,
    shareDataWithPartners: false,
    allowAnalytics: true
  };

  let isSaving = false;
  let saveSuccess = false;

  async function handleSave() {
    isSaving = true;
    saveSuccess = false;

    try {
      // TODO: Replace with actual API call
      console.log('Saving privacy settings:', privacySettings);

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

  async function handleDownloadData() {
    // TODO: Implement data download
    console.log('Downloading user data...');
    alert('Your data download has been initiated. You will receive an email with a download link shortly.');
  }

  async function handleDeleteAccount() {
    const confirmed = confirm(
      'Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently deleted.'
    );

    if (confirmed) {
      const doubleConfirm = prompt('Type "DELETE" to confirm account deletion:');
      if (doubleConfirm === 'DELETE') {
        // TODO: Implement account deletion
        console.log('Deleting account...');
        alert('Account deletion initiated. You will receive a confirmation email.');
      }
    }
  }
</script>

<svelte:head>
  <title>Privacy Settings - HirePulse.in</title>
  <meta name="description" content="Manage your privacy and data settings" />
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
          <Shield size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Privacy Settings</h1>
          <p class="text-blue-100 mt-1">Control your profile and data visibility</p>
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
        <p class="text-green-700 font-medium">Your privacy settings have been saved!</p>
      </div>
    {/if}

    <div class="space-y-6">

      <!-- Profile Visibility -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
          <div class="p-3 bg-blue-100 rounded-lg">
            <Eye class="text-blue-600" size={24} />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">Profile Visibility</h2>
            <p class="text-sm text-gray-600 mt-1">Control who can see your profile information</p>
          </div>
        </div>

        <div class="space-y-6">
          <!-- Profile Visibility Level -->
          <fieldset class="space-y-3 border-0 p-0 m-0">
            <legend class="block text-sm font-medium text-gray-700 mb-3">
              Who can view your profile?
            </legend>
            <div class="space-y-3">
              <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-blue-500={privacySettings.profileVisibility === 'public'} class:bg-blue-50={privacySettings.profileVisibility === 'public'} class:border-gray-200={privacySettings.profileVisibility !== 'public'}>
                <input
                  type="radio"
                  bind:group={privacySettings.profileVisibility}
                  value="public"
                  class="mt-1"
                />
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">Public</div>
                  <div class="text-sm text-gray-600">Anyone can view your profile, including search engines</div>
                </div>
              </label>

              <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-blue-500={privacySettings.profileVisibility === 'recruiters'} class:bg-blue-50={privacySettings.profileVisibility === 'recruiters'} class:border-gray-200={privacySettings.profileVisibility !== 'recruiters'}>
                <input
                  type="radio"
                  bind:group={privacySettings.profileVisibility}
                  value="recruiters"
                  class="mt-1"
                />
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">Recruiters Only (Recommended)</div>
                  <div class="text-sm text-gray-600">Only verified recruiters can view your profile</div>
                </div>
              </label>

              <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-blue-500={privacySettings.profileVisibility === 'private'} class:bg-blue-50={privacySettings.profileVisibility === 'private'} class:border-gray-200={privacySettings.profileVisibility !== 'private'}>
                <input
                  type="radio"
                  bind:group={privacySettings.profileVisibility}
                  value="private"
                  class="mt-1"
                />
                <div class="flex-1">
                  <div class="font-semibold text-gray-800">Private</div>
                  <div class="text-sm text-gray-600">Only you can view your profile</div>
                </div>
              </label>
            </div>
          </fieldset>

          <!-- Contact Information -->
          <div class="pt-6 border-t border-gray-200">
            <h3 class="font-semibold text-gray-800 mb-4">Contact Information Visibility</h3>
            <div class="space-y-4">
              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-gray-800">Show Email Address</div>
                  <div class="text-sm text-gray-600">Allow others to see your email</div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={privacySettings.showEmail}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-gray-800">Show Phone Number</div>
                  <div class="text-sm text-gray-600">Allow others to see your phone number</div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={privacySettings.showPhone}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>

              <div class="flex items-center justify-between">
                <div>
                  <div class="font-medium text-gray-800">Show Social Links</div>
                  <div class="text-sm text-gray-600">Display LinkedIn, GitHub, etc.</div>
                </div>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    bind:checked={privacySettings.showSocialLinks}
                    class="sr-only peer"
                  />
                  <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Resume Visibility -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
          <div class="p-3 bg-purple-100 rounded-lg">
            <FileText class="text-purple-600" size={24} />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">Resume Visibility</h2>
            <p class="text-sm text-gray-600 mt-1">Control who can access your resume</p>
          </div>
        </div>

        <fieldset class="space-y-3 border-0 p-0 m-0">
          <legend class="block text-sm font-medium text-gray-700 mb-3">
            Who can view and download your resume?
          </legend>
          <div class="space-y-3">
            <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-purple-500={privacySettings.resumeVisibility === 'public'} class:bg-purple-50={privacySettings.resumeVisibility === 'public'} class:border-gray-200={privacySettings.resumeVisibility !== 'public'}>
              <input
                type="radio"
                bind:group={privacySettings.resumeVisibility}
                value="public"
                class="mt-1"
              />
              <div class="flex-1">
                <div class="font-semibold text-gray-800">Public</div>
                <div class="text-sm text-gray-600">Anyone can view and download your resume</div>
              </div>
            </label>

            <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-purple-500={privacySettings.resumeVisibility === 'recruiters'} class:bg-purple-50={privacySettings.resumeVisibility === 'recruiters'} class:border-gray-200={privacySettings.resumeVisibility !== 'recruiters'}>
              <input
                type="radio"
                bind:group={privacySettings.resumeVisibility}
                value="recruiters"
                class="mt-1"
              />
              <div class="flex-1">
                <div class="font-semibold text-gray-800">Recruiters Only (Recommended)</div>
                <div class="text-sm text-gray-600">Only verified recruiters can access your resume</div>
              </div>
            </label>

            <label class="flex items-start gap-3 p-4 border-2 rounded-lg cursor-pointer transition-all duration-200" class:border-purple-500={privacySettings.resumeVisibility === 'private'} class:bg-purple-50={privacySettings.resumeVisibility === 'private'} class:border-gray-200={privacySettings.resumeVisibility !== 'private'}>
              <input
                type="radio"
                bind:group={privacySettings.resumeVisibility}
                value="private"
                class="mt-1"
              />
              <div class="flex-1">
                <div class="font-semibold text-gray-800">Private</div>
                <div class="text-sm text-gray-600">Only you can access your resume</div>
              </div>
            </label>
          </div>

          <div class="mt-4 flex items-center justify-between">
            <div>
              <div class="font-medium text-gray-800">Show Application History</div>
              <div class="text-sm text-gray-600">Display which companies you've applied to</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={privacySettings.showApplicationHistory}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-purple-600"></div>
            </label>
          </div>
        </fieldset>
      </div>

      <!-- Communication Preferences -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <h2 class="text-xl font-bold text-gray-800 mb-4">Communication Preferences</h2>

        <div>
          <label for="message-visibility" class="block text-sm font-medium text-gray-700 mb-3">
            Who can send you messages?
          </label>
          <select
            id="message-visibility"
            bind:value={privacySettings.allowMessagesFrom}
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white text-gray-700"
          >
            <option value="anyone">Anyone</option>
            <option value="verified">Verified recruiters only</option>
            <option value="none">No one</option>
          </select>
          <p class="text-xs text-gray-500 mt-1">Control who can contact you through HirePulse</p>
        </div>
      </div>

      <!-- Data & Privacy -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <div class="flex items-center gap-3 mb-6 pb-6 border-b border-gray-200">
          <div class="p-3 bg-green-100 rounded-lg">
            <Database class="text-green-600" size={24} />
          </div>
          <div>
            <h2 class="text-2xl font-bold text-gray-800">Data & Privacy</h2>
            <p class="text-sm text-gray-600 mt-1">Manage how your data is used</p>
          </div>
        </div>

        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-gray-800">Allow Search Engine Indexing</div>
              <div class="text-sm text-gray-600">Let search engines index your public profile</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={privacySettings.allowProfileIndexing}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-gray-800">Share Data with Partners</div>
              <div class="text-sm text-gray-600">Allow trusted partners to access anonymized data</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={privacySettings.shareDataWithPartners}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>

          <div class="flex items-center justify-between">
            <div>
              <div class="font-medium text-gray-800">Analytics & Performance</div>
              <div class="text-sm text-gray-600">Help us improve by allowing usage analytics</div>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={privacySettings.allowAnalytics}
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-green-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-green-600"></div>
            </label>
          </div>
        </div>
      </div>

      <!-- Data Management -->
      <div class="bg-white rounded-xl shadow-lg p-6 md:p-8 border border-gray-100">
        <h2 class="text-xl font-bold text-gray-800 mb-6">Data Management</h2>

        <div class="space-y-4">
          <button
            type="button"
            onclick={handleDownloadData}
            class="w-full flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 group"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-100 rounded-lg">
                <Download class="text-blue-600" size={20} />
              </div>
              <div class="text-left">
                <div class="font-semibold text-gray-800 group-hover:text-blue-600">Download Your Data</div>
                <div class="text-sm text-gray-600">Get a copy of all your HirePulse data</div>
              </div>
            </div>
          </button>

          <button
            type="button"
            onclick={handleDeleteAccount}
            class="w-full flex items-center justify-between p-4 border-2 border-gray-200 rounded-lg hover:border-red-300 hover:bg-red-50 transition-all duration-200 group"
          >
            <div class="flex items-center gap-3">
              <div class="p-2 bg-red-100 rounded-lg">
                <Trash2 class="text-red-600" size={20} />
              </div>
              <div class="text-left">
                <div class="font-semibold text-gray-800 group-hover:text-red-600">Delete Account</div>
                <div class="text-sm text-gray-600">Permanently delete your account and data</div>
              </div>
            </div>
          </button>
        </div>

        <div class="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 flex gap-3">
          <AlertCircle class="text-yellow-600 flex-shrink-0" size={20} />
          <div class="text-sm text-yellow-800">
            <strong>Important:</strong> Account deletion is permanent and cannot be undone. All your data, applications, and saved jobs will be permanently deleted.
          </div>
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
