import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

export const useAdminStore = defineStore('admin', () => {
  const toast = useToast()
  
  // State
  const users = ref([])
  const chatSessions = ref([])
  const systemStats = ref({
    totalUsers: 0,
    totalSessions: 0,
    totalMessages: 0,
    activeUsers: 0,
    systemHealth: 'healthy'
  })
  const isLoading = ref(false)
  const pagination = ref({
    page: 1,
    limit: 20,
    total: 0,
    totalPages: 0
  })
  
  // Getters
  const activeUsers = computed(() => 
    users.value.filter(user => user.is_active)
  )
  
  const inactiveUsers = computed(() => 
    users.value.filter(user => !user.is_active)
  )
  
  const adminUsers = computed(() => 
    users.value.filter(user => user.role === 'admin')
  )
  
  const recentSessions = computed(() => 
    chatSessions.value
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
      .slice(0, 10)
  )
  
  // Actions
  const fetchSystemStats = async () => {
    try {
      const response = await api.get('/admin/stats')
      systemStats.value = response.data
    } catch (error) {
      console.error('Fetch system stats error:', error)
      toast.error('Failed to load system statistics')
    }
  }
  
  const fetchUsers = async (page = 1, limit = 20, search = '') => {
    try {
      isLoading.value = true
      const params = { page, limit }
      if (search) params.search = search
      
      const response = await api.get('/admin/users', { params })
      
      users.value = response.data.users
      pagination.value = {
        page: response.data.page,
        limit: response.data.limit,
        total: response.data.total,
        totalPages: response.data.total_pages
      }
    } catch (error) {
      console.error('Fetch users error:', error)
      toast.error('Failed to load users')
    } finally {
      isLoading.value = false
    }
  }
  
  const fetchChatSessions = async (page = 1, limit = 20, userId = null) => {
    try {
      isLoading.value = true
      const params = { page, limit }
      if (userId) params.user_id = userId
      
      const response = await api.get('/admin/chat-sessions', { params })
      
      chatSessions.value = response.data.sessions
      pagination.value = {
        page: response.data.page,
        limit: response.data.limit,
        total: response.data.total,
        totalPages: response.data.total_pages
      }
    } catch (error) {
      console.error('Fetch chat sessions error:', error)
      toast.error('Failed to load chat sessions')
    } finally {
      isLoading.value = false
    }
  }
  
  const createUser = async (userData) => {
    try {
      const response = await api.post('/admin/users', userData)
      users.value.unshift(response.data)
      toast.success('User created successfully')
      return response.data
    } catch (error) {
      console.error('Create user error:', error)
      toast.error(error.response?.data?.detail || 'Failed to create user')
      throw error
    }
  }
  
  const updateUser = async (userId, userData) => {
    try {
      const response = await api.put(`/admin/users/${userId}`, userData)
      
      const userIndex = users.value.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        users.value[userIndex] = response.data
      }
      
      toast.success('User updated successfully')
      return response.data
    } catch (error) {
      console.error('Update user error:', error)
      toast.error(error.response?.data?.detail || 'Failed to update user')
      throw error
    }
  }
  
  const deleteUser = async (userId) => {
    try {
      await api.delete(`/admin/users/${userId}`)
      users.value = users.value.filter(u => u.id !== userId)
      toast.success('User deleted successfully')
    } catch (error) {
      console.error('Delete user error:', error)
      toast.error('Failed to delete user')
      throw error
    }
  }
  
  const toggleUserStatus = async (userId, isActive) => {
    try {
      const response = await api.patch(`/admin/users/${userId}/status`, {
        is_active: isActive
      })
      
      const userIndex = users.value.findIndex(u => u.id === userId)
      if (userIndex !== -1) {
        users.value[userIndex] = response.data
      }
      
      toast.success(`User ${isActive ? 'activated' : 'deactivated'} successfully`)
    } catch (error) {
      console.error('Toggle user status error:', error)
      toast.error('Failed to update user status')
      throw error
    }
  }
  
  const resetUserPassword = async (userId) => {
    try {
      const response = await api.post(`/admin/users/${userId}/reset-password`)
      toast.success('Password reset email sent')
      return response.data
    } catch (error) {
      console.error('Reset password error:', error)
      toast.error('Failed to reset user password')
      throw error
    }
  }
  
  const deleteChatSession = async (sessionId) => {
    try {
      await api.delete(`/admin/chat-sessions/${sessionId}`)
      chatSessions.value = chatSessions.value.filter(s => s.id !== sessionId)
      toast.success('Chat session deleted successfully')
    } catch (error) {
      console.error('Delete chat session error:', error)
      toast.error('Failed to delete chat session')
      throw error
    }
  }
  
  const exportUserData = async (userId) => {
    try {
      const response = await api.get(`/admin/users/${userId}/export`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `user-data-${userId}.json`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('User data exported successfully')
    } catch (error) {
      console.error('Export user data error:', error)
      toast.error('Failed to export user data')
    }
  }
  
  const exportSystemData = async (dataType = 'all') => {
    try {
      const response = await api.get(`/admin/export/${dataType}`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `system-${dataType}-${new Date().toISOString().split('T')[0]}.json`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('System data exported successfully')
    } catch (error) {
      console.error('Export system data error:', error)
      toast.error('Failed to export system data')
    }
  }
  
  const getSystemLogs = async (level = 'all', limit = 100) => {
    try {
      const response = await api.get('/admin/logs', {
        params: { level, limit }
      })
      return response.data
    } catch (error) {
      console.error('Get system logs error:', error)
      toast.error('Failed to load system logs')
      throw error
    }
  }
  
  const updateSystemSettings = async (settings) => {
    try {
      const response = await api.put('/admin/settings', settings)
      toast.success('System settings updated successfully')
      return response.data
    } catch (error) {
      console.error('Update system settings error:', error)
      toast.error('Failed to update system settings')
      throw error
    }
  }
  
  const getSystemHealth = async () => {
    try {
      const response = await api.get('/admin/health')
      systemStats.value.systemHealth = response.data.status
      return response.data
    } catch (error) {
      console.error('Get system health error:', error)
      systemStats.value.systemHealth = 'unhealthy'
      throw error
    }
  }
  
  return {
    users,
    chatSessions,
    systemStats,
    isLoading,
    pagination,
    activeUsers,
    inactiveUsers,
    adminUsers,
    recentSessions,
    fetchSystemStats,
    fetchUsers,
    fetchChatSessions,
    createUser,
    updateUser,
    deleteUser,
    toggleUserStatus,
    resetUserPassword,
    deleteChatSession,
    exportUserData,
    exportSystemData,
    getSystemLogs,
    updateSystemSettings,
    getSystemHealth
  }
})