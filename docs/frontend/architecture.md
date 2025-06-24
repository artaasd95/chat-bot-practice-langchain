# Frontend Architecture Documentation

This document describes the frontend architecture of the LangGraph Chat Bot System, built with Vue.js 3, TypeScript, and modern web technologies.

## Overview

The frontend is a Single Page Application (SPA) built with:

- **Vue.js 3**: Progressive JavaScript framework with Composition API
- **TypeScript**: Type-safe JavaScript development
- **Vite**: Fast build tool and development server
- **Vue Router**: Client-side routing
- **Pinia**: State management
- **Axios**: HTTP client for API communication
- **Tailwind CSS**: Utility-first CSS framework

## Project Structure

```
frontend/
├── public/                 # Static assets
│   ├── favicon.ico
│   └── index.html
├── src/                   # Source code
│   ├── components/        # Reusable Vue components
│   │   ├── common/        # Common UI components
│   │   ├── chat/          # Chat-specific components
│   │   ├── admin/         # Admin panel components
│   │   └── auth/          # Authentication components
│   ├── views/             # Page-level components
│   │   ├── Auth/          # Authentication pages
│   │   ├── Admin/         # Admin panel pages
│   │   └── *.vue          # Main application pages
│   ├── router/            # Vue Router configuration
│   ├── stores/            # Pinia stores
│   ├── services/          # API services and utilities
│   ├── types/             # TypeScript type definitions
│   ├── utils/             # Utility functions
│   ├── assets/            # Static assets (images, styles)
│   ├── App.vue            # Root component
│   ├── main.ts            # Application entry point
│   └── style.css          # Global styles
├── package.json           # Dependencies and scripts
├── vite.config.ts         # Vite configuration
├── tsconfig.json          # TypeScript configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── eslint.config.js       # ESLint configuration
```

## Core Architecture

### Application Entry Point

```typescript
// src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './style.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
```

### Root Component

```vue
<!-- src/App.vue -->
<template>
  <div id="app" :class="themeClass">
    <!-- Loading Overlay -->
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-spinner"></div>
    </div>
    
    <!-- Main Application -->
    <router-view v-slot="{ Component, route }">
      <transition :name="route.meta.transition || 'fade'" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useThemeStore } from './stores/theme'

const authStore = useAuthStore()
const themeStore = useThemeStore()

const isLoading = computed(() => authStore.isLoading)
const themeClass = computed(() => themeStore.currentTheme)

onMounted(() => {
  // Initialize theme
  themeStore.initializeTheme()
  
  // Check authentication status
  authStore.checkAuthStatus()
})
</script>
```

## Routing Architecture

### Router Configuration

```typescript
// src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  // Authentication Routes
  {
    path: '/auth',
    component: () => import('../views/Auth/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'Login',
        component: () => import('../views/Auth/LoginView.vue'),
        meta: { requiresGuest: true }
      },
      {
        path: 'register',
        name: 'Register',
        component: () => import('../views/Auth/RegisterView.vue'),
        meta: { requiresGuest: true }
      },
      {
        path: 'forgot-password',
        name: 'ForgotPassword',
        component: () => import('../views/Auth/ForgotPasswordView.vue'),
        meta: { requiresGuest: true }
      }
    ]
  },
  
  // Main Application Routes
  {
    path: '/',
    component: () => import('../views/DashboardLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue')
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/ChatView.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('../views/ProfileView.vue')
      }
    ]
  },
  
  // Admin Routes
  {
    path: '/admin',
    component: () => import('../views/Admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: () => import('../views/Admin/AdminDashboard.vue')
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/Admin/AdminUsers.vue')
      },
      {
        path: 'chats',
        name: 'AdminChats',
        component: () => import('../views/Admin/AdminChats.vue')
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/Admin/AdminSettings.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation Guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
    return
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
    return
  }
  
  // Check if route requires admin privileges
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router
```

## State Management

### Pinia Store Architecture

#### Authentication Store

