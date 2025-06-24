<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Welcome Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Welcome back, {{ authStore.user?.full_name?.split(' ')[0] || 'User' }}! 👋
          </h1>
          <p class="text-gray-600 dark:text-gray-400">
            Ready to continue your AI conversations?
          </p>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div class="card hover:shadow-lg transition-shadow duration-200 cursor-pointer" @click="startNewChat">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <PlusIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">New Chat</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Start a conversation</p>
              </div>
            </div>
          </div>

          <div class="card hover:shadow-lg transition-shadow duration-200 cursor-pointer" @click="$router.push('/chat')">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-xl flex items-center justify-center">
                <ChatBubbleLeftRightIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Recent Chats</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ chatStore.sessions.length }} sessions</p>
              </div>
            </div>
          </div>

          <div class="card hover:shadow-lg transition-shadow duration-200 cursor-pointer" @click="$router.push('/profile')">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl flex items-center justify-center">
                <UserIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Profile</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">Manage account</p>
              </div>
            </div>
          </div>

          <div v-if="authStore.isAdmin" class="card hover:shadow-lg transition-shadow duration-200 cursor-pointer" @click="$router.push('/admin')">
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <ShieldCheckIcon class="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Admin Panel</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400">System management</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Stats Overview -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Conversations</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ chatStore.sessions.length }}</p>
              </div>
              <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ChatBubbleLeftRightIcon class="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Messages Sent</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalMessages }}</p>
              </div>
              <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <PaperAirplaneIcon class="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Since</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ memberSince }}</p>
              </div>
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <CalendarIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Chat Sessions -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- Recent Conversations -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Recent Conversations</h2>
              <router-link
                to="/chat"
                class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 text-sm font-medium"
              >
                View all
              </router-link>
            </div>

            <div v-if="recentSessions.length === 0" class="text-center py-8">
              <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p class="text-gray-600 dark:text-gray-400 mb-4">No conversations yet</p>
              <button @click="startNewChat" class="btn-primary">
                Start your first chat
              </button>
            </div>

            <div v-else class="space-y-4">
              <div
                v-for="session in recentSessions"
                :key="session.id"
                class="flex items-center space-x-4 p-4 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 cursor-pointer"
                @click="openChat(session.id)"
              >
                <div class="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
                  <ChatBubbleLeftRightIcon class="w-5 h-5 text-white" />
                </div>
                <div class="flex-1 min-w-0">
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                    {{ session.title || 'Untitled Chat' }}
                  </h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">
                    {{ formatDate(session.updated_at) }}
                  </p>
                </div>
                <ChevronRightIcon class="w-4 h-4 text-gray-400" />
              </div>
            </div>
          </div>

          <!-- Quick Tips -->
          <div class="card">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Quick Tips</h2>
            
            <div class="space-y-4">
              <div class="flex items-start space-x-3">
                <div class="w-6 h-6 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mt-0.5">
                  <span class="text-xs font-bold text-blue-600 dark:text-blue-400">1</span>
                </div>
                <div>
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white">Be specific with your questions</h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">The more context you provide, the better the AI can help you.</p>
                </div>
              </div>

              <div class="flex items-start space-x-3">
                <div class="w-6 h-6 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mt-0.5">
                  <span class="text-xs font-bold text-green-600 dark:text-green-400">2</span>
                </div>
                <div>
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white">Use follow-up questions</h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">Build on previous responses to dive deeper into topics.</p>
                </div>
              </div>

              <div class="flex items-start space-x-3">
                <div class="w-6 h-6 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mt-0.5">
                  <span class="text-xs font-bold text-purple-600 dark:text-purple-400">3</span>
                </div>
                <div>
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white">Organize with sessions</h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">Create different chat sessions for different topics.</p>
                </div>
              </div>

              <div class="flex items-start space-x-3">
                <div class="w-6 h-6 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mt-0.5">
                  <span class="text-xs font-bold text-orange-600 dark:text-orange-400">4</span>
                </div>
                <div>
                  <h3 class="text-sm font-medium text-gray-900 dark:text-white">Export your conversations</h3>
                  <p class="text-xs text-gray-600 dark:text-gray-400">Save important conversations for future reference.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import {
  PlusIcon,
  ChatBubbleLeftRightIcon,
  UserIcon,
  ShieldCheckIcon,
  PaperAirplaneIcon,
  CalendarIcon,
  ChevronRightIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const chatStore = useChatStore()

const recentSessions = computed(() => {
  return chatStore.sortedSessions.slice(0, 5)
})

const totalMessages = computed(() => {
  return chatStore.sessions.reduce((total, session) => {
    return total + (session.message_count || 0)
  }, 0)
})

const memberSince = computed(() => {
  if (!authStore.user?.created_at) return 'Recently'
  
  const createdDate = new Date(authStore.user.created_at)
  const now = new Date()
  const diffTime = Math.abs(now - createdDate)
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays < 30) {
    return `${diffDays}d`
  } else if (diffDays < 365) {
    return `${Math.floor(diffDays / 30)}mo`
  } else {
    return `${Math.floor(diffDays / 365)}y`
  }
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

const startNewChat = async () => {
  try {
    await chatStore.createSession()
    router.push('/chat')
  } catch (error) {
    console.error('Failed to create new chat:', error)
  }
}

const openChat = (sessionId) => {
  router.push(`/chat?session=${sessionId}`)
}

onMounted(async () => {
  // Load chat sessions if not already loaded
  if (chatStore.sessions.length === 0) {
    await chatStore.fetchSessions()
  }
})
</script>