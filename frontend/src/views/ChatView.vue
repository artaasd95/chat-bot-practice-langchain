<template>
  <div class="flex h-[calc(100vh-4rem)] max-w-7xl mx-auto">
        <!-- Chat Sidebar -->
        <div class="w-80 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <!-- Sidebar Header -->
          <div class="p-4 border-b border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Chat Sessions</h2>
              <button
                @click="createNewSession"
                class="p-2 rounded-lg bg-primary-600 hover:bg-primary-700 text-white transition-colors duration-200"
                title="New Chat"
              >
                <PlusIcon class="w-4 h-4" />
              </button>
            </div>
            
            <!-- Search Sessions -->
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search conversations..."
                class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>

          <!-- Sessions List -->
          <div class="flex-1 overflow-y-auto">
            <div v-if="isLoading" class="p-4">
              <div class="space-y-3">
                <div v-for="i in 3" :key="i" class="animate-pulse">
                  <div class="h-16 bg-gray-200 dark:bg-gray-700 rounded-lg"></div>
                </div>
              </div>
            </div>

            <div v-else-if="filteredSessions.length === 0" class="p-4 text-center">
              <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p class="text-gray-600 dark:text-gray-400 mb-4">
                {{ searchQuery ? 'No sessions found' : 'No conversations yet' }}
              </p>
              <button @click="createNewSession" class="btn-primary">
                Start your first chat
              </button>
            </div>

            <div v-else class="p-2">
              <div
                v-for="session in filteredSessions"
                :key="session.id"
                class="session-item"
                :class="{ 'session-item-active': currentSessionId === session.id }"
                @click="selectSession(session.id)"
              >
                <div class="flex items-start space-x-3">
                  <div class="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <ChatBubbleLeftRightIcon class="w-5 h-5 text-white" />
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {{ session.title || 'Untitled Chat' }}
                    </h3>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {{ formatDate(session.updated_at) }}
                    </p>
                  </div>
                  <div class="flex items-center space-x-1">
                    <button
                      @click.stop="editSessionTitle(session)"
                      class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                      title="Edit title"
                    >
                      <PencilIcon class="w-3 h-3 text-gray-400" />
                    </button>
                    <button
                      @click.stop="deleteSession(session.id)"
                      class="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                      title="Delete session"
                    >
                      <TrashIcon class="w-3 h-3 text-red-400" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Area -->
        <div class="flex-1 flex flex-col">
          <!-- Chat Header -->
          <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <div class="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                  <ChatBubbleLeftRightIcon class="w-4 h-4 text-white" />
                </div>
                <div>
                  <h1 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ currentSession?.title || 'New Chat' }}
                  </h1>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ messages.length }} messages
                  </p>
                </div>
              </div>
              
              <div class="flex items-center space-x-2">
                <button
                  v-if="currentSession"
                  @click="exportSession"
                  class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                  title="Export chat"
                >
                  <ArrowDownTrayIcon class="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </button>
                <button
                  @click="clearChat"
                  class="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200"
                  title="Clear chat"
                >
                  <TrashIcon class="w-4 h-4 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
            </div>
          </div>

          <!-- Messages Area -->
          <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="messagesContainer">
            <div v-if="messages.length === 0" class="text-center py-12">
              <div class="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <ChatBubbleLeftRightIcon class="w-8 h-8 text-white" />
              </div>
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Start a conversation
              </h3>
              <p class="text-gray-600 dark:text-gray-400 mb-6">
                Ask me anything! I'm here to help with your questions.
              </p>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
                <button
                  v-for="suggestion in suggestions"
                  :key="suggestion"
                  @click="sendMessage(suggestion)"
                  class="p-3 text-left bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200"
                >
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ suggestion }}</span>
                </button>
              </div>
            </div>

            <div v-else>
              <div
                v-for="message in messages"
                :key="message.id"
                class="message-bubble"
                :class="{
                  'message-user': message.message_type === 'user',
                  'message-assistant': message.message_type === 'assistant'
                }"
              >
                <div class="flex items-start space-x-3">
                  <div class="message-avatar">
                    <UserIcon v-if="message.message_type === 'user'" class="w-4 h-4" />
                    <div v-else class="w-6 h-6 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                      <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                      </svg>
                    </div>
                  </div>
                  <div class="message-content">
                    <div class="message-text" v-html="formatMessage(message.content)"></div>
                    <div class="message-time">
                      {{ formatTime(message.created_at) }}
                    </div>
                  </div>
                </div>
              </div>

              <!-- Typing Indicator -->
              <div v-if="isTyping" class="message-bubble message-assistant">
                <div class="flex items-start space-x-3">
                  <div class="message-avatar">
                    <div class="w-6 h-6 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                      <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
                      </svg>
                    </div>
                  </div>
                  <div class="message-content">
                    <div class="typing-indicator">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Message Input -->
          <div class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4">
            <form @submit.prevent="handleSendMessage" class="flex items-end space-x-3">
              <div class="flex-1">
                <textarea
                  v-model="messageInput"
                  @keydown.enter.exact.prevent="handleSendMessage"
                  @keydown.enter.shift.exact="messageInput += '\n'"
                  placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
                  rows="1"
                  class="w-full resize-none border border-gray-300 dark:border-gray-600 rounded-lg px-4 py-3 bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent max-h-32"
                  :disabled="isLoading"
                  ref="messageInputRef"
                ></textarea>
              </div>
              <button
                type="submit"
                :disabled="!messageInput.trim() || isLoading"
                class="p-3 rounded-lg bg-primary-600 hover:bg-primary-700 disabled:bg-gray-300 dark:disabled:bg-gray-600 text-white transition-colors duration-200 flex-shrink-0"
              >
                <PaperAirplaneIcon class="w-5 h-5" />
              </button>
            </form>
          </div>
        </div>
      </div>

    <!-- Edit Session Title Modal -->
    <div v-if="editingSession" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Edit Session Title</h3>
        <input
          v-model="editTitle"
          type="text"
          class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="Enter session title"
          @keydown.enter="saveSessionTitle"
          ref="editTitleInput"
        />
        <div class="flex justify-end space-x-3 mt-4">
          <button
            @click="cancelEditTitle"
            class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
          >
            Cancel
          </button>
          <button
            @click="saveSessionTitle"
            class="btn-primary"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'

