<script lang="ts">
  import { User, Bell, Briefcase, Lock, Shield, Mail, Phone, Calendar, CheckCircle, AlertCircle, ChevronRight } from '@lucide/svelte';
  import type { Component } from 'svelte';

  type ColorName = 'blue' | 'green' | 'purple' | 'yellow' | 'red';

  interface ColorClasses {
    bg: string;
    text: string;
    hover: string;
  }

  // Mock user data - will be replaced with actual data from auth/database
  const user = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    memberSince: 'January 2024',
    profileCompletion: 85,
    emailVerified: true,
    phoneVerified: false
  };

  // Mock stats
  const stats: Array<{ label: string; value: string; icon: Component; color: ColorName }> = [
    { label: 'Profile Completion', value: `${user.profileCompletion}%`, icon: User, color: 'blue' },
    { label: 'Applications Sent', value: '12', icon: Briefcase, color: 'green' },
    { label: 'Saved Jobs', value: '24', icon: AlertCircle, color: 'purple' },
    { label: 'Job Alerts Active', value: '3', icon: Bell, color: 'yellow' }
  ];

  // Settings sections
  const settingsSections: Array<{ title: string; description: string; icon: Component; href: string; color: ColorName }> = [
    {
      title: 'Notifications',
      description: 'Manage email and push notification preferences',
      icon: Bell,
      href: '/settings/notifications',
      color: 'blue'
    },
    {
      title: 'Job Alerts',
      description: 'Create and manage custom job alerts',
      icon: Briefcase,
      href: '/settings/job-alerts',
      color: 'green'
    },
    {
      title: 'Privacy',
      description: 'Control your profile and data visibility',
      icon: Shield,
      href: '/settings/privacy',
      color: 'purple'
    },
    {
      title: 'Change Password',
      description: 'Update your account password',
      icon: Lock,
      href: '/settings/password',
      color: 'red'
    }
  ];

  const colorClasses: Record<ColorName, ColorClasses> = {
    blue: { bg: 'bg-blue-100', text: 'text-blue-600', hover: 'group-hover:bg-blue-50' },
    green: { bg: 'bg-green-100', text: 'text-green-600', hover: 'group-hover:bg-green-50' },
    purple: { bg: 'bg-purple-100', text: 'text-purple-600', hover: 'group-hover:bg-purple-50' },
    yellow: { bg: 'bg-yellow-100', text: 'text-yellow-600', hover: 'group-hover:bg-yellow-50' },
    red: { bg: 'bg-red-100', text: 'text-red-600', hover: 'group-hover:bg-red-50' }
  };
</script>

