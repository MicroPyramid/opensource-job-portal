<script>
  import { Bell, CheckCheck, Trash2, Filter, Briefcase, MessageCircle, Star, AlertCircle, Check, Settings, X } from '@lucide/svelte';

  let selectedFilter = 'all';
  let showOnlyUnread = false;

  const filters = [
    { id: 'all', name: 'All', icon: Bell },
    { id: 'applications', name: 'Applications', icon: Briefcase },
    { id: 'messages', name: 'Messages', icon: MessageCircle },
    { id: 'job_alerts', name: 'Job Alerts', icon: Star },
    { id: 'system', name: 'System', icon: AlertCircle }
  ];

  let notifications = [
    {
      id: 1,
      type: 'applications',
      title: 'Application Status Updated',
      message: 'Your application for Senior Software Engineer at Tech Corp has been reviewed',
      timestamp: '2024-01-18T14:30:00',
      read: false,
      actionUrl: '/applications/123'
    },
    {
      id: 2,
      type: 'messages',
      title: 'New Message from Recruiter',
      message: 'Sarah Johnson from Innovate Inc. sent you a message',
      timestamp: '2024-01-18T13:15:00',
      read: false,
      actionUrl: '/messages/456'
    },
    {
      id: 3,
      type: 'job_alerts',
      title: 'New Job Alert Match',
      message: '5 new jobs matching "Full Stack Developer - Remote" are available',
      timestamp: '2024-01-18T12:00:00',
      read: false,
      actionUrl: '/jobs?alert=789'
    },
    {
      id: 4,
      type: 'applications',
      title: 'Application Received',
      message: 'Your application for Product Manager at StartupXYZ has been received',
      timestamp: '2024-01-18T10:45:00',
      read: true,
      actionUrl: '/applications/124'
    },
    {
      id: 5,
      type: 'system',
      title: 'Profile Completion Reminder',
      message: 'Complete your profile to increase your chances of getting hired',
      timestamp: '2024-01-18T09:00:00',
      read: true,
      actionUrl: '/profile'
    },
    {
      id: 6,
      type: 'job_alerts',
      title: 'New Job Alert Match',
      message: '3 new jobs matching "Backend Engineer - Python" are available',
      timestamp: '2024-01-17T16:30:00',
      read: true,
      actionUrl: '/jobs?alert=790'
    },
    {
      id: 7,
      type: 'messages',
      title: 'Message Read Confirmation',
      message: 'Your message to TechStart Recruiting was read',
      timestamp: '2024-01-17T15:20:00',
      read: true,
      actionUrl: '/messages/457'
    },
    {
      id: 8,
      type: 'applications',
      title: 'Interview Invitation',
      message: 'You have been invited to interview for Software Engineer at Cloud Solutions',
      timestamp: '2024-01-17T11:00:00',
      read: false,
      actionUrl: '/applications/125'
    },
    {
      id: 9,
      type: 'system',
      title: 'Weekly Job Recommendations',
      message: 'Check out 15 new jobs we think you\'ll love',
      timestamp: '2024-01-17T08:00:00',
      read: true,
      actionUrl: '/jobs'
    },
    {
      id: 10,
      type: 'job_alerts',
      title: 'Job Alert Created',
      message: 'Your job alert for "Data Scientist - Machine Learning" is now active',
      timestamp: '2024-01-16T18:00:00',
      read: true,
      actionUrl: '/settings/job-alerts'
    }
  ];

  // Stats
  $: totalNotifications = notifications.length;
  $: unreadCount = notifications.filter(n => !n.read).length;
  $: todayCount = notifications.filter(n => {
    const today = new Date().toDateString();
    const notifDate = new Date(n.timestamp).toDateString();
    return today === notifDate;
  }).length;

  // Filtered notifications
  $: filteredNotifications = notifications
    .filter(n => selectedFilter === 'all' || n.type === selectedFilter)
    .filter(n => !showOnlyUnread || !n.read)
    .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

  function markAsRead(id) {
    notifications = notifications.map(n =>
      n.id === id ? { ...n, read: true } : n
    );
  }

  function markAllAsRead() {
    notifications = notifications.map(n => ({ ...n, read: true }));
  }

  function deleteNotification(id) {
    notifications = notifications.filter(n => n.id !== id);
  }

  function clearAllRead() {
    const confirmed = confirm('Are you sure you want to delete all read notifications?');
    if (confirmed) {
      notifications = notifications.filter(n => !n.read);
    }
  }

  function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }

  function getNotificationIcon(type) {
    const iconMap = {
      applications: Briefcase,
      messages: MessageCircle,
      job_alerts: Star,
      system: AlertCircle
    };
    return iconMap[type] || Bell;
  }

  function getNotificationColor(type) {
    const colorMap = {
      applications: 'blue',
      messages: 'green',
      job_alerts: 'purple',
      system: 'gray'
    };
    return colorMap[type] || 'gray';
  }