import {
  PlusIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  PencilIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  UserIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const chatStore = useChatStore()

const searchQuery = ref('')
const messageInput = ref('')
const messagesContainer = ref(null)
const messageInputRef = ref(null)
const editingSession = ref(null)
const editTitle = ref('')
const editTitleInput = ref(null)

const suggestions = [
  "What can you help me with?",
  "Explain quantum computing",
  "Write a creative story",
  "Help me plan my day"
]

const { sessions, currentSession, messages, isLoading, isTyping, currentSessionId } = chatStore

const filteredSessions = computed(() => {
  if (!searchQuery.value) return chatStore.sortedSessions
  
  return chatStore.sortedSessions.filter(session => 
    session.title?.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diffTime = Math.abs(now - date)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 1) {
    return 'Today'
  } else if (diffDays === 2) {
    return 'Yesterday'
  } else if (diffDays < 7) {
    return `${diffDays - 1} days ago`
  } else {
    return date.toLocaleDateString()
  }
}

const formatTime = (dateString) => {
  return new Date(dateString).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const formatMessage = (content) => {
  // Simple markdown-like formatting
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm">$1</code>')
    .replace(/\n/g, '<br>')
}

const createNewSession = async () => {
  try {
    await chatStore.createSession()
    scrollToBottom()
  } catch (error) {
    console.error('Failed to create session:', error)
  }
}

const selectSession = async (sessionId) => {
  try {
    await chatStore.selectSession(sessionId)
    router.push({ query: { session: sessionId } })
    scrollToBottom()
  } catch (error) {
    console.error('Failed to select session:', error)
  }
}

const handleSendMessage = async () => {
  if (!messageInput.value.trim()) return
  
  const message = messageInput.value.trim()
  messageInput.value = ''
  
  try {
    await chatStore.sendMessage(message)
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const sendMessage = async (message) => {
  try {
    await chatStore.sendMessage(message)
    scrollToBottom()
  } catch (error) {
    console.error('Failed to send message:', error)
  }
}

const deleteSession = async (sessionId) => {
  if (confirm('Are you sure you want to delete this chat session?')) {
    try {
      await chatStore.deleteSession(sessionId)
      if (currentSessionId === sessionId) {
        router.push({ query: {} })
      }
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }
}

const editSessionTitle = (session) => {
  editingSession.value = session
  editTitle.value = session.title || ''
  nextTick(() => {
    editTitleInput.value?.focus()
  })
}

const saveSessionTitle = async () => {
  if (!editingSession.value || !editTitle.value.trim()) return
  
  try {
    await chatStore.updateSessionTitle(editingSession.value.id, editTitle.value.trim())
    cancelEditTitle()
  } catch (error) {
    console.error('Failed to update session title:', error)
  }
}

const cancelEditTitle = () => {
  editingSession.value = null
  editTitle.value = ''
}

const clearChat = () => {
  if (confirm('Are you sure you want to clear this chat?')) {
    chatStore.clearCurrentSession()
  }
}

const exportSession = async () => {
  if (!currentSession) return
  
  try {
    await chatStore.exportSession(currentSession.id)
  } catch (error) {
    console.error('Failed to export session:', error)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const autoResizeTextarea = () => {
  const textarea = messageInputRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    textarea.style.height = Math.min(textarea.scrollHeight, 128) + 'px'
  }
}

watch(() => messageInput.value, autoResizeTextarea)
watch(() => messages.length, scrollToBottom)

onMounted(async () => {
  // Initialize socket connection
  chatStore.initializeSocket()
  
  // Load sessions
  await chatStore.fetchSessions()
  
  // Load specific session if provided in query
  const sessionId = route.query.session
  if (sessionId && sessions.find(s => s.id === sessionId)) {
    await chatStore.selectSession(sessionId)
  }
  
  scrollToBottom()
})

onUnmounted(() => {
  chatStore.disconnectSocket()
})
</script>

<style scoped>
.session-item {
  @apply p-3 rounded-lg cursor-pointer transition-colors duration-200 hover:bg-gray-100 dark:hover:bg-gray-700;
}

.session-item-active {
  @apply bg-primary-100 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800;
}

.message-bubble {
  @apply max-w-none;
}

.message-user {
  @apply ml-12;
}

.message-user .message-avatar {
  @apply w-6 h-6 bg-gray-600 dark:bg-gray-400 rounded-full flex items-center justify-center text-white;
}

.message-assistant {
  @apply mr-12;
}

.message-content {
  @apply flex-1;
}

.message-text {
  @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 text-gray-900 dark:text-white;
}

.message-user .message-text {
  @apply bg-primary-600 text-white border-primary-600;
}

.message-time {
  @apply text-xs text-gray-500 dark:text-gray-400 mt-2;
}

.typing-indicator {
  @apply flex space-x-1 p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg;
}

.typing-indicator div {
  @apply w-2 h-2 bg-gray-400 rounded-full animate-pulse;
}

.typing-indicator div:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator div:nth-child(3) {
  animation-delay: 0.4s;
}
</style>