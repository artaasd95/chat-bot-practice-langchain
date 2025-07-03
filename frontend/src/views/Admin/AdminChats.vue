<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Chat Management
              </h1>
              <p class="text-gray-600 dark:text-gray-400">
                Monitor and manage chat sessions
              </p>
            </div>
            <div class="flex items-center space-x-3">
              <button
                @click="exportChats"
                class="btn-secondary"
              >
                <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
                Export
              </button>
              <button
                @click="refreshData"
                :disabled="isLoading"
                class="btn-primary"
              >
                <ArrowPathIcon class="w-4 h-4 mr-2" :class="{ 'animate-spin': isLoading }" />
                Refresh
              </button>
            </div>
          </div>
        </div>

        <!-- Filters and Search -->
        <div class="card mb-8">
          <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
            <!-- Search -->
            <div class="md:col-span-2">
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search by user or session title..."
                  class="input-field pl-10"
                />
                <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>
            
            <!-- Date Range -->
            <div>
              <select v-model="selectedDateRange" class="input-field">
                <option value="">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="custom">Custom Range</option>
              </select>
            </div>
            
            <!-- Status Filter -->
            <div>
              <select v-model="selectedStatus" class="input-field">
                <option value="">All Sessions</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
              </select>
            </div>
            
            <!-- Sort -->
            <div>
              <select v-model="sortBy" class="input-field">
                <option value="updated_at">Last Updated</option>
                <option value="created_at">Created Date</option>
                <option value="message_count">Message Count</option>
                <option value="user_name">User Name</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Chat Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Sessions</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalSessions }}</p>
              </div>
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <ChatBubbleLeftRightIcon class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Sessions</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ activeSessions }}</p>
              </div>
              <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <PlayIcon class="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Messages</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalMessages }}</p>
              </div>
              <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <PaperAirplaneIcon class="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Avg. Session Length</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ avgSessionLength }}</p>
              </div>
              <div class="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                <ClockIcon class="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>
        </div>

        <!-- Chat Sessions Table -->
        <div class="card">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    <input
                      type="checkbox"
                      v-model="selectAll"
                      @change="toggleSelectAll"
                      class="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                    />
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Session
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Messages
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Duration
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Last Activity
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <template v-if="isLoading">
                  <tr v-for="i in 5" :key="i" class="animate-pulse">
                  <td class="px-6 py-4">
                    <div class="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="space-y-2">
                      <div class="w-32 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      <div class="w-24 h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                      <div class="w-20 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-12 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-20 h-6 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex justify-end space-x-2">
                      <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  </td>
                  </tr>
                </template>
                
                <tr v-else v-for="session in filteredSessions" :key="session.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td class="px-6 py-4">
                    <input
                      type="checkbox"
                      v-model="selectedSessions"
                      :value="session.id"
                      class="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                    />
                  </td>
                  <td class="px-6 py-4">
                    <div>
                      <div class="text-sm font-medium text-gray-900 dark:text-white">
                        {{ session.title || 'Untitled Chat' }}
                      </div>
                      <div class="text-sm text-gray-500 dark:text-gray-400">
                        ID: {{ session.id }}
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-8 h-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                        <span class="text-white text-xs font-medium">
                          {{ getUserInitials(session.user?.full_name) }}
                        </span>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ session.user?.full_name || 'Unknown User' }}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">
                          {{ session.user?.email }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center space-x-2">
                      <span class="text-sm font-medium text-gray-900 dark:text-white">
                        {{ session.message_count || 0 }}
                      </span>
                      <ChatBubbleLeftRightIcon class="w-4 h-4 text-gray-400" />
                    </div>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ getSessionDuration(session) }}
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="getSessionStatusClass(session)">
                      {{ getSessionStatus(session) }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(session.updated_at) }}
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex justify-end items-center space-x-2">
                      <button
                        @click="viewSession(session)"
                        class="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
                        title="View session"
                      >
                        <EyeIcon class="w-4 h-4" />
                      </button>
                      <button
                        @click="exportSession(session)"
                        class="p-2 text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition-colors duration-200"
                        title="Export session"
                      >
                        <ArrowDownTrayIcon class="w-4 h-4" />
                      </button>
                      <button
                        @click="deleteSession(session)"
                        class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200"
                        title="Delete session"
                      >
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
                
                <tr v-if="!isLoading && filteredSessions.length === 0">
                  <td colspan="8" class="px-6 py-12 text-center">
                    <ChatBubbleLeftRightIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p class="text-gray-600 dark:text-gray-400">No chat sessions found</p>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Pagination -->
          <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
            <div class="flex items-center justify-between">
              <div class="text-sm text-gray-700 dark:text-gray-300">
                Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalSessions) }} of {{ totalSessions }} results
              </div>
              <div class="flex items-center space-x-2">
                <button
                  @click="currentPage--"
                  :disabled="currentPage === 1"
                  class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Previous
                </button>
                <span class="px-3 py-1 text-sm bg-primary-600 text-white rounded-md">
                  {{ currentPage }}
                </span>
                <button
                  @click="currentPage++"
                  :disabled="currentPage === totalPages"
                  class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Session Detail Modal -->
        <div v-if="showSessionModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg w-full max-w-4xl mx-4 h-5/6 flex flex-col">
        <div class="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
              {{ selectedSession?.title || 'Untitled Chat' }}
            </h3>
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ selectedSession?.user?.full_name }} • {{ formatDate(selectedSession?.created_at) }}
            </p>
          </div>
          <button
            @click="closeSessionModal"
            class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <XMarkIcon class="w-6 h-6" />
          </button>
        </div>
        
        <div class="flex-1 overflow-y-auto p-6">
          <div class="space-y-4">
            <div v-for="message in sessionMessages" :key="message.id" class="flex" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
              <div class="max-w-3xl">
                <div class="flex items-center space-x-2 mb-1">
                  <span class="text-xs font-medium text-gray-600 dark:text-gray-400">
                    {{ message.role === 'user' ? 'User' : 'Assistant' }}
                  </span>
                  <span class="text-xs text-gray-500 dark:text-gray-500">
                    {{ formatTime(message.created_at) }}
                  </span>
                </div>
                <div class="message-bubble" :class="message.role === 'user' ? 'message-bubble-user' : 'message-bubble-assistant'">
                  <p class="whitespace-pre-wrap">{{ message.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="p-6 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-end space-x-3">
            <button
              @click="exportSession(selectedSession)"
              class="btn-secondary"
            >
              <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
              Export
            </button>
            <button
              @click="closeSessionModal"
              class="btn-primary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import {
  ArrowDownTrayIcon,
  ArrowPathIcon,
  MagnifyingGlassIcon,
  ChatBubbleLeftRightIcon,
  PlayIcon,
  PaperAirplaneIcon,
  ClockIcon,
  EyeIcon,
  TrashIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const adminStore = useAdminStore()

const isLoading = ref(false)
const showSessionModal = ref(false)
const selectAll = ref(false)
const selectedSessions = ref([])
const selectedSession = ref(null)
const sessionMessages = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

const searchQuery = ref('')
const selectedDateRange = ref('')
const selectedStatus = ref('')
const sortBy = ref('updated_at')

const filteredSessions = computed(() => {
  let sessions = adminStore.chatSessions || []
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    sessions = sessions.filter(session => 
      session.title?.toLowerCase().includes(query) ||
      session.user?.full_name?.toLowerCase().includes(query) ||
      session.user?.email?.toLowerCase().includes(query)
    )
  }
  
  if (selectedDateRange.value) {
    const now = new Date()
    let startDate
    
    switch (selectedDateRange.value) {
      case 'today':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate())
        break
      case 'week':
        startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        startDate = new Date(now.getFullYear(), now.getMonth(), 1)
        break
    }
    
    if (startDate) {
      sessions = sessions.filter(session => new Date(session.created_at) >= startDate)
    }
  }
  
  if (selectedStatus.value) {
    sessions = sessions.filter(session => {
      const status = getSessionStatus(session)
      return status.toLowerCase() === selectedStatus.value
    })
  }
  
  // Sort sessions
  sessions.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_at':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'message_count':
        return (b.message_count || 0) - (a.message_count || 0)
      case 'user_name':
        return (a.user?.full_name || '').localeCompare(b.user?.full_name || '')
      default: // updated_at
        return new Date(b.updated_at) - new Date(a.updated_at)
    }
  })
  
  return sessions
})

