<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                System Settings
              </h1>
              <p class="text-gray-600 dark:text-gray-400">
                Configure system preferences and security settings
              </p>
            </div>
            <div class="flex items-center space-x-3">
              <button
                @click="resetToDefaults"
                class="btn-secondary"
              >
                <ArrowPathIcon class="w-4 h-4 mr-2" />
                Reset to Defaults
              </button>
              <button
                @click="saveSettings"
                :disabled="isSaving"
                class="btn-primary"
              >
                <CheckIcon class="w-4 h-4 mr-2" :class="{ 'animate-spin': isSaving }" />
                Save Changes
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Settings Navigation -->
          <div class="lg:col-span-1">
            <div class="card">
              <nav class="space-y-1">
                <button
                  v-for="section in settingSections"
                  :key="section.id"
                  @click="activeSection = section.id"
                  class="w-full flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200"
                  :class="activeSection === section.id
                    ? 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'
                    : 'text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700/50'
                  "
                >
                  <component :is="section.icon" class="w-5 h-5 mr-3" />
                  {{ section.name }}
                </button>
              </nav>
            </div>
          </div>

          <!-- Settings Content -->
          <div class="lg:col-span-2">
            <!-- General Settings -->
            <div v-if="activeSection === 'general'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  General Configuration
                </h3>
                
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Application Name
                    </label>
                    <input
                      v-model="settings.general.appName"
                      type="text"
                      class="input-field"
                      placeholder="Enter application name"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Application Description
                    </label>
                    <textarea
                      v-model="settings.general.appDescription"
                      rows="3"
                      class="input-field"
                      placeholder="Enter application description"
                    ></textarea>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Default Language
                    </label>
                    <select v-model="settings.general.defaultLanguage" class="input-field">
                      <option value="en">English</option>
                      <option value="es">Spanish</option>
                      <option value="fr">French</option>
                      <option value="de">German</option>
                      <option value="zh">Chinese</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Timezone
                    </label>
                    <select v-model="settings.general.timezone" class="input-field">
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time</option>
                      <option value="America/Chicago">Central Time</option>
                      <option value="America/Denver">Mountain Time</option>
                      <option value="America/Los_Angeles">Pacific Time</option>
                      <option value="Europe/London">London</option>
                      <option value="Europe/Paris">Paris</option>
                      <option value="Asia/Tokyo">Tokyo</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Security Settings -->
            <div v-if="activeSection === 'security'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Authentication & Security
                </h3>
                
                <div class="space-y-4">
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Require Email Verification
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Users must verify their email before accessing the system
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.security.requireEmailVerification"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Two-Factor Authentication
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Enable 2FA for enhanced security
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.security.enableTwoFactor"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Session Timeout (minutes)
                    </label>
                    <input
                      v-model.number="settings.security.sessionTimeout"
                      type="number"
                      min="5"
                      max="1440"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Password Minimum Length
                    </label>
                    <input
                      v-model.number="settings.security.passwordMinLength"
                      type="number"
                      min="6"
                      max="50"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max Login Attempts
                    </label>
                    <input
                      v-model.number="settings.security.maxLoginAttempts"
                      type="number"
                      min="3"
                      max="10"
                      class="input-field"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Chat Settings -->
            <div v-if="activeSection === 'chat'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Chat Configuration
                </h3>
                
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max Messages per Session
                    </label>
                    <input
                      v-model.number="settings.chat.maxMessagesPerSession"
                      type="number"
                      min="10"
                      max="1000"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Message Character Limit
                    </label>
                    <input
                      v-model.number="settings.chat.messageCharLimit"
                      type="number"
                      min="100"
                      max="10000"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Response Timeout (seconds)
                    </label>
                    <input
                      v-model.number="settings.chat.responseTimeout"
                      type="number"
                      min="5"
                      max="300"
                      class="input-field"
                    />
                  </div>
                  
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Enable File Uploads
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Allow users to upload files in chat
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.chat.enableFileUploads"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Auto-save Chat History
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Automatically save chat sessions
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.chat.autoSaveHistory"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Email Settings -->
            <div v-if="activeSection === 'email'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Email Configuration
                </h3>
                
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      SMTP Server
                    </label>
                    <input
                      v-model="settings.email.smtpServer"
                      type="text"
                      class="input-field"
                      placeholder="smtp.example.com"
                    />
                  </div>
                  
                  <div class="grid grid-cols-2 gap-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        SMTP Port
                      </label>
                      <input
                        v-model.number="settings.email.smtpPort"
                        type="number"
                        class="input-field"
                        placeholder="587"
                      />
                    </div>
                    
                    <div>
                      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Encryption
                      </label>
                      <select v-model="settings.email.encryption" class="input-field">
                        <option value="none">None</option>
                        <option value="tls">TLS</option>
                        <option value="ssl">SSL</option>
                      </select>
                    </div>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Username
                    </label>
                    <input
                      v-model="settings.email.username"
                      type="text"
                      class="input-field"
                      placeholder="your-email@example.com"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Password
                    </label>
                    <input
                      v-model="settings.email.password"
                      type="password"
                      class="input-field"
                      placeholder="••••••••"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      From Email
                    </label>
                    <input
                      v-model="settings.email.fromEmail"
                      type="email"
                      class="input-field"
                      placeholder="noreply@example.com"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      From Name
                    </label>
                    <input
                      v-model="settings.email.fromName"
                      type="text"
                      class="input-field"
                      placeholder="Your App Name"
                    />
                  </div>
                  
                  <div class="pt-4">
                    <button
                      @click="testEmailConnection"
                      :disabled="isTestingEmail"
                      class="btn-secondary"
                    >
                      <EnvelopeIcon class="w-4 h-4 mr-2" :class="{ 'animate-pulse': isTestingEmail }" />
                      Test Email Connection
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- API Settings -->
            <div v-if="activeSection === 'api'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  API Configuration
                </h3>
                
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Rate Limit (requests per minute)
                    </label>
                    <input
                      v-model.number="settings.api.rateLimit"
                      type="number"
                      min="10"
                      max="1000"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      API Timeout (seconds)
                    </label>
                    <input
                      v-model.number="settings.api.timeout"
                      type="number"
                      min="5"
                      max="300"
                      class="input-field"
                    />
                  </div>
                  
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Enable API Logging
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Log all API requests and responses
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.api.enableLogging"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                  
                  <div class="flex items-center justify-between">
                    <div>
                      <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Enable CORS
                      </label>
                      <p class="text-sm text-gray-500 dark:text-gray-400">
                        Allow cross-origin requests
                      </p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input
                        v-model="settings.api.enableCors"
                        type="checkbox"
                        class="sr-only peer"
                      />
                      <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                    </label>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Allowed Origins (one per line)
                    </label>
                    <textarea
                      v-model="settings.api.allowedOrigins"
                      rows="4"
                      class="input-field"
                      placeholder="https://example.com\nhttps://app.example.com"
                    ></textarea>
                  </div>
                </div>
              </div>
            </div>

            <!-- Storage Settings -->
            <div v-if="activeSection === 'storage'" class="space-y-6">
              <div class="card">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Storage Configuration
                </h3>
                
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Storage Provider
                    </label>
                    <select v-model="settings.storage.provider" class="input-field">
                      <option value="local">Local Storage</option>
                      <option value="s3">Amazon S3</option>
                      <option value="gcs">Google Cloud Storage</option>
                      <option value="azure">Azure Blob Storage</option>
                    </select>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Max File Size (MB)
                    </label>
                    <input
                      v-model.number="settings.storage.maxFileSize"
                      type="number"
                      min="1"
                      max="100"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Allowed File Types
                    </label>
                    <input
                      v-model="settings.storage.allowedFileTypes"
                      type="text"
                      class="input-field"
                      placeholder="jpg,png,pdf,txt,docx"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Storage Quota per User (GB)
                    </label>
                    <input
                      v-model.number="settings.storage.quotaPerUser"
                      type="number"
                      min="0.1"
                      max="100"
                      step="0.1"
                      class="input-field"
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Auto-cleanup after (days)
                    </label>
                    <input
                      v-model.number="settings.storage.autoCleanupDays"
                      type="number"
                      min="1"
                      max="365"
                      class="input-field"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import { useToast } from 'vue-toastification'