<svelte:head>
  <title>Account Settings - HirePulse.in</title>
  <meta name="description" content="Manage your HirePulse account settings and preferences" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center gap-3 mb-4">
      <div class="p-3 bg-white/10 rounded-lg">
        <User size={32} />
      </div>
      <div>
        <h1 class="text-3xl md:text-4xl font-bold">Account Settings</h1>
        <p class="text-blue-100 mt-1">Manage your account preferences and settings</p>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid lg:grid-cols-3 gap-8">

      <!-- Left Column - Account Overview -->
      <div class="lg:col-span-1">
        <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100 sticky top-24">
          <h2 class="text-xl font-bold text-gray-800 mb-6">Account Overview</h2>

          <!-- User Info -->
          <div class="space-y-4 mb-6 pb-6 border-b border-gray-200">
            <div class="flex items-center gap-3">
              <div class="w-16 h-16 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-full flex items-center justify-center text-white text-2xl font-bold">
                {user.name.split(' ').map(n => n[0]).join('')}
              </div>
              <div>
                <h3 class="font-bold text-gray-800">{user.name}</h3>
                <p class="text-sm text-gray-600">Job Seeker</p>
              </div>
            </div>

            <div class="space-y-2">
              <div class="flex items-center gap-2 text-sm">
                <Mail size={16} class="text-gray-400" />
                <span class="text-gray-700">{user.email}</span>
                {#if user.emailVerified}
                  <CheckCircle size={16} class="text-green-600" />
                {/if}
              </div>

              <div class="flex items-center gap-2 text-sm">
                <Phone size={16} class="text-gray-400" />
                <span class="text-gray-700">{user.phone}</span>
                {#if !user.phoneVerified}
                  <AlertCircle size={16} class="text-yellow-600" />
                {/if}
              </div>

              <div class="flex items-center gap-2 text-sm">
                <Calendar size={16} class="text-gray-400" />
                <span class="text-gray-600">Member since {user.memberSince}</span>
              </div>
            </div>
          </div>

          <!-- Profile Completion -->
          <div class="mb-4">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-700">Profile Completion</span>
              <span class="text-sm font-bold text-blue-600">{user.profileCompletion}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full transition-all duration-500"
                style="width: {user.profileCompletion}%"
              ></div>
            </div>
            {#if user.profileCompletion < 100}
              <a href="/profile/" class="text-xs text-blue-600 hover:text-blue-700 mt-2 inline-block">
                Complete your profile →
              </a>
            {/if}
          </div>

          <!-- Quick Actions -->
          <div class="space-y-2">
            <a
              href="/profile/"
              class="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Edit Profile
            </a>
            <a
              href="/jobseeker-dashboard/"
              class="block w-full text-center border border-gray-300 hover:border-blue-300 text-gray-700 hover:text-blue-600 font-semibold py-2 px-4 rounded-lg transition-colors duration-200"
            >
              Back to Dashboard
            </a>
          </div>
        </div>
      </div>

      <!-- Right Column - Settings Sections -->
      <div class="lg:col-span-2">

        <!-- Stats Grid -->
        <div class="grid md:grid-cols-2 gap-6 mb-8">
          {#each stats as stat}
            <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
              <div class="flex items-center justify-between">
                <div>
                  <p class="text-sm text-gray-600 mb-1">{stat.label}</p>
                  <p class="text-3xl font-bold text-gray-800">{stat.value}</p>
                </div>
                <div class="p-3 {colorClasses[stat.color].bg} rounded-full">
                  <stat.icon class={colorClasses[stat.color].text} size={24} />
                </div>
              </div>
            </div>
          {/each}
        </div>

        <!-- Settings Sections -->
        <div class="space-y-8">
          <div>
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Settings</h2>

            <div class="space-y-4">
              {#each settingsSections as section}
                <a
                  href={section.href}
                  class="group block bg-white rounded-xl shadow-lg hover:shadow-xl p-6 border border-gray-100 hover:border-blue-200 transition-all duration-200"
                >
                  <div class="flex items-center gap-4">
                    <div class="p-3 {colorClasses[section.color].bg} {colorClasses[section.color].hover} rounded-lg transition-colors duration-200">
                      <section.icon class={colorClasses[section.color].text} size={24} />
                    </div>

                    <div class="flex-1">
                      <h3 class="text-lg font-bold text-gray-800 group-hover:text-blue-600 transition-colors duration-200 mb-1">
                        {section.title}
                      </h3>
                      <p class="text-sm text-gray-600">
                        {section.description}
                      </p>
                    </div>

                    <ChevronRight class="text-gray-400 group-hover:text-blue-600 transition-colors duration-200" size={24} />
                  </div>
                </a>
              {/each}
            </div>
          </div>

          <!-- Account Actions -->
          <div class="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
            <h3 class="text-lg font-bold text-gray-800 mb-4">Account Actions</h3>

            <div class="space-y-3">
              <button
                type="button"
                class="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 flex items-center justify-between group"
              >
                <span class="text-gray-700 group-hover:text-blue-600">Download My Data</span>
                <ChevronRight class="text-gray-400 group-hover:text-blue-600" size={20} />
              </button>

              <button
                type="button"
                class="w-full text-left px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors duration-200 flex items-center justify-between group"
              >
                <span class="text-gray-700 group-hover:text-blue-600">Export Resume</span>
                <ChevronRight class="text-gray-400 group-hover:text-blue-600" size={20} />
              </button>

              <button
                type="button"
                class="w-full text-left px-4 py-3 rounded-lg hover:bg-red-50 transition-colors duration-200 flex items-center justify-between group"
              >
                <span class="text-red-600">Deactivate Account</span>
                <ChevronRight class="text-red-400" size={20} />
              </button>
            </div>
          </div>

          <!-- Help Section -->
          <div class="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl shadow-lg p-6 text-white">
            <h3 class="text-lg font-bold mb-2">Need Help?</h3>
            <p class="text-sm text-blue-100 mb-4">
              Visit our help center or contact support for assistance with your account.
            </p>
            <div class="flex gap-3">
              <a
                href="/help/"
                class="bg-white text-blue-600 hover:bg-blue-50 font-semibold py-2 px-4 rounded-lg transition-colors duration-200 text-sm"
              >
                Help Center
              </a>
              <a
                href="/contact/"
                class="border border-white hover:bg-white/10 font-semibold py-2 px-4 rounded-lg transition-colors duration-200 text-sm"
              >
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</section>
