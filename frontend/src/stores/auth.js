import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'
import api from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const toast = useToast()
  
  // State
  const user = ref(null)
  const token = ref(localStorage.getItem('token'))
  const refreshToken = ref(localStorage.getItem('refreshToken'))
  const isLoading = ref(false)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  // Actions
  const setTokens = (accessToken, refreshTokenValue) => {
    token.value = accessToken
    refreshToken.value = refreshTokenValue
    localStorage.setItem('token', accessToken)
    localStorage.setItem('refreshToken', refreshTokenValue)
    api.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`
  }
  
  const clearTokens = () => {
    token.value = null
    refreshToken.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('refreshToken')
    delete api.defaults.headers.common['Authorization']
  }
  
  const login = async (credentials) => {
    try {
      isLoading.value = true
      const formData = new FormData()
      formData.append('username', credentials.email)
      formData.append('password', credentials.password)
      
      const response = await api.post('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      })
      
      const { access_token, refresh_token } = response.data
      setTokens(access_token, refresh_token)
      
      // Get user profile
      await getCurrentUser()
      
      toast.success('Welcome back!')
      router.push('/dashboard')
      
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Login failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  const register = async (userData) => {
    try {
      isLoading.value = true
      const response = await api.post('/auth/register', userData)
      
      toast.success('Account created successfully! Please log in.')
      router.push('/auth/login')
      
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.detail || 'Registration failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = async () => {
    try {
      if (token.value) {
        await api.post('/auth/logout')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      clearTokens()
      toast.info('You have been logged out')
      router.push('/auth/login')
    }
  }
  
  const getCurrentUser = async () => {
    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      return response.data
    } catch (error) {
      console.error('Get current user error:', error)
      if (error.response?.status === 401) {
        clearTokens()
      }
      throw error
    }
  }
  
  const updateProfile = async (profileData) => {
    try {
      isLoading.value = true
      const response = await api.put('/auth/profile', profileData)
      user.value = { ...user.value, ...response.data }
      toast.success('Profile updated successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const message = error.response?.data?.detail || 'Profile update failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  const changePassword = async (passwordData) => {
    try {
      isLoading.value = true
      await api.post('/auth/change-password', passwordData)
      toast.success('Password changed successfully')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.detail || 'Password change failed'
      toast.error(message)
      return { success: false, error: message }
    } finally {
      isLoading.value = false
    }
  }
  
  const refreshAccessToken = async () => {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available')
      }
      
      const response = await api.post('/auth/refresh', {
        refresh_token: refreshToken.value
      })
      
      const { access_token } = response.data
      token.value = access_token
      localStorage.setItem('token', access_token)
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      
      return access_token
    } catch (error) {
      clearTokens()
      router.push('/auth/login')
      throw error
    }
  }
  
  const initializeAuth = async () => {
    if (token.value) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
      try {
        await getCurrentUser()
      } catch (error) {
        if (refreshToken.value) {
          try {
            await refreshAccessToken()
            await getCurrentUser()
          } catch (refreshError) {
            clearTokens()
          }
        } else {
          clearTokens()
        }
      }
    }
  }
  
  return {
    user,
    token,
    isLoading,
    isAuthenticated,
    isAdmin,
    login,
    register,
    logout,
    getCurrentUser,
    updateProfile,
    changePassword,
    refreshAccessToken,
    initializeAuth
  }
})