```typescript
// src/stores/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authService } from '../services/auth'
import type { User, LoginCredentials, RegisterData } from '../types/auth'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  // Actions
  const login = async (credentials: LoginCredentials) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authService.login(credentials)
      
      token.value = response.access_token
      localStorage.setItem('token', response.access_token)
      
      await fetchUser()
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Login failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const register = async (data: RegisterData) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authService.register(data)
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Registration failed'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const logout = async () => {
    try {
      if (token.value) {
        await authService.logout()
      }
    } catch (err) {
      console.error('Logout error:', err)
    } finally {
      user.value = null
      token.value = null
      localStorage.removeItem('token')
    }
  }
  
  const fetchUser = async () => {
    try {
      const userData = await authService.getCurrentUser()
      user.value = userData
    } catch (err) {
      console.error('Failed to fetch user:', err)
      await logout()
    }
  }
  
  const checkAuthStatus = async () => {
    if (token.value) {
      await fetchUser()
    }
  }
  
  return {
    // State
    user,
    token,
    isLoading,
    error,
    
    // Getters
    isAuthenticated,
    isAdmin,
    
    // Actions
    login,
    register,
    logout,
    fetchUser,
    checkAuthStatus
  }
})
```

#### Chat Store

```typescript
// src/stores/chat.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatService } from '../services/chat'
import type { ChatSession, ChatMessage, SendMessageRequest } from '../types/chat'

export const useChatStore = defineStore('chat', () => {
  // State
  const sessions = ref<ChatSession[]>([])
  const currentSession = ref<ChatSession | null>(null)
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const isSending = ref(false)
  const error = ref<string | null>(null)
  
  // Getters
  const currentSessionId = computed(() => currentSession.value?.session_id)
  const hasMessages = computed(() => messages.value.length > 0)
  
  // Actions
  const fetchSessions = async () => {
    try {
      isLoading.value = true
      const response = await chatService.getSessions()
      sessions.value = response.sessions
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to fetch sessions'
    } finally {
      isLoading.value = false
    }
  }
  
  const createSession = async (title?: string, initialMessage?: string) => {
    try {
      isLoading.value = true
      const response = await chatService.createSession({ title, initial_message: initialMessage })
      
      sessions.value.unshift(response)
      currentSession.value = response
      
      if (response.first_message && response.ai_response) {
        messages.value = [response.first_message, response.ai_response]
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to create session'
      throw err
    } finally {
      isLoading.value = false
    }
  }
  
  const selectSession = async (sessionId: string) => {
    try {
      isLoading.value = true
      const session = await chatService.getSession(sessionId)
      
      currentSession.value = session
      messages.value = session.messages || []
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to load session'
    } finally {
      isLoading.value = false
    }
  }
  
  const sendMessage = async (content: string) => {
    if (!currentSession.value) {
      throw new Error('No active session')
    }
    
    try {
      isSending.value = true
      
      const response = await chatService.sendMessage(currentSession.value.session_id, {
        message: content
      })
      
      // Add both user message and AI response to messages
      messages.value.push(response.user_message, response.ai_response)
      
      // Update session info
      if (response.session_updated) {
        currentSession.value.message_count = response.session_updated.message_count
        currentSession.value.updated_at = response.session_updated.updated_at
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to send message'
      throw err
    } finally {
      isSending.value = false
    }
  }
  
  const updateSessionTitle = async (sessionId: string, title: string) => {
    try {
      const response = await chatService.updateSessionTitle(sessionId, title)
      
      // Update in sessions list
      const sessionIndex = sessions.value.findIndex(s => s.session_id === sessionId)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].title = title
      }
      
      // Update current session if it's the same
      if (currentSession.value?.session_id === sessionId) {
        currentSession.value.title = title
      }
      
      return response
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to update session title'
      throw err
    }
  }
  
  const deleteSession = async (sessionId: string) => {
    try {
      await chatService.deleteSession(sessionId)
      
      // Remove from sessions list
      sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
      
      // Clear current session if it's the deleted one
      if (currentSession.value?.session_id === sessionId) {
        currentSession.value = null
        messages.value = []
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Failed to delete session'
      throw err
    }
  }
  
  const clearCurrentSession = () => {
    currentSession.value = null
    messages.value = []
  }
  
  return {
    // State
    sessions,
    currentSession,
    messages,
    isLoading,
    isSending,
    error,
    
    // Getters
    currentSessionId,
    hasMessages,
    
    // Actions
    fetchSessions,
    createSession,
    selectSession,
    sendMessage,
    updateSessionTitle,
    deleteSession,
    clearCurrentSession
  }
})
```

