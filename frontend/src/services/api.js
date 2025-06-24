import axios from 'axios'
import { useToast } from 'vue-toastification'

// Create axios instance
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const toast = useToast()
    const originalRequest = error.config
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      // Try to refresh token
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const response = await axios.post(
            `${import.meta.env.VITE_API_URL || 'http://localhost:8080/api'}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          
          const { access_token } = response.data
          localStorage.setItem('token', access_token)
          
          // Retry original request
          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('token')
          localStorage.removeItem('refreshToken')
          localStorage.removeItem('user')
          
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
          
          return Promise.reject(refreshError)
        }
      } else {
        // No refresh token, redirect to login
        localStorage.removeItem('token')
        localStorage.removeItem('refreshToken')
        localStorage.removeItem('user')
        
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
    }
    
    // Handle other errors
    if (error.response?.status === 403) {
      toast.error('Access denied. You do not have permission to perform this action.')
    } else if (error.response?.status === 404) {
      toast.error('Resource not found.')
    } else if (error.response?.status === 422) {
      // Validation errors
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach(err => {
          toast.error(`${err.loc?.join(' → ') || 'Field'}: ${err.msg}`)
        })
      } else if (typeof detail === 'string') {
        toast.error(detail)
      } else {
        toast.error('Validation error occurred.')
      }
    } else if (error.response?.status === 429) {
      toast.error('Too many requests. Please try again later.')
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      toast.error('Request timeout. Please check your connection.')
    } else if (!error.response) {
      toast.error('Network error. Please check your connection.')
    }
    
    return Promise.reject(error)
  }
)

// API endpoints
export const authAPI = {
  login: (credentials) => api.post('/auth/login', credentials),
  register: (userData) => api.post('/auth/register', userData),
  logout: () => api.post('/auth/logout'),
  refreshToken: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  getCurrentUser: () => api.get('/auth/me'),
  updateProfile: (userData) => api.put('/auth/profile', userData),
  changePassword: (passwordData) => api.put('/auth/password', passwordData),
  forgotPassword: (email) => api.post('/auth/forgot-password', { email }),
  resetPassword: (token, password) => api.post('/auth/reset-password', { token, password })
}

export const chatAPI = {
  getSessions: () => api.get('/chat/sessions'),
  createSession: (data) => api.post('/chat/sessions', data),
  getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
  updateSession: (sessionId, data) => api.put(`/chat/sessions/${sessionId}`, data),
  deleteSession: (sessionId) => api.delete(`/chat/sessions/${sessionId}`),
  getMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`),
  sendMessage: (data) => api.post('/chat', data),
  exportSession: (sessionId) => api.get(`/chat/sessions/${sessionId}/export`, { responseType: 'blob' })
}

export const adminAPI = {
  getStats: () => api.get('/admin/stats'),
  getUsers: (params) => api.get('/admin/users', { params }),
  createUser: (userData) => api.post('/admin/users', userData),
  updateUser: (userId, userData) => api.put(`/admin/users/${userId}`, userData),
  deleteUser: (userId) => api.delete(`/admin/users/${userId}`),
  toggleUserStatus: (userId, isActive) => api.patch(`/admin/users/${userId}/status`, { is_active: isActive }),
  resetUserPassword: (userId) => api.post(`/admin/users/${userId}/reset-password`),
  exportUserData: (userId) => api.get(`/admin/users/${userId}/export`, { responseType: 'blob' }),
  getChatSessions: (params) => api.get('/admin/chat-sessions', { params }),
  deleteChatSession: (sessionId) => api.delete(`/admin/chat-sessions/${sessionId}`),
  exportSystemData: (dataType) => api.get(`/admin/export/${dataType}`, { responseType: 'blob' }),
  getLogs: (params) => api.get('/admin/logs', { params }),
  updateSettings: (settings) => api.put('/admin/settings', settings),
  getHealth: () => api.get('/admin/health')
}

export default api