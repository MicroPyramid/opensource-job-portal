<script lang="ts">
  import { MessageCircle, Search, Filter, Archive, Star, Trash2, MoreVertical } from '@lucide/svelte';
  import { goto } from '$app/navigation';

  interface RecruiterSummary {
    name: string;
    company: string;
    position: string;
    avatar: string | null;
    online: boolean;
  }

  type FilterType = 'all' | 'unread' | 'starred' | 'archived';

  interface ConversationSummary {
    id: number;
    recruiter: RecruiterSummary;
    jobTitle: string;
    lastMessage: string;
    lastMessageSender: 'me' | 'recruiter';
    timestamp: string;
    unread: number;
    starred: boolean;
    archived: boolean;
  }

  // TODO: Replace with API call to fetch conversations
  let conversations = $state<ConversationSummary[]>([
    {
      id: 1,
      recruiter: {
        name: 'Sarah Johnson',
        company: 'Innovate Inc.',
        position: 'Senior Recruiter',
        avatar: null,
        online: true
      },
      jobTitle: 'Senior Software Engineer',
      lastMessage: 'Great! When would you be available for a quick call?',
      lastMessageSender: 'recruiter', // 'me' or 'recruiter'
      timestamp: '2024-01-18T14:30:00',
      unread: 2,
      starred: false,
      archived: false
    },
    {
      id: 2,
      recruiter: {
        name: 'Michael Chen',
        company: 'Tech Corp',
        position: 'Talent Acquisition Manager',
        avatar: null,
        online: false
      },
      jobTitle: 'Full Stack Developer',
      lastMessage: 'We\'d like to schedule an interview with you.',
      lastMessageSender: 'recruiter',
      timestamp: '2024-01-18T10:15:00',
      unread: 1,
      starred: true,
      archived: false
    },
    {
      id: 3,
      recruiter: {
        name: 'Emily Rodriguez',
        company: 'StartupXYZ',
        position: 'HR Manager',
        avatar: null,
        online: true
      },
      jobTitle: 'React Developer',
      lastMessage: 'Perfect! I\'ll send you the meeting invite shortly.',
      lastMessageSender: 'recruiter',
      timestamp: '2024-01-17T16:45:00',
      unread: 0,
      starred: false,
      archived: false
    },
    {
      id: 4,
      recruiter: {
        name: 'David Williams',
        company: 'Cloud Solutions',
        position: 'Lead Recruiter',
        avatar: null,
        online: false
      },
      jobTitle: 'DevOps Engineer',
      lastMessage: 'Thank you for your interest!',
      lastMessageSender: 'recruiter',
      timestamp: '2024-01-16T14:20:00',
      unread: 0,
      starred: false,
      archived: false
    },
    {
      id: 5,
      recruiter: {
        name: 'Jessica Park',
        company: 'Data Analytics Inc.',
        position: 'Technical Recruiter',
        avatar: null,
        online: true
      },
      jobTitle: 'Backend Engineer',
      lastMessage: 'Looking forward to our conversation!',
      lastMessageSender: 'me',
      timestamp: '2024-01-15T11:30:00',
      unread: 0,
      starred: true,
      archived: false
    },
    {
      id: 6,
      recruiter: {
        name: 'Robert Martinez',
        company: 'FinTech Solutions',
        position: 'Recruiting Specialist',
        avatar: null,
        online: false
      },
      jobTitle: 'Mobile App Developer',
      lastMessage: 'The salary range for this position is $120k-$150k.',
      lastMessageSender: 'recruiter',
      timestamp: '2024-01-14T09:15:00',
      unread: 0,
      starred: false,
      archived: false
    }
  ]);

  let searchQuery = $state('');
  let filterType = $state<FilterType>('all');

  const totalUnread = $derived(
    conversations
      .filter(conversation => !conversation.archived)
      .reduce((sum, conversation) => sum + conversation.unread, 0)
  );

  const starredCount = $derived(
    conversations.filter(conversation => conversation.starred && !conversation.archived).length
  );

  const archivedCount = $derived(conversations.filter(conversation => conversation.archived).length);

  const filteredConversations = $derived(
    (() => {
      const searchLower = searchQuery.toLowerCase();

      return conversations
        .filter(conversation => {
          if (filterType === 'unread' && conversation.unread === 0) return false;
          if (filterType === 'starred' && !conversation.starred) return false;
          if (filterType === 'archived' && !conversation.archived) return false;
          if (filterType === 'all' && conversation.archived) return false;

          return (
            conversation.recruiter.name.toLowerCase().includes(searchLower) ||
            conversation.recruiter.company.toLowerCase().includes(searchLower) ||
            conversation.jobTitle.toLowerCase().includes(searchLower) ||
            conversation.lastMessage.toLowerCase().includes(searchLower)
          );
        })
        .sort(
          (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        );
    })()
  );

  function openConversation(id: number): void {
    goto(`/messages/${id}`);
  }

  function toggleStar(id: number, event: MouseEvent): void {
    event.stopPropagation();
    conversations = conversations.map(conversation =>
      conversation.id === id ? { ...conversation, starred: !conversation.starred } : conversation
    );
  }

  function archiveConversation(id: number, event: MouseEvent): void {
    event.stopPropagation();
    conversations = conversations.map(conversation =>
      conversation.id === id ? { ...conversation, archived: true } : conversation
    );
  }

  function deleteConversation(id: number, event: MouseEvent): void {
    event.stopPropagation();
    if (confirm('Are you sure you want to delete this conversation? This action cannot be undone.')) {
      conversations = conversations.filter(conversation => conversation.id !== id);
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
</script>

<svelte:head>
  <title>Messages - PeelJobs</title>
  <meta name="description" content="Chat with recruiters and hiring managers" />
</svelte:head>

<!-- Page Header -->
<section class="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-800 text-white py-8">
  <div class="container mx-auto px-4 lg:px-6">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex items-center gap-3">
        <div class="p-3 bg-white/10 rounded-lg">
          <MessageCircle size={28} />
        </div>
        <div>
          <h1 class="text-3xl md:text-4xl font-bold">Messages</h1>
          <p class="text-blue-100 mt-1">
            {totalUnread > 0 ? `${totalUnread} unread message${totalUnread > 1 ? 's' : ''}` : 'All caught up!'}
          </p>
        </div>
      </div>

      <!-- Filter Tabs (Desktop) -->
      <div class="hidden md:flex items-center gap-2">
        <button
          onclick={() => filterType = 'all'}
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 {filterType === 'all' ? 'bg-white text-blue-600' : 'bg-white/10 text-white'}"
        >
          All
        </button>
        <button
          onclick={() => filterType = 'unread'}
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 {filterType === 'unread' ? 'bg-white text-blue-600' : 'bg-white/10 text-white'}"
        >
          Unread
          {#if totalUnread > 0}
            <span class="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">{totalUnread}</span>
          {/if}
        </button>
        <button
          onclick={() => filterType = 'starred'}
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 {filterType === 'starred' ? 'bg-white text-blue-600' : 'bg-white/10 text-white'}"
        >
          <Star size={16} />
          Starred
        </button>
        <button
          onclick={() => filterType = 'archived'}
          class="px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 {filterType === 'archived' ? 'bg-white text-blue-600' : 'bg-white/10 text-white'}"
        >
          <Archive size={16} />
          Archived
        </button>
      </div>
    </div>
  </div>
</section>

<!-- Main Content -->
<section class="py-8 bg-gray-50 min-h-screen">
  <div class="container mx-auto px-4 lg:px-6">

    <!-- Mobile Filter Tabs -->
    <div class="md:hidden mb-4 flex items-center gap-2 overflow-x-auto pb-2">
      <button
        onclick={() => filterType = 'all'}
        class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 {filterType === 'all' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}"
      >
        All
      </button>
      <button
        onclick={() => filterType = 'unread'}
        class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 flex items-center gap-2 {filterType === 'unread' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}"
      >
        Unread
        {#if totalUnread > 0}
          <span class="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">{totalUnread}</span>
        {/if}
      </button>
      <button
        onclick={() => filterType = 'starred'}
        class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 flex items-center gap-2 {filterType === 'starred' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}"
      >
        <Star size={16} />
        Starred
      </button>
      <button
        onclick={() => filterType = 'archived'}
        class="px-4 py-2 rounded-lg font-medium transition-all duration-200 whitespace-nowrap flex-shrink-0 flex items-center gap-2 {filterType === 'archived' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700'}"
      >
        <Archive size={16} />
        Archived
      </button>
    </div>

    <!-- Search Bar -->
    <div class="mb-6">
      <div class="relative max-w-2xl">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <Search class="text-gray-400" size={20} />
        </div>
        <input
          type="text"
          bind:value={searchQuery}
          placeholder="Search conversations by name, company, job title, or message..."
          class="w-full pl-12 pr-4 py-3 bg-white border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
      </div>
    </div>

    <!-- Conversations Grid -->
    {#if filteredConversations.length > 0}
      <div class="grid gap-4">
        {#each filteredConversations as conversation (conversation.id)}
          <div
            class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-200 border border-gray-100 overflow-hidden cursor-pointer group"
            onclick={() => openConversation(conversation.id)}
            onkeydown={(e) => e.key === 'Enter' && openConversation(conversation.id)}
            role="button"
            tabindex="0"
          >
            <div class="p-6">
              <div class="flex items-start gap-4">
                <!-- Avatar -->
                <div class="relative flex-shrink-0">
                  <div class="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                    {conversation.recruiter.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  {#if conversation.recruiter.online}
                    <div class="absolute bottom-0 right-0 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                  {/if}
                </div>

                <!-- Content -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-start justify-between mb-2">
                    <div class="flex-1 min-w-0">
                      <h3 class="font-bold text-gray-800 text-lg mb-0.5">{conversation.recruiter.name}</h3>
                      <p class="text-sm text-gray-600">{conversation.recruiter.position} at {conversation.recruiter.company}</p>
                    </div>
                    <div class="flex items-center gap-2 ml-4">
                      <span class="text-sm text-gray-500 whitespace-nowrap">{formatTimestamp(conversation.timestamp)}</span>
                      {#if conversation.unread > 0}
                        <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-full font-semibold">
                          {conversation.unread}
                        </span>
                      {/if}
                    </div>
                  </div>

                  <div class="flex items-center gap-2 mb-3">
                    <span class="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                      {conversation.jobTitle}
                    </span>
                  </div>

                  <div class="flex items-start justify-between gap-4">
                    <p class="text-gray-700 flex-1 line-clamp-2">
                      {#if conversation.lastMessageSender === 'me'}
                        <span class="text-gray-500 font-medium">You: </span>
                      {/if}
                      {conversation.lastMessage}
                    </p>
                  </div>
                </div>

                <!-- Actions -->
                <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                  <button
                    onclick={(e) => toggleStar(conversation.id, e)}
                    class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                    title={conversation.starred ? 'Unstar' : 'Star'}
                  >
                    <Star
                      size={18}
                      class={conversation.starred ? 'text-yellow-500 fill-yellow-500' : 'text-gray-400'}
                    />
                  </button>
                  {#if !conversation.archived}
                    <button
                      onclick={(e) => archiveConversation(conversation.id, e)}
                      class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                      title="Archive"
                    >
                      <Archive size={18} class="text-gray-400" />
                    </button>
                  {/if}
                  <button
                    onclick={(e) => deleteConversation(conversation.id, e)}
                    class="p-2 hover:bg-red-50 rounded-lg transition-colors duration-200"
                    title="Delete"
                  >
                    <Trash2 size={18} class="text-red-500" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        {/each}
      </div>

    {:else}
      <!-- Empty State -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-12">
        <div class="text-center max-w-md mx-auto">
          <div class="p-4 bg-gray-100 rounded-full inline-block mb-4">
            {#if filterType === 'archived'}
              <Archive class="text-gray-400" size={48} />
            {:else if filterType === 'starred'}
              <Star class="text-gray-400" size={48} />
            {:else if filterType === 'unread'}
              <MessageCircle class="text-gray-400" size={48} />
            {:else}
              <Search class="text-gray-400" size={48} />
            {/if}
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">
            {#if filterType === 'archived'}
              No Archived Conversations
            {:else if filterType === 'starred'}
              No Starred Conversations
            {:else if filterType === 'unread'}
              No Unread Messages
            {:else if searchQuery}
              No Conversations Found
            {:else}
              No Messages Yet
            {/if}
          </h3>
          <p class="text-gray-600">
            {#if searchQuery}
              Try adjusting your search terms or filters
            {:else if filterType === 'all'}
              Your conversations with recruiters will appear here
            {:else}
              {filterType === 'archived' ? 'Archived conversations will appear here' : ''}
              {filterType === 'starred' ? 'Star important conversations to find them here' : ''}
              {filterType === 'unread' ? 'You\'re all caught up!' : ''}
            {/if}
          </p>
        </div>
      </div>
    {/if}
  </div>
</section>