## Component Architecture

### Component Categories

#### 1. Layout Components

```vue
<!-- src/components/common/AppLayout.vue -->
<template>
  <div class="app-layout">
    <AppHeader />
    <div class="app-content">
      <AppSidebar v-if="showSidebar" />
      <main class="main-content">
        <slot />
      </main>
    </div>
    <AppFooter v-if="showFooter" />
  </div>
</template>

<script setup lang="ts">
interface Props {
  showSidebar?: boolean
  showFooter?: boolean
}

withDefaults(defineProps<Props>(), {
  showSidebar: true,
  showFooter: true
})
</script>
```

#### 2. Chat Components

```vue
<!-- src/components/chat/ChatMessage.vue -->
<template>
  <div :class="messageClasses">
    <div v-if="message.role === 'user'" class="user-message">
      <div class="message-content">
        {{ message.content }}
      </div>
      <div class="message-meta">
        {{ formatTime(message.timestamp) }}
      </div>
    </div>
    
    <div v-else-if="message.role === 'assistant'" class="assistant-message">
      <div class="message-content">
        <MarkdownRenderer :content="message.content" />
      </div>
      <div class="message-meta">
        {{ formatTime(message.timestamp) }}
        <span v-if="message.metadata?.tokens_used" class="token-count">
          {{ message.metadata.tokens_used }} tokens
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../../types/chat'
import MarkdownRenderer from '../common/MarkdownRenderer.vue'
import { formatTime } from '../../utils/date'

interface Props {
  message: ChatMessage
}

const props = defineProps<Props>()

const messageClasses = computed(() => ({
  'chat-message': true,
  'user-message': props.message.role === 'user',
  'assistant-message': props.message.role === 'assistant',
  'system-message': props.message.role === 'system'
}))
</script>
```

#### 3. Form Components

```vue
<!-- src/components/common/FormInput.vue -->
<template>
  <div class="form-input">
    <label v-if="label" :for="inputId" class="form-label">
      {{ label }}
      <span v-if="required" class="required">*</span>
    </label>
    
    <input
      :id="inputId"
      v-model="inputValue"
      :type="type"
      :placeholder="placeholder"
      :disabled="disabled"
      :class="inputClasses"
      @blur="handleBlur"
      @focus="handleFocus"
    />
    
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
    
    <div v-if="hint" class="hint-message">
      {{ hint }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { generateId } from '../../utils/helpers'

interface Props {
  modelValue: string
  type?: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  error?: string
  hint?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'blur'): void
  (e: 'focus'): void
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text'
})

const emit = defineEmits<Emits>()

const inputId = generateId('input')
const isFocused = ref(false)

const inputValue = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inputClasses = computed(() => ({
  'form-control': true,
  'is-invalid': !!props.error,
  'is-focused': isFocused.value,
  'is-disabled': props.disabled
}))

const handleFocus = () => {
  isFocused.value = true
  emit('focus')
}

const handleBlur = () => {
  isFocused.value = false
  emit('blur')
}
</script>
```

## Service Layer

### API Service Architecture

