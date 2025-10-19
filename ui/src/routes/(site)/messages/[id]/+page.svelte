<script>
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import {
    ArrowLeft,
    Send,
    Paperclip,
    MoreVertical,
    Phone,
    Video,
    Info,
    Check,
    CheckCheck,
    Smile,
    Image as ImageIcon,
    File
  } from '@lucide/svelte';

  // Get conversation ID from URL params
  $: conversationId = parseInt($page.params.id);

  // TODO: Replace with API call to fetch conversation data
  // Mock data for all conversations
  const allConversations = [
    {
      id: 1,
      recruiter: {
        name: 'Sarah Johnson',
        company: 'Innovate Inc.',
        position: 'Senior Recruiter',
        avatar: null,
        online: true,
        email: 'sarah.johnson@innovate.com',
        phone: '+1 (555) 123-4567'
      },
      jobTitle: 'Senior Software Engineer',
      jobId: 101,
      messages: [
        {
          id: 101,
          sender: 'recruiter',
          text: 'Hi! I reviewed your application for the Senior Software Engineer position. Your background in React and Node.js is really impressive!',
          timestamp: '2024-01-18T13:00:00',
          read: true
        },
        {
          id: 102,
          sender: 'me',
          text: 'Thank you for reaching out! I\'m very interested in this opportunity. I\'ve been working with React for the past 4 years and would love to learn more about the role.',
          timestamp: '2024-01-18T13:15:00',
          read: true
        },
        {
          id: 103,
          sender: 'recruiter',
          text: 'Great! The role involves leading a team of 5 developers and working on our new customer-facing platform. The tech stack is React, Node.js, PostgreSQL, and AWS.',
          timestamp: '2024-01-18T13:20:00',
          read: true
        },
        {
          id: 104,
          sender: 'me',
          text: 'That sounds perfect! I have experience with all those technologies. What would be the next steps?',
          timestamp: '2024-01-18T13:25:00',
          read: true
        },
        {
          id: 105,
          sender: 'recruiter',
          text: 'Great! When would you be available for a quick call to discuss the position in more detail?',
          timestamp: '2024-01-18T14:30:00',
          read: false
        }
      ]
    },
    {
      id: 2,
      recruiter: {
        name: 'Michael Chen',
        company: 'Tech Corp',
        position: 'Talent Acquisition Manager',
        avatar: null,
        online: false,
        email: 'michael.chen@techcorp.com',
        phone: '+1 (555) 234-5678'
      },
      jobTitle: 'Full Stack Developer',
      jobId: 102,
      messages: [
        {
          id: 201,
          sender: 'recruiter',
          text: 'Hello! Your profile caught our attention. We have a Full Stack Developer position that matches your skills.',
          timestamp: '2024-01-18T09:00:00',
          read: true
        },
        {
          id: 202,
          sender: 'recruiter',
          text: 'We\'d like to schedule an interview with you. Are you available next week?',
          timestamp: '2024-01-18T10:15:00',
          read: false
        }
      ]
    },
    {
      id: 3,
      recruiter: {
        name: 'Emily Rodriguez',
        company: 'StartupXYZ',
        position: 'HR Manager',
        avatar: null,
        online: true,
        email: 'emily@startupxyz.com',
        phone: '+1 (555) 345-6789'
      },
      jobTitle: 'React Developer',
      jobId: 103,
      messages: [
        {
          id: 301,
          sender: 'recruiter',
          text: 'Hi! Are you available next Tuesday for an interview?',
          timestamp: '2024-01-17T15:00:00',
          read: true
        },
        {
          id: 302,
          sender: 'me',
          text: 'Yes, Tuesday works great for me! What time would be best?',
          timestamp: '2024-01-17T15:30:00',
          read: true
        },
        {
          id: 303,
          sender: 'recruiter',
          text: 'Perfect! I\'ll send you the meeting invite for 2 PM. Looking forward to speaking with you!',
          timestamp: '2024-01-17T16:45:00',
          read: true
        }
      ]
    }
  ];

  // Find the current conversation
  $: conversation = allConversations.find(c => c.id === conversationId);

  // Redirect if conversation not found
  $: if (!conversation && typeof window !== 'undefined') {
    goto('/messages');
  }

  let messageText = '';
  let messages = conversation?.messages || [];
  let showRecruiterInfo = false;
  let showAttachmentMenu = false;

  function goBack() {
    goto('/messages');
  }

  function sendMessage() {
    if (!messageText.trim() || !conversation) return;

    const newMessage = {
      id: Date.now(),
      sender: 'me',
      text: messageText.trim(),
      timestamp: new Date().toISOString(),
      read: false
    };

    messages = [...messages, newMessage];
    messageText = '';

    // Auto-scroll to bottom
    setTimeout(() => {
      const messagesContainer = document.getElementById('messages-container');
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    }, 100);

    // TODO: Send message to API
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function formatMessageTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  }

  function formatMessageDate(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diffDays = Math.floor((now - date) / 86400000);

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return date.toLocaleDateString('en-US', { weekday: 'long' });

    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  }

  function attachFile(type) {
    // TODO: Implement file attachment
    alert(`${type} attachment will be implemented`);
    showAttachmentMenu = false;
  }

  function makeCall(type) {
    // TODO: Implement calling functionality
    alert(`${type} call feature will be implemented`);
  }

  // Group messages by date
  $: groupedMessages = messages.reduce((groups, message) => {
    const date = formatMessageDate(message.timestamp);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
    return groups;
  }, {});