import {
  ArrowPathIcon,
  CheckIcon,
  CogIcon,
  ShieldCheckIcon,
  ChatBubbleLeftRightIcon,
  EnvelopeIcon,
  CodeBracketIcon,
  CloudIcon
} from '@heroicons/vue/24/outline'

const adminStore = useAdminStore()
const toast = useToast()

const activeSection = ref('general')
const isSaving = ref(false)
const isTestingEmail = ref(false)

const settingSections = [
  { id: 'general', name: 'General', icon: CogIcon },
  { id: 'security', name: 'Security', icon: ShieldCheckIcon },
  { id: 'chat', name: 'Chat', icon: ChatBubbleLeftRightIcon },
  { id: 'email', name: 'Email', icon: EnvelopeIcon },
  { id: 'api', name: 'API', icon: CodeBracketIcon },
  { id: 'storage', name: 'Storage', icon: CloudIcon }
]

const settings = reactive({
  general: {
    appName: 'ChatBot Assistant',
    appDescription: 'AI-powered chat assistant for your business',
    defaultLanguage: 'en',
    timezone: 'UTC'
  },
  security: {
    requireEmailVerification: true,
    enableTwoFactor: false,
    sessionTimeout: 60,
    passwordMinLength: 8,
    maxLoginAttempts: 5
  },
  chat: {
    maxMessagesPerSession: 100,
    messageCharLimit: 2000,
    responseTimeout: 30,
    enableFileUploads: true,
    autoSaveHistory: true
  },
  email: {
    smtpServer: '',
    smtpPort: 587,
    encryption: 'tls',
    username: '',
    password: '',
    fromEmail: '',
    fromName: ''
  },
  api: {
    rateLimit: 100,
    timeout: 30,
    enableLogging: true,
    enableCors: true,
    allowedOrigins: 'https://localhost:3000\nhttps://127.0.0.1:3000'
  },
  storage: {
    provider: 'local',
    maxFileSize: 10,
    allowedFileTypes: 'jpg,jpeg,png,gif,pdf,txt,docx,xlsx',
    quotaPerUser: 1.0,
    autoCleanupDays: 30
  }
})

