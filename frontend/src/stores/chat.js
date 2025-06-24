import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useToast } from 'vue-toastification'
import api from '@/services/api'
import { io } from 'socket.io-client'

export const useChatStore = defineStore('chat', () => {
  const toast = useToast()
  
  // State
  const sessions = ref([])
  const currentSession = ref(null)
  const messages = ref([])
  const isLoading = ref(false)
  const isTyping = ref(false)
  const socket = ref(null)
  
  // Getters
  const currentSessionId = computed(() => currentSession.value?.id)
  const hasActiveSessions = computed(() => sessions.value.length > 0)
  const sortedSessions = computed(() => 
    sessions.value.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
  )
  
  // Actions
  const initializeSocket = () => {
    if (!socket.value) {
      socket.value = io(import.meta.env.VITE_WEBSOCKET_URL || 'ws://localhost:8080', {
        auth: {
          token: localStorage.getItem('token')
        }
      })
      
      socket.value.on('connect', () => {
        console.log('Connected to chat server')
      })
      
      socket.value.on('disconnect', () => {
        console.log('Disconnected from chat server')
      })
      
      socket.value.on('message', (message) => {
        addMessage(message)
      })
      
      socket.value.on('typing', (data) => {
        isTyping.value = data.typing
      })
    }
  }
  
  const disconnectSocket = () => {
    if (socket.value) {
      socket.value.disconnect()
      socket.value = null
    }
  }
  
  const fetchSessions = async () => {
    try {
      isLoading.value = true
      const response = await api.get('/chat/sessions')
      sessions.value = response.data
    } catch (error) {
      console.error('Fetch sessions error:', error)
      toast.error('Failed to load chat sessions')
    } finally {
      isLoading.value = false
    }
  }
  
  const createSession = async (title = null) => {
    try {
      const response = await api.post('/chat/sessions', {
        title: title || `Chat ${new Date().toLocaleString()}`
      })
      
      const newSession = response.data
      sessions.value.unshift(newSession)
      currentSession.value = newSession
      messages.value = []
      
      return newSession
    } catch (error) {
      console.error('Create session error:', error)
      toast.error('Failed to create chat session')
      throw error
    }
  }
  
  const selectSession = async (sessionId) => {
    try {
      isLoading.value = true
      
      // Find session in local state
      const session = sessions.value.find(s => s.id === sessionId)
      if (session) {
        currentSession.value = session
      }
      
      // Fetch messages for this session
      const response = await api.get(`/chat/sessions/${sessionId}/messages`)
      messages.value = response.data
      
      // Join socket room for this session
      if (socket.value) {
        socket.value.emit('join_session', { session_id: sessionId })
      }
    } catch (error) {
      console.error('Select session error:', error)
      toast.error('Failed to load chat session')
    } finally {
      isLoading.value = false
    }
  }
  
  const sendMessage = async (content) => {
    if (!currentSession.value) {
      // Create a new session if none exists
      await createSession()
    }
    
    try {
      // Add user message immediately
      const userMessage = {
        id: Date.now(), // Temporary ID
        content,
        message_type: 'user',
        created_at: new Date().toISOString(),
        session_id: currentSession.value.id
      }
      
      messages.value.push(userMessage)
      isTyping.value = true
      
      // Send message via API
      const response = await api.post('/chat', {
        message: content,
        session_id: currentSession.value.id
      })
      
      // Update user message with real ID
      const messageIndex = messages.value.findIndex(m => m.id === userMessage.id)
      if (messageIndex !== -1) {
        messages.value[messageIndex] = response.data.user_message
      }
      
      // Add assistant response
      if (response.data.assistant_message) {
        messages.value.push(response.data.assistant_message)
      }
      
      // Update session timestamp
      if (currentSession.value) {
        currentSession.value.updated_at = new Date().toISOString()
      }
      
    } catch (error) {
      console.error('Send message error:', error)
      toast.error('Failed to send message')
      
      // Remove the failed message
      const messageIndex = messages.value.findIndex(m => m.content === content && m.message_type === 'user')
      if (messageIndex !== -1) {
        messages.value.splice(messageIndex, 1)
      }
    } finally {
      isTyping.value = false
    }
  }
  
  const addMessage = (message) => {
    // Avoid duplicates
    const exists = messages.value.some(m => m.id === message.id)
    if (!exists) {
      messages.value.push(message)
    }
  }
  
  const deleteSession = async (sessionId) => {
    try {
      await api.delete(`/chat/sessions/${sessionId}`)
      
      // Remove from local state
      sessions.value = sessions.value.filter(s => s.id !== sessionId)
      
      // Clear current session if it was deleted
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
      
      toast.success('Chat session deleted')
    } catch (error) {
      console.error('Delete session error:', error)
      toast.error('Failed to delete chat session')
    }
  }
  
  const updateSessionTitle = async (sessionId, title) => {
    try {
      const response = await api.put(`/chat/sessions/${sessionId}`, { title })
      
      // Update local state
      const sessionIndex = sessions.value.findIndex(s => s.id === sessionId)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex] = response.data
      }
      
      if (currentSession.value?.id === sessionId) {
        currentSession.value = response.data
      }
      
      toast.success('Session title updated')
    } catch (error) {
      console.error('Update session title error:', error)
      toast.error('Failed to update session title')
    }
  }
  
  const clearCurrentSession = () => {
    currentSession.value = null
    messages.value = []
  }
  
  const exportSession = async (sessionId) => {
    try {
      const response = await api.get(`/chat/sessions/${sessionId}/export`, {
        responseType: 'blob'
      })
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `chat-session-${sessionId}.json`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      toast.success('Chat session exported')
    } catch (error) {
      console.error('Export session error:', error)
      toast.error('Failed to export chat session')
    }
  }
  
  return {
    sessions,
    currentSession,
    messages,
    isLoading,
    isTyping,
    currentSessionId,
    hasActiveSessions,
    sortedSessions,
    initializeSocket,
    disconnectSocket,
    fetchSessions,
    createSession,
    selectSession,
    sendMessage,
    addMessage,
    deleteSession,
    updateSessionTitle,
    clearCurrentSession,
    exportSession
  }
})