const totalSessions = computed(() => filteredSessions.value.length)
const activeSessions = computed(() => filteredSessions.value.filter(session => getSessionStatus(session) === 'Active').length)
const totalMessages = computed(() => filteredSessions.value.reduce((sum, session) => sum + (session.message_count || 0), 0))
const avgSessionLength = computed(() => {
  const sessions = filteredSessions.value.filter(session => session.message_count > 0)
  if (sessions.length === 0) return '0 min'
  const avgMinutes = sessions.reduce((sum, session) => {
    const duration = getSessionDurationMinutes(session)
    return sum + duration
  }, 0) / sessions.length
  return `${Math.round(avgMinutes)} min`
})

const totalPages = computed(() => Math.ceil(totalSessions.value / pageSize.value))

const getUserInitials = (fullName) => {
  if (!fullName) return 'U'
  return fullName
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const formatTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleTimeString()
}

const getSessionDuration = (session) => {
  const minutes = getSessionDurationMinutes(session)
  if (minutes < 60) return `${minutes}m`
  const hours = Math.floor(minutes / 60)
  const remainingMinutes = minutes % 60
  return `${hours}h ${remainingMinutes}m`
}

const getSessionDurationMinutes = (session) => {
  if (!session.created_at || !session.updated_at) return 0
  const start = new Date(session.created_at)
  const end = new Date(session.updated_at)
  return Math.floor((end - start) / (1000 * 60))
}