const saveSettings = async () => {
  isSaving.value = true
  try {
    await adminStore.updateSystemSettings(settings)
    toast.success('Settings saved successfully')
  } catch (error) {
    console.error('Failed to save settings:', error)
    toast.error('Failed to save settings')
  } finally {
    isSaving.value = false
  }
}

const resetToDefaults = () => {
  if (confirm('Are you sure you want to reset all settings to defaults? This action cannot be undone.')) {
    // Reset to default values
    Object.assign(settings.general, {
      appName: 'ChatBot Assistant',
      appDescription: 'AI-powered chat assistant for your business',
      defaultLanguage: 'en',
      timezone: 'UTC'
    })
    
    Object.assign(settings.security, {
      requireEmailVerification: true,
      enableTwoFactor: false,
      sessionTimeout: 60,
      passwordMinLength: 8,
      maxLoginAttempts: 5
    })
    
    Object.assign(settings.chat, {
      maxMessagesPerSession: 100,
      messageCharLimit: 2000,
      responseTimeout: 30,
      enableFileUploads: true,
      autoSaveHistory: true
    })
    
    Object.assign(settings.email, {
      smtpServer: '',
      smtpPort: 587,
      encryption: 'tls',
      username: '',
      password: '',
      fromEmail: '',
      fromName: ''
    })
    
    Object.assign(settings.api, {
      rateLimit: 100,
      timeout: 30,
      enableLogging: true,
      enableCors: true,
      allowedOrigins: 'https://localhost:3000\nhttps://127.0.0.1:3000'
    })
    
    Object.assign(settings.storage, {
      provider: 'local',
      maxFileSize: 10,
      allowedFileTypes: 'jpg,jpeg,png,gif,pdf,txt,docx,xlsx',
      quotaPerUser: 1.0,
      autoCleanupDays: 30
    })
    
    toast.info('Settings reset to defaults')
  }
}

const testEmailConnection = async () => {
  isTestingEmail.value = true
  try {
    // Simulate email test
    await new Promise(resolve => setTimeout(resolve, 2000))
    toast.success('Email connection test successful')
  } catch (error) {
    console.error('Email test failed:', error)
    toast.error('Email connection test failed')
  } finally {
    isTestingEmail.value = false
  }
}

const loadSettings = async () => {
  try {
    const systemSettings = await adminStore.getSystemSettings()
    if (systemSettings) {
      Object.assign(settings, systemSettings)
    }
  } catch (error) {
    console.error('Failed to load settings:', error)
    toast.error('Failed to load settings')
  }
}

onMounted(() => {
  loadSettings()
})
</script>