</script>

<svelte:head>
  <title>Notifications - HirePulse.in</title>
  <meta name="description" content="View and manage your notifications" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-12">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="p-3 bg-white/10 rounded-lg">
          <Bell size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Notifications</h1>
          <p class="text-blue-100 mt-1">Stay updated with your job search activity</p>
        </div>
      </div>

      <a
        href="/settings/notifications"
        class="bg-white/10 hover:bg-white/20 text-white font-semibold px-4 py-2 rounded-lg transition-colors duration-200 flex items-center gap-2"
      >
        <Settings size={18} />
        <span class="hidden md:inline">Settings</span>
      </a>
    </div>
  </div>
</section>

<!-- Stats Section -->
<section class="bg-white border-b border-gray-200 py-8">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="flex items-center gap-4 p-4 bg-blue-50 rounded-lg">
        <div class="p-3 bg-blue-100 rounded-lg">
          <Bell class="text-blue-600" size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-800">{totalNotifications}</div>
          <div class="text-sm text-gray-600">Total Notifications</div>
        </div>
      </div>

      <div class="flex items-center gap-4 p-4 bg-red-50 rounded-lg">
        <div class="p-3 bg-red-100 rounded-lg">
          <AlertCircle class="text-red-600" size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-800">{unreadCount}</div>
          <div class="text-sm text-gray-600">Unread</div>
        </div>
      </div>

      <div class="flex items-center gap-4 p-4 bg-green-50 rounded-lg">
        <div class="p-3 bg-green-100 rounded-lg">
          <Check class="text-green-600" size={24} />
        </div>
        <div>
          <div class="text-2xl font-bold text-gray-800">{todayCount}</div>
          <div class="text-sm text-gray-600">Today</div>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-12 bg-gray-50">
  <div class="container mx-auto px-4 lg:px-6">

    <!-- Filters and Actions -->
    <div class="bg-white rounded-xl shadow-lg border border-gray-100 p-6 mb-6">
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-4">

        <!-- Filter Tabs -->
        <div class="flex items-center gap-2 overflow-x-auto">
          {#each filters as filter}
            <button
              onclick={() => selectedFilter = filter.id}
              class="flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors duration-200 whitespace-nowrap"
              class:bg-blue-600={selectedFilter === filter.id}
              class:text-white={selectedFilter === filter.id}
              class:bg-gray-100={selectedFilter !== filter.id}
              class:text-gray-700={selectedFilter !== filter.id}
              class:hover:bg-gray-200={selectedFilter !== filter.id}
            >
              <svelte:component this={filter.icon} size={16} />
              {filter.name}
            </button>
          {/each}
        </div>

        <!-- Actions -->
        <div class="flex items-center gap-3">
          <label class="flex items-center gap-2 cursor-pointer text-sm">
            <input type="checkbox" bind:checked={showOnlyUnread} class="w-4 h-4 text-blue-600 rounded" />
            <span class="text-gray-700">Unread only</span>
          </label>

          {#if unreadCount > 0}
            <button
              onclick={markAllAsRead}
              class="text-blue-600 hover:text-blue-700 font-medium text-sm flex items-center gap-2"
            >
              <CheckCheck size={16} />
              Mark all as read
            </button>
          {/if}

          {#if notifications.some(n => n.read)}
            <button
              onclick={clearAllRead}
              class="text-red-600 hover:text-red-700 font-medium text-sm flex items-center gap-2"
            >
              <Trash2 size={16} />
              Clear read
            </button>
          {/if}
        </div>
      </div>
    </div>

    <!-- Notifications List -->
    {#if filteredNotifications.length > 0}
      <div class="space-y-3">
        {#each filteredNotifications as notification (notification.id)}
          {@const IconComponent = getNotificationIcon(notification.type)}
          {@const color = getNotificationColor(notification.type)}

          <div
            class="bg-white rounded-xl shadow-lg border border-gray-100 hover:shadow-xl transition-all duration-300 overflow-hidden"
            class:bg-blue-50={!notification.read}
            class:border-blue-200={!notification.read}
          >
            <div class="p-6">
              <div class="flex items-start gap-4">
                <!-- Icon -->
                <div class="flex-shrink-0">
                  <div
                    class="p-3 rounded-lg"
                    class:bg-blue-100={color === 'blue'}
                    class:bg-green-100={color === 'green'}
                    class:bg-purple-100={color === 'purple'}
                    class:bg-gray-100={color === 'gray'}
                  >
                    <svelte:component
                      this={IconComponent}
                      size={24}
                      class={
                        color === 'blue' ? 'text-blue-600' :
                        color === 'green' ? 'text-green-600' :
                        color === 'purple' ? 'text-purple-600' :
                        'text-gray-600'
                      }
                    />
                  </div>
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between gap-4">
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center gap-2 mb-1">
                        <h3 class="text-lg font-bold text-gray-800">{notification.title}</h3>
                        {#if !notification.read}
                          <span class="w-2 h-2 bg-blue-600 rounded-full"></span>
                        {/if}
                      </div>
                      <p class="text-gray-600 mb-2">{notification.message}</p>
                      <div class="flex items-center gap-4 text-sm text-gray-500">
                        <span>{formatTimestamp(notification.timestamp)}</span>
                        <span class="capitalize text-gray-400">• {notification.type.replace('_', ' ')}</span>
                      </div>
                    </div>

                    <!-- Timestamp and Actions -->
                    <div class="flex items-start gap-2 flex-shrink-0">
                      {#if !notification.read}
                        <button
                          onclick={() => markAsRead(notification.id)}
                          class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors duration-200"
                          title="Mark as read"
                        >
                          <Check size={18} />
                        </button>
                      {/if}
                      <button
                        onclick={() => deleteNotification(notification.id)}
                        class="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors duration-200"
                        title="Delete"
                      >
                        <X size={18} />
                      </button>
                    </div>
                  </div>

                  <!-- Action Button -->
                  {#if notification.actionUrl}
                    <div class="mt-4">
                      <a
                        href={notification.actionUrl}
                        class="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                      >
                        View Details →
                      </a>
                    </div>
                  {/if}
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="bg-white rounded-xl shadow-lg p-12 text-center border border-gray-100">
        <div class="flex justify-center mb-4">
          <div class="p-4 bg-gray-100 rounded-full">
            <Bell class="text-gray-400" size={48} />
          </div>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-2">No Notifications</h2>
        <p class="text-gray-600">
          {#if showOnlyUnread}
            You're all caught up! No unread notifications.
          {:else if selectedFilter !== 'all'}
            No {filters.find(f => f.id === selectedFilter)?.name.toLowerCase()} notifications yet.
          {:else}
            You don't have any notifications yet. We'll notify you when there's activity on your account.
          {/if}
        </p>
      </div>
    {/if}

  </div>
</section>