```typescript
// src/services/api.ts
import axios, { type AxiosInstance, type AxiosRequestConfig } from 'axios'
import { useAuthStore } from '../stores/auth'

class ApiService {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    this.setupInterceptors()
  }
  
  private setupInterceptors() {
    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.token) {
          config.headers.Authorization = `Bearer ${authStore.token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )
    
    // Response interceptor to handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          const authStore = useAuthStore()
          await authStore.logout()
          window.location.href = '/auth/login'
        }
        return Promise.reject(error)
      }
    )
  }
  
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get(url, config)
    return response.data
  }
  
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post(url, data, config)
    return response.data
  }
  
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put(url, data, config)
    return response.data
  }
  
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete(url, config)
    return response.data
  }
}

export const apiService = new ApiService()
```

### Chat Service

```typescript
// src/services/chat.ts
import { apiService } from './api'
import type {
  ChatSession,
  ChatMessage,
  CreateSessionRequest,
  SendMessageRequest,
  SessionsResponse,
  MessageResponse
} from '../types/chat'

class ChatService {
  private baseUrl = '/api/v1/chat'
  
  async getSessions(page = 1, size = 20): Promise<SessionsResponse> {
    return apiService.get(`${this.baseUrl}/sessions`, {
      params: { page, size }
    })
  }
  
  async getSession(sessionId: string): Promise<ChatSession> {
    return apiService.get(`${this.baseUrl}/sessions/${sessionId}`)
  }
  
  async createSession(data: CreateSessionRequest): Promise<ChatSession> {
    return apiService.post(`${this.baseUrl}/sessions`, data)
  }
  
  async sendMessage(sessionId: string, data: SendMessageRequest): Promise<MessageResponse> {
    return apiService.post(`${this.baseUrl}/sessions/${sessionId}/messages`, data)
  }
  
  async updateSessionTitle(sessionId: string, title: string): Promise<{ session_id: string; title: string; updated_at: string }> {
    return apiService.put(`${this.baseUrl}/sessions/${sessionId}/title`, { title })
  }
  
  async deleteSession(sessionId: string): Promise<void> {
    return apiService.delete(`${this.baseUrl}/sessions/${sessionId}`)
  }
  
  async directChat(message: string, context?: any): Promise<any> {
    return apiService.post(`${this.baseUrl}/direct`, {
      message,
      context
    })
  }
}

export const chatService = new ChatService()
```

## Type Definitions

### Core Types

```typescript
// src/types/auth.ts
export interface User {
  id: number
  uuid: string
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  created_at: string
  updated_at: string
  last_login?: string
  avatar_url?: string
  bio?: string
  phone?: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
}

export interface AuthResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}
```

```typescript
// src/types/chat.ts
export interface ChatMessage {
  id: string
  content: string
  role: 'user' | 'assistant' | 'system'
  timestamp: string
  metadata?: {
    model_used?: string
    tokens_used?: {
      input: number
      output: number
      total: number
    }
    processing_time_ms?: number
    [key: string]: any
  }
}

export interface ChatSession {
  session_id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  messages?: ChatMessage[]
  last_message_preview?: string
  last_message_timestamp?: string
}

export interface CreateSessionRequest {
  title?: string
  initial_message?: string
  context?: any
}

export interface SendMessageRequest {
  message: string
  context?: any
}

export interface MessageResponse {
  user_message: ChatMessage
  ai_response: ChatMessage
  session_updated: {
    message_count: number
    updated_at: string
  }
}

export interface SessionsResponse {
  sessions: ChatSession[]
  pagination: {
    total: number
    page: number
    size: number
    pages: number
    has_next: boolean
    has_prev: boolean
  }
}
```

## Build Configuration

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          ui: ['@headlessui/vue', '@heroicons/vue']
        }
      }
    }
  },
  define: {
    __VUE_OPTIONS_API__: false,
    __VUE_PROD_DEVTOOLS__: false
  }
})
```