const getSessionStatus = (session) => {
  if (!session.updated_at) return 'Unknown'
  const lastActivity = new Date(session.updated_at)
  const now = new Date()
  const hoursSinceActivity = (now - lastActivity) / (1000 * 60 * 60)
  
  if (hoursSinceActivity < 1) return 'Active'
  if (hoursSinceActivity < 24) return 'Recent'
  return 'Completed'
}

const getSessionStatusClass = (session) => {
  const status = getSessionStatus(session)
  switch (status) {
    case 'Active':
      return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
    case 'Recent':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
    case 'Completed':
      return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'
    default:
      return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  }
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedSessions.value = filteredSessions.value.map(session => session.id)
  } else {
    selectedSessions.value = []
  }
}

const viewSession = async (session) => {
  selectedSession.value = session
  showSessionModal.value = true
  
  try {
    // Fetch session messages
    sessionMessages.value = await adminStore.getSessionMessages(session.id)
  } catch (error) {
    console.error('Failed to fetch session messages:', error)
    sessionMessages.value = []
  }
}

const closeSessionModal = () => {
  showSessionModal.value = false
  selectedSession.value = null
  sessionMessages.value = []
}

const exportSession = async (session) => {
  try {
    await adminStore.exportSession(session.id)
  } catch (error) {
    console.error('Failed to export session:', error)
  }
}

const deleteSession = async (session) => {
  if (confirm(`Are you sure you want to delete this chat session?`)) {
    try {
      await adminStore.deleteSession(session.id)
    } catch (error) {
      console.error('Failed to delete session:', error)
    }
  }
}

const exportChats = async () => {
  try {
    await adminStore.exportSessions()
  } catch (error) {
    console.error('Failed to export chats:', error)
  }
}

const refreshData = async () => {
  isLoading.value = true
  try {
    await adminStore.fetchChatSessions()
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    isLoading.value = false
  }
}

watch(selectedSessions, (newVal) => {
  selectAll.value = newVal.length === filteredSessions.value.length && newVal.length > 0
})

onMounted(() => {
  adminStore.fetchChatSessions()
})
</script>