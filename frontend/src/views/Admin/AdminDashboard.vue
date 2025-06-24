<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                Admin Dashboard
              </h1>
              <p class="text-gray-600 dark:text-gray-400">
                System overview and management
              </p>
            </div>
            <div class="flex items-center space-x-3">
              <button
                @click="refreshData"
                :disabled="isLoading"
                class="btn-secondary"
              >
                <ArrowPathIcon class="w-4 h-4 mr-2" :class="{ 'animate-spin': isLoading }" />
                Refresh
              </button>
              <button class="btn-primary">
                <Cog6ToothIcon class="w-4 h-4 mr-2" />
                Settings
              </button>
            </div>
          </div>
        </div>

        <!-- System Health Status -->
        <div class="mb-8">
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">System Health</h2>
              <div class="flex items-center space-x-2">
                <div class="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                <span class="text-sm text-green-600 dark:text-green-400 font-medium">All Systems Operational</span>
              </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div class="text-center">
                <div class="w-16 h-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                  <ServerIcon class="w-8 h-8 text-green-600 dark:text-green-400" />
                </div>
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">API Server</h3>
                <p class="text-xs text-green-600 dark:text-green-400">Online</p>
              </div>
              
              <div class="text-center">
                <div class="w-16 h-16 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CircleStackIcon class="w-8 h-8 text-blue-600 dark:text-blue-400" />
                </div>
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">Database</h3>
                <p class="text-xs text-blue-600 dark:text-blue-400">Connected</p>
              </div>
              
              <div class="text-center">
                <div class="w-16 h-16 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CpuChipIcon class="w-8 h-8 text-purple-600 dark:text-purple-400" />
                </div>
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">AI Service</h3>
                <p class="text-xs text-purple-600 dark:text-purple-400">Active</p>
              </div>
              
              <div class="text-center">
                <div class="w-16 h-16 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center mx-auto mb-3">
                  <CloudIcon class="w-8 h-8 text-orange-600 dark:text-orange-400" />
                </div>
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">Storage</h3>
                <p class="text-xs text-orange-600 dark:text-orange-400">Available</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Key Metrics -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</p>
                <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ adminStore.systemStats.totalUsers || 0 }}</p>
                <p class="text-sm text-green-600 dark:text-green-400 mt-1">
                  <ArrowUpIcon class="w-4 h-4 inline mr-1" />
                  +12% this month
                </p>
              </div>
              <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <UsersIcon class="w-6 h-6 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Sessions</p>
                <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ adminStore.systemStats.activeSessions || 0 }}</p>
                <p class="text-sm text-blue-600 dark:text-blue-400 mt-1">
                  <ArrowUpIcon class="w-4 h-4 inline mr-1" />
                  +5% today
                </p>
              </div>
              <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <ChatBubbleLeftRightIcon class="w-6 h-6 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Messages Today</p>
                <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ adminStore.systemStats.messagesToday || 0 }}</p>
                <p class="text-sm text-purple-600 dark:text-purple-400 mt-1">
                  <ArrowUpIcon class="w-4 h-4 inline mr-1" />
                  +8% vs yesterday
                </p>
              </div>
              <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <PaperAirplaneIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>

          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">System Load</p>
                <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ systemLoad }}%</p>
                <p class="text-sm text-yellow-600 dark:text-yellow-400 mt-1">
                  <ArrowDownIcon class="w-4 h-4 inline mr-1" />
                  -2% vs last hour
                </p>
              </div>
              <div class="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                <ChartBarIcon class="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions & Recent Activity -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <!-- Quick Actions -->
          <div class="card">
            <h2 class="text-xl font-semibold text-gray-900 dark:text-white mb-6">Quick Actions</h2>
            <div class="grid grid-cols-2 gap-4">
              <router-link to="/admin/users" class="admin-action-card">
                <UsersIcon class="w-8 h-8 text-blue-600 dark:text-blue-400 mb-3" />
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">Manage Users</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">View and edit user accounts</p>
              </router-link>
              
              <router-link to="/admin/chats" class="admin-action-card">
                <ChatBubbleLeftRightIcon class="w-8 h-8 text-green-600 dark:text-green-400 mb-3" />
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">Chat Sessions</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">Monitor conversations</p>
              </router-link>
              
              <button @click="viewSystemLogs" class="admin-action-card">
                <DocumentTextIcon class="w-8 h-8 text-purple-600 dark:text-purple-400 mb-3" />
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">System Logs</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">View system activity</p>
              </button>
              
              <router-link to="/admin/settings" class="admin-action-card">
                <Cog6ToothIcon class="w-8 h-8 text-orange-600 dark:text-orange-400 mb-3" />
                <h3 class="text-sm font-medium text-gray-900 dark:text-white">Settings</h3>
                <p class="text-xs text-gray-600 dark:text-gray-400">Configure system</p>
              </router-link>
            </div>
          </div>

          <!-- Recent Activity -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Recent Activity</h2>
              <button class="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300">
                View All
              </button>
            </div>
            
            <div class="space-y-4">
              <div v-for="activity in recentActivities" :key="activity.id" class="flex items-start space-x-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0"
                     :class="getActivityIconBg(activity.type)">
                  <component :is="getActivityIcon(activity.type)" class="w-4 h-4" :class="getActivityIconColor(activity.type)" />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm text-gray-900 dark:text-white">{{ activity.description }}</p>
                  <p class="text-xs text-gray-600 dark:text-gray-400">{{ formatTimeAgo(activity.timestamp) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <!-- User Growth Chart -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">User Growth</h2>
              <select class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option>Last 7 days</option>
                <option>Last 30 days</option>
                <option>Last 90 days</option>
              </select>
            </div>
            <div class="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div class="text-center">
                <ChartBarIcon class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p class="text-gray-600 dark:text-gray-400">Chart will be rendered here</p>
              </div>
            </div>
          </div>

          <!-- Message Volume Chart -->
          <div class="card">
            <div class="flex items-center justify-between mb-6">
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Message Volume</h2>
              <select class="text-sm border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-1 bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
                <option>Today</option>
                <option>This week</option>
                <option>This month</option>
              </select>
            </div>
            <div class="h-64 flex items-center justify-center bg-gray-50 dark:bg-gray-700/50 rounded-lg">
              <div class="text-center">
                <ChartBarIcon class="w-12 h-12 text-gray-400 mx-auto mb-2" />
                <p class="text-gray-600 dark:text-gray-400">Chart will be rendered here</p>
              </div>
            </div>
          </div>
        </div>
      </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import {
  ArrowPathIcon,
  Cog6ToothIcon,
  ServerIcon,
  CircleStackIcon,
  CpuChipIcon,
  CloudIcon,
  UsersIcon,
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  ChartBarIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  DocumentTextIcon,
  UserPlusIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const adminStore = useAdminStore()
const isLoading = ref(false)

const systemLoad = computed(() => {
  return Math.floor(Math.random() * 30) + 45 // Simulated system load
})

const recentActivities = ref([
  {
    id: 1,
    type: 'user_registered',
    description: 'New user john.doe@example.com registered',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: 2,
    type: 'chat_created',
    description: 'New chat session started by user Alice',
    timestamp: new Date(Date.now() - 15 * 60 * 1000)
  },
  {
    id: 3,
    type: 'system_alert',
    description: 'High CPU usage detected on server-01',
    timestamp: new Date(Date.now() - 30 * 60 * 1000)
  },
  {
    id: 4,
    type: 'user_login',
    description: 'Admin user logged in from 192.168.1.100',
    timestamp: new Date(Date.now() - 45 * 60 * 1000)
  },
  {
    id: 5,
    type: 'system_update',
    description: 'System configuration updated successfully',
    timestamp: new Date(Date.now() - 60 * 60 * 1000)
  }
])

const getActivityIcon = (type) => {
  const icons = {
    user_registered: UserPlusIcon,
    chat_created: ChatBubbleLeftRightIcon,
    system_alert: ExclamationTriangleIcon,
    user_login: UsersIcon,
    system_update: CheckCircleIcon
  }
  return icons[type] || CheckCircleIcon
}

const getActivityIconBg = (type) => {
  const backgrounds = {
    user_registered: 'bg-blue-100 dark:bg-blue-900/30',
    chat_created: 'bg-green-100 dark:bg-green-900/30',
    system_alert: 'bg-red-100 dark:bg-red-900/30',
    user_login: 'bg-purple-100 dark:bg-purple-900/30',
    system_update: 'bg-yellow-100 dark:bg-yellow-900/30'
  }
  return backgrounds[type] || 'bg-gray-100 dark:bg-gray-900/30'
}

const getActivityIconColor = (type) => {
  const colors = {
    user_registered: 'text-blue-600 dark:text-blue-400',
    chat_created: 'text-green-600 dark:text-green-400',
    system_alert: 'text-red-600 dark:text-red-400',
    user_login: 'text-purple-600 dark:text-purple-400',
    system_update: 'text-yellow-600 dark:text-yellow-400'
  }
  return colors[type] || 'text-gray-600 dark:text-gray-400'
}

const formatTimeAgo = (timestamp) => {
  const now = new Date()
  const diff = now - timestamp
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  return timestamp.toLocaleDateString()
}

const refreshData = async () => {
  isLoading.value = true
  try {
    await adminStore.fetchSystemStats()
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000))
  } catch (error) {
    console.error('Failed to refresh data:', error)
  } finally {
    isLoading.value = false
  }
}

const viewSystemLogs = () => {
  // This would open a modal or navigate to logs page
  console.log('Opening system logs...')
}

onMounted(() => {
  adminStore.fetchSystemStats()
})
</script>

<style scoped>
.admin-action-card {
  @apply p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200 cursor-pointer text-center block;
}
</style>