### TypeScript Configuration

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{"path": "./tsconfig.node.json"}]
}
```

## Performance Optimizations

### Code Splitting

```typescript
// Lazy loading routes
const routes = [
  {
    path: '/chat',
    component: () => import('../views/ChatView.vue')
  },
  {
    path: '/admin',
    component: () => import('../views/Admin/AdminLayout.vue'),
    children: [
      {
        path: 'users',
        component: () => import('../views/Admin/AdminUsers.vue')
      }
    ]
  }
]
```

### Component Optimization

```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Lazy load heavy components
const MarkdownRenderer = defineAsyncComponent(
  () => import('./MarkdownRenderer.vue')
)

const CodeEditor = defineAsyncComponent({
  loader: () => import('./CodeEditor.vue'),
  loadingComponent: LoadingSpinner,
  errorComponent: ErrorComponent,
  delay: 200,
  timeout: 3000
})
</script>
```

### Virtual Scrolling

```vue
<!-- For large message lists -->
<template>
  <VirtualList
    :items="messages"
    :item-height="estimateMessageHeight"
    :buffer="5"
  >
    <template #default="{ item }">
      <ChatMessage :message="item" />
    </template>
  </VirtualList>
</template>
```

## Testing Strategy

### Unit Testing

```typescript
// tests/components/ChatMessage.test.ts
import { mount } from '@vue/test-utils'
import ChatMessage from '@/components/chat/ChatMessage.vue'
import type { ChatMessage as ChatMessageType } from '@/types/chat'

describe('ChatMessage', () => {
  const mockMessage: ChatMessageType = {
    id: '1',
    content: 'Hello, world!',
    role: 'user',
    timestamp: '2024-01-01T12:00:00Z'
  }
  
  it('renders user message correctly', () => {
    const wrapper = mount(ChatMessage, {
      props: { message: mockMessage }
    })
    
    expect(wrapper.text()).toContain('Hello, world!')
    expect(wrapper.classes()).toContain('user-message')
  })
  
  it('renders assistant message with markdown', () => {
    const assistantMessage = {
      ...mockMessage,
      role: 'assistant' as const,
      content: '**Bold text**'
    }
    
    const wrapper = mount(ChatMessage, {
      props: { message: assistantMessage }
    })
    
    expect(wrapper.classes()).toContain('assistant-message')
  })
})
```

### Integration Testing

```typescript
// tests/stores/auth.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'
import { authService } from '@/services/auth'

vi.mock('@/services/auth')

describe('Auth Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })
  
  it('should login successfully', async () => {
    const authStore = useAuthStore()
    const mockResponse = {
      access_token: 'token123',
      refresh_token: 'refresh123',
      token_type: 'bearer',
      expires_in: 1800
    }
    
    vi.mocked(authService.login).mockResolvedValue(mockResponse)
    vi.mocked(authService.getCurrentUser).mockResolvedValue({
      id: 1,
      email: 'test@example.com',
      full_name: 'Test User'
    })
    
    await authStore.login({ username: 'test@example.com', password: 'password' })
    
    expect(authStore.isAuthenticated).toBe(true)
    expect(authStore.token).toBe('token123')
  })
})
```

## Security Considerations

### XSS Prevention

```vue
<template>
  <!-- Always use v-text for user content -->
  <div v-text="userContent"></div>
  
  <!-- Use sanitized HTML for markdown -->
  <div v-html="sanitizedMarkdown"></div>
</template>

<script setup lang="ts">
import DOMPurify from 'dompurify'
import { marked } from 'marked'

const sanitizedMarkdown = computed(() => {
  const html = marked(props.content)
  return DOMPurify.sanitize(html)
})
</script>
```

### CSRF Protection

```typescript
// CSRF token handling
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')

if (csrfToken) {
  apiService.defaults.headers.common['X-CSRF-TOKEN'] = csrfToken
}
```

### Content Security Policy

```html
<!-- In index.html -->
<meta http-equiv="Content-Security-Policy" content="
  default-src 'self';
  script-src 'self' 'unsafe-eval';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data: https:;
  connect-src 'self' ws: wss:;
  font-src 'self';
">
```

This frontend architecture provides a scalable, maintainable, and performant foundation for the Chat Bot System's user interface.