</script>

<svelte:head>
  <title>{conversation?.recruiter.name || 'Conversation'} - Messages - HirePulse.in</title>
  <meta name="description" content="Chat with {conversation?.recruiter.name || 'recruiter'}" />
</svelte:head>

{#if conversation}
  <div class="flex flex-col h-screen">
    <!-- Header -->
    <section class="bg-white border-b border-gray-200 sticky top-0 z-10">
      <div class="container mx-auto px-4 lg:px-6">
        <div class="flex items-center justify-between py-4">
          <!-- Left: Back button and recruiter info -->
          <div class="flex items-center gap-3 flex-1 min-w-0">
            <button
              onclick={goBack}
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200 flex-shrink-0"
              title="Back to messages"
            >
              <ArrowLeft size={24} class="text-gray-600" />
            </button>

            <div class="relative flex-shrink-0">
              <div class="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                {conversation.recruiter.name.split(' ').map(n => n[0]).join('')}
              </div>
              {#if conversation.recruiter.online}
                <div class="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-white rounded-full"></div>
              {/if}
            </div>

            <div class="flex-1 min-w-0">
              <h1 class="font-bold text-gray-800 text-lg truncate">{conversation.recruiter.name}</h1>
              <p class="text-sm text-gray-600 truncate">
                {conversation.recruiter.position} at {conversation.recruiter.company}
                {#if conversation.recruiter.online}
                  <span class="text-green-600">• Online</span>
                {:else}
                  <span class="text-gray-400">• Offline</span>
                {/if}
              </p>
            </div>
          </div>

          <!-- Right: Action buttons -->
          <div class="flex items-center gap-1">
            <button
              onclick={() => makeCall('voice')}
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Voice call"
            >
              <Phone size={20} class="text-gray-600" />
            </button>
            <button
              onclick={() => makeCall('video')}
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Video call"
            >
              <Video size={20} class="text-gray-600" />
            </button>
            <button
              onclick={() => showRecruiterInfo = !showRecruiterInfo}
              class="p-2 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              title="Conversation info"
            >
              <Info size={20} class="text-gray-600" />
            </button>
          </div>
        </div>

        <!-- Job Context Banner -->
        <div class="pb-4">
          <a
            href="/jobs/{conversation.jobId}"
            class="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors duration-200"
          >
            <span class="text-sm text-blue-700">
              <strong>Job:</strong> {conversation.jobTitle}
            </span>
            <span class="text-blue-400">→</span>
          </a>
        </div>
      </div>
    </section>

    <!-- Main Content Area -->
    <div class="flex-1 flex overflow-hidden bg-gray-50">
      <!-- Messages Area -->
      <div class="flex-1 flex flex-col">
        <!-- Messages -->
        <div id="messages-container" class="flex-1 overflow-y-auto p-4 lg:p-6 space-y-6">
          <div class="max-w-4xl mx-auto space-y-6">
            {#each Object.entries(groupedMessages) as [date, dateMessages]}
              <div class="space-y-4">
                <!-- Date Divider -->
                <div class="flex items-center justify-center">
                  <div class="bg-gray-200 text-gray-600 text-xs px-3 py-1 rounded-full">
                    {date}
                  </div>
                </div>

                <!-- Messages for this date -->
                {#each dateMessages as message (message.id)}
                  <div class="flex" class:justify-end={message.sender === 'me'}>
                    <div class="max-w-[70%] md:max-w-[60%]">
                      <div
                        class="rounded-2xl px-4 py-3"
                        class:bg-blue-600={message.sender === 'me'}
                        class:text-white={message.sender === 'me'}
                        class:bg-white={message.sender === 'recruiter'}
                        class:text-gray-800={message.sender === 'recruiter'}
                        class:shadow-sm={message.sender === 'recruiter'}
                      >
                        <p class="text-sm leading-relaxed whitespace-pre-wrap">{message.text}</p>
                      </div>

                      <div class="flex items-center gap-1 mt-1 px-2" class:justify-end={message.sender === 'me'}>
                        <span class="text-xs text-gray-500">{formatMessageTime(message.timestamp)}</span>
                        {#if message.sender === 'me'}
                          <span class="ml-1">
                            {#if message.read}
                              <CheckCheck size={14} class="text-blue-600" />
                            {:else}
                              <Check size={14} class="text-gray-400" />
                            {/if}
                          </span>
                        {/if}
                      </div>
                    </div>
                  </div>
                {/each}
              </div>
            {/each}
          </div>
        </div>

        <!-- Message Input -->
        <div class="border-t border-gray-200 bg-white">
          <div class="max-w-4xl mx-auto p-4">
            <!-- Attachment Menu -->
            {#if showAttachmentMenu}
              <div class="mb-3 flex items-center gap-2">
                <button
                  onclick={() => attachFile('image')}
                  class="flex items-center gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors duration-200 text-sm"
                >
                  <ImageIcon size={16} />
                  Image
                </button>
                <button
                  onclick={() => attachFile('file')}
                  class="flex items-center gap-2 px-3 py-2 bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-lg transition-colors duration-200 text-sm"
                >
                  <File size={16} />
                  File
                </button>
                <button
                  onclick={() => showAttachmentMenu = false}
                  class="ml-auto text-gray-500 hover:text-gray-700"
                >
                  Cancel
                </button>
              </div>
            {/if}

            <form onsubmit={(e) => { e.preventDefault(); sendMessage(); }} class="flex items-end gap-2">
              <div class="flex-1 relative">
                <textarea
                  bind:value={messageText}
                  onkeypress={handleKeyPress}
                  placeholder="Type your message..."
                  rows="1"
                  class="w-full px-4 py-3 pr-20 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none bg-gray-50 focus:bg-white transition-colors duration-200"
                  style="min-height: 48px; max-height: 120px;"
                ></textarea>

                <div class="absolute bottom-3 right-3 flex items-center gap-1">
                  <button
                    type="button"
                    onclick={() => showAttachmentMenu = !showAttachmentMenu}
                    class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                    title="Attach file"
                  >
                    <Paperclip size={18} />
                  </button>
                  <button
                    type="button"
                    class="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors duration-200"
                    title="Add emoji"
                  >
                    <Smile size={18} />
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={!messageText.trim()}
                class="bg-blue-600 hover:bg-blue-700 text-white font-semibold p-3 rounded-lg transition-colors duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex-shrink-0"
                title="Send message"
              >
                <Send size={20} />
              </button>
            </form>

            <p class="text-xs text-gray-500 mt-2">Press Enter to send, Shift+Enter for new line</p>
          </div>
        </div>
      </div>

      <!-- Recruiter Info Sidebar (Desktop) -->
      {#if showRecruiterInfo}
        <div class="hidden lg:block w-80 border-l border-gray-200 bg-white overflow-y-auto">
          <div class="p-6">
            <div class="flex items-center justify-between mb-6">
              <h3 class="text-lg font-bold text-gray-800">Conversation Info</h3>
              <button
                onclick={() => showRecruiterInfo = false}
                class="p-1 hover:bg-gray-100 rounded-lg transition-colors duration-200"
              >
                <MoreVertical size={20} class="text-gray-600" />
              </button>
            </div>

            <!-- Recruiter Details -->
            <div class="text-center mb-6 pb-6 border-b border-gray-200">
              <div class="w-24 h-24 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4">
                {conversation.recruiter.name.split(' ').map(n => n[0]).join('')}
              </div>
              <h4 class="font-bold text-gray-800 text-lg mb-1">{conversation.recruiter.name}</h4>
              <p class="text-sm text-gray-600 mb-2">{conversation.recruiter.position}</p>
              <p class="text-sm text-gray-600 font-medium">{conversation.recruiter.company}</p>
              {#if conversation.recruiter.online}
                <span class="inline-block mt-2 text-sm text-green-600">• Online</span>
              {:else}
                <span class="inline-block mt-2 text-sm text-gray-400">• Offline</span>
              {/if}
            </div>

            <!-- Contact Info -->
            <div class="space-y-4 mb-6 pb-6 border-b border-gray-200">
              <h4 class="font-semibold text-gray-800 text-sm">Contact Information</h4>
              <div class="space-y-3">
                <div>
                  <p class="text-xs text-gray-500 mb-1">Email</p>
                  <a href="mailto:{conversation.recruiter.email}" class="text-sm text-blue-600 hover:underline">
                    {conversation.recruiter.email}
                  </a>
                </div>
                <div>
                  <p class="text-xs text-gray-500 mb-1">Phone</p>
                  <a href="tel:{conversation.recruiter.phone}" class="text-sm text-blue-600 hover:underline">
                    {conversation.recruiter.phone}
                  </a>
                </div>
              </div>
            </div>

            <!-- Job Info -->
            <div class="space-y-4">
              <h4 class="font-semibold text-gray-800 text-sm">Related Job</h4>
              <a
                href="/jobs/{conversation.jobId}"
                class="block p-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors duration-200"
              >
                <p class="font-semibold text-blue-900 mb-1">{conversation.jobTitle}</p>
                <p class="text-sm text-blue-700">{conversation.recruiter.company}</p>
                <p class="text-xs text-blue-600 mt-2">View job details →</p>
              </a>
            </div>
          </div>
        </div>
      {/if}
    </div>
  </div>

  <!-- Mobile Recruiter Info Modal -->
  {#if showRecruiterInfo}
    <div class="lg:hidden fixed inset-0 bg-black/50 z-50" onclick={() => showRecruiterInfo = false}>
      <div class="absolute bottom-0 left-0 right-0 bg-white rounded-t-2xl p-6 max-h-[80vh] overflow-y-auto" onclick={(e) => e.stopPropagation()}>
        <div class="w-12 h-1 bg-gray-300 rounded-full mx-auto mb-6"></div>

        <!-- Recruiter Details -->
        <div class="text-center mb-6 pb-6 border-b border-gray-200">
          <div class="w-24 h-24 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-2xl mx-auto mb-4">
            {conversation.recruiter.name.split(' ').map(n => n[0]).join('')}
          </div>
          <h4 class="font-bold text-gray-800 text-lg mb-1">{conversation.recruiter.name}</h4>
          <p class="text-sm text-gray-600 mb-2">{conversation.recruiter.position}</p>
          <p class="text-sm text-gray-600 font-medium">{conversation.recruiter.company}</p>
          {#if conversation.recruiter.online}
            <span class="inline-block mt-2 text-sm text-green-600">• Online</span>
          {:else}
            <span class="inline-block mt-2 text-sm text-gray-400">• Offline</span>
          {/if}
        </div>

        <!-- Contact Info -->
        <div class="space-y-4 mb-6 pb-6 border-b border-gray-200">
          <h4 class="font-semibold text-gray-800">Contact Information</h4>
          <div class="space-y-3">
            <div>
              <p class="text-xs text-gray-500 mb-1">Email</p>
              <a href="mailto:{conversation.recruiter.email}" class="text-sm text-blue-600 hover:underline">
                {conversation.recruiter.email}
              </a>
            </div>
            <div>
              <p class="text-xs text-gray-500 mb-1">Phone</p>
              <a href="tel:{conversation.recruiter.phone}" class="text-sm text-blue-600 hover:underline">
                {conversation.recruiter.phone}
              </a>
            </div>
          </div>
        </div>

        <!-- Job Info -->
        <div class="space-y-4">
          <h4 class="font-semibold text-gray-800">Related Job</h4>
          <a
            href="/jobs/{conversation.jobId}"
            class="block p-4 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg transition-colors duration-200"
          >
            <p class="font-semibold text-blue-900 mb-1">{conversation.jobTitle}</p>
            <p class="text-sm text-blue-700">{conversation.recruiter.company}</p>
            <p class="text-xs text-blue-600 mt-2">View job details →</p>
          </a>
        </div>
      </div>
    </div>
  {/if}
{:else}
  <!-- Loading or not found -->
  <div class="flex items-center justify-center min-h-screen bg-gray-50">
    <div class="text-center">
      <p class="text-gray-500">Loading conversation...</p>
    </div>
  </div>
{/if}
