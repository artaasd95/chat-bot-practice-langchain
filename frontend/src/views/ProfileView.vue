<template>
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">Profile Settings</h1>
          <p class="text-gray-600 dark:text-gray-400">
            Manage your account information and preferences
          </p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- Profile Card -->
          <div class="lg:col-span-1">
            <div class="card text-center">
              <!-- Avatar -->
              <div class="mb-6">
                <div class="w-24 h-24 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span class="text-2xl font-bold text-white">
                    {{ userInitials }}
                  </span>
                </div>
                <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                  {{ authStore.user?.full_name }}
                </h2>
                <p class="text-gray-600 dark:text-gray-400">
                  {{ authStore.user?.email }}
                </p>
                <div class="mt-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="authStore.user?.is_active 
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'">
                    {{ authStore.user?.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
              </div>

              <!-- Quick Stats -->
              <div class="space-y-4">
                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Member since</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ formatDate(authStore.user?.created_at) }}
                  </span>
                </div>
                <div class="flex justify-between items-center py-2 border-b border-gray-200 dark:border-gray-700">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Last login</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    {{ formatDate(authStore.user?.last_login) }}
                  </span>
                </div>
                <div class="flex justify-between items-center py-2">
                  <span class="text-sm text-gray-600 dark:text-gray-400">Role</span>
                  <span class="text-sm font-medium text-gray-900 dark:text-white capitalize">
                    {{ authStore.user?.role }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Settings Forms -->
          <div class="lg:col-span-2 space-y-8">
            <!-- Personal Information -->
            <div class="card">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Personal Information</h3>
                <button
                  v-if="!editingProfile"
                  @click="startEditProfile"
                  class="btn-secondary"
                >
                  <PencilIcon class="w-4 h-4 mr-2" />
                  Edit
                </button>
              </div>

              <form v-if="editingProfile" @submit.prevent="saveProfile" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Full Name
                    </label>
                    <input
                      v-model="profileForm.fullName"
                      type="text"
                      required
                      class="input-field"
                      :class="{ 'border-red-500 dark:border-red-400': profileErrors.fullName }"
                    />
                    <p v-if="profileErrors.fullName" class="mt-1 text-sm text-red-600 dark:text-red-400">
                      {{ profileErrors.fullName }}
                    </p>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <input
                      v-model="profileForm.email"
                      type="email"
                      required
                      class="input-field"
                      :class="{ 'border-red-500 dark:border-red-400': profileErrors.email }"
                    />
                    <p v-if="profileErrors.email" class="mt-1 text-sm text-red-600 dark:text-red-400">
                      {{ profileErrors.email }}
                    </p>
                  </div>
                </div>

                <div class="flex justify-end space-x-3">
                  <button
                    type="button"
                    @click="cancelEditProfile"
                    class="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="isUpdatingProfile"
                    class="btn-primary"
                  >
                    <div v-if="isUpdatingProfile" class="loading-dots mr-2">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    Save Changes
                  </button>
                </div>
              </form>

              <div v-else class="space-y-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Full Name
                    </label>
                    <p class="text-gray-900 dark:text-white">{{ authStore.user?.full_name }}</p>
                  </div>
                  <div>
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Email Address
                    </label>
                    <p class="text-gray-900 dark:text-white">{{ authStore.user?.email }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Change Password -->
            <div class="card">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Change Password</h3>
                <button
                  v-if="!changingPassword"
                  @click="startChangePassword"
                  class="btn-secondary"
                >
                  <LockClosedIcon class="w-4 h-4 mr-2" />
                  Change
                </button>
              </div>

              <form v-if="changingPassword" @submit.prevent="savePassword" class="space-y-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Current Password
                  </label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.currentPassword"
                      :type="showCurrentPassword ? 'text' : 'password'"
                      required
                      class="input-field pr-10"
                      :class="{ 'border-red-500 dark:border-red-400': passwordErrors.currentPassword }"
                    />
                    <button
                      type="button"
                      @click="showCurrentPassword = !showCurrentPassword"
                      class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <EyeIcon v-if="!showCurrentPassword" class="w-5 h-5" />
                      <EyeSlashIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                  <p v-if="passwordErrors.currentPassword" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ passwordErrors.currentPassword }}
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    New Password
                  </label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.newPassword"
                      :type="showNewPassword ? 'text' : 'password'"
                      required
                      class="input-field pr-10"
                      :class="{ 'border-red-500 dark:border-red-400': passwordErrors.newPassword }"
                    />
                    <button
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                      class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <EyeIcon v-if="!showNewPassword" class="w-5 h-5" />
                      <EyeSlashIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                  <p v-if="passwordErrors.newPassword" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ passwordErrors.newPassword }}
                  </p>
                  
                  <!-- Password Strength Indicator -->
                  <div v-if="passwordForm.newPassword" class="mt-2">
                    <div class="flex space-x-1">
                      <div
                        v-for="i in 4"
                        :key="i"
                        class="h-1 flex-1 rounded-full"
                        :class="getPasswordStrengthColor(i)"
                      ></div>
                    </div>
                    <p class="text-xs mt-1" :class="getPasswordStrengthTextColor()">
                      {{ getPasswordStrengthText() }}
                    </p>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Confirm New Password
                  </label>
                  <div class="relative">
                    <input
                      v-model="passwordForm.confirmPassword"
                      :type="showConfirmPassword ? 'text' : 'password'"
                      required
                      class="input-field pr-10"
                      :class="{ 'border-red-500 dark:border-red-400': passwordErrors.confirmPassword }"
                    />
                    <button
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                    >
                      <EyeIcon v-if="!showConfirmPassword" class="w-5 h-5" />
                      <EyeSlashIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                  <p v-if="passwordErrors.confirmPassword" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ passwordErrors.confirmPassword }}
                  </p>
                </div>

                <div class="flex justify-end space-x-3">
                  <button
                    type="button"
                    @click="cancelChangePassword"
                    class="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="isUpdatingPassword"
                    class="btn-primary"
                  >
                    <div v-if="isUpdatingPassword" class="loading-dots mr-2">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    Update Password
                  </button>
                </div>
              </form>

              <div v-else class="text-gray-600 dark:text-gray-400">
                <p>Password was last changed {{ formatDate(authStore.user?.updated_at) }}</p>
              </div>
            </div>

            <!-- Preferences -->
            <div class="card">
              <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-6">Preferences</h3>
              
              <div class="space-y-6">
                <!-- Theme Preference -->
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">Theme</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Choose your preferred theme</p>
                  </div>
                  <div class="flex items-center space-x-2">
                    <button
                      @click="themeStore.setTheme('light')"
                      class="p-2 rounded-lg transition-colors duration-200"
                      :class="themeStore.theme === 'light' 
                        ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'"
                    >
                      <SunIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click="themeStore.setTheme('dark')"
                      class="p-2 rounded-lg transition-colors duration-200"
                      :class="themeStore.theme === 'dark' 
                        ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'"
                    >
                      <MoonIcon class="w-4 h-4" />
                    </button>
                    <button
                      @click="themeStore.setTheme('system')"
                      class="p-2 rounded-lg transition-colors duration-200"
                      :class="themeStore.theme === 'system' 
                        ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'"
                    >
                      <ComputerDesktopIcon class="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <!-- Notifications -->
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">Email Notifications</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Receive email updates about your account</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      v-model="preferences.emailNotifications"
                      type="checkbox"
                      class="sr-only peer"
                    />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                  </label>
                </div>

                <!-- Auto-save Chats -->
                <div class="flex items-center justify-between">
                  <div>
                    <h4 class="text-sm font-medium text-gray-900 dark:text-white">Auto-save Chats</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400">Automatically save your conversations</p>
                  </div>
                  <label class="relative inline-flex items-center cursor-pointer">
                    <input
                      v-model="preferences.autoSaveChats"
                      type="checkbox"
                      class="sr-only peer"
                    />
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
                  </label>
                </div>
              </div>
            </div>

            <!-- Danger Zone -->
            <div class="card border-red-200 dark:border-red-800">
              <h3 class="text-lg font-semibold text-red-600 dark:text-red-400 mb-6">Danger Zone</h3>
              
              <div class="space-y-4">
                <div class="flex items-center justify-between p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
                  <div>
                    <h4 class="text-sm font-medium text-red-900 dark:text-red-400">Delete Account</h4>
                    <p class="text-sm text-red-700 dark:text-red-500">Permanently delete your account and all data</p>
                  </div>
                  <button
                    @click="confirmDeleteAccount"
                    class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-medium rounded-lg transition-colors duration-200"
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Delete Account Modal -->
      <div v-if="showDeleteModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
          <div class="flex items-center mb-4">
            <ExclamationTriangleIcon class="w-6 h-6 text-red-600 mr-3" />
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Delete Account</h3>
          </div>
          <p class="text-gray-600 dark:text-gray-400 mb-6">
            This action cannot be undone. This will permanently delete your account and all associated data.
          </p>
          <div class="flex justify-end space-x-3">
            <button
              @click="showDeleteModal = false"
              class="px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
            >
              Cancel
            </button>
            <button
              @click="deleteAccount"
              class="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg"
            >
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'

import {
  PencilIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  SunIcon,
  MoonIcon,
  ComputerDesktopIcon,
  ExclamationTriangleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const editingProfile = ref(false)
const changingPassword = ref(false)
const isUpdatingProfile = ref(false)
const isUpdatingPassword = ref(false)
const showDeleteModal = ref(false)

const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const profileForm = reactive({
  fullName: '',
  email: ''
})

const passwordForm = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const preferences = reactive({
  emailNotifications: true,
  autoSaveChats: true
})

const profileErrors = reactive({
  fullName: '',
  email: ''
})

const passwordErrors = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const userInitials = computed(() => {
  const user = authStore.user
  if (!user?.full_name) return 'U'
  return user.full_name
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
})

const passwordStrength = computed(() => {
  const password = passwordForm.newPassword
  let score = 0
  
  if (password.length >= 8) score++
  if (/[a-z]/.test(password)) score++
  if (/[A-Z]/.test(password)) score++
  if (/[0-9]/.test(password)) score++
  if (/[^A-Za-z0-9]/.test(password)) score++
  
  return Math.min(score, 4)
})

const getPasswordStrengthColor = (index) => {
  if (passwordStrength.value >= index) {
    if (passwordStrength.value <= 1) return 'bg-red-500'
    if (passwordStrength.value <= 2) return 'bg-yellow-500'
    if (passwordStrength.value <= 3) return 'bg-blue-500'
    return 'bg-green-500'
  }
  return 'bg-gray-200 dark:bg-gray-600'
}

const getPasswordStrengthText = () => {
  if (passwordStrength.value <= 1) return 'Weak'
  if (passwordStrength.value <= 2) return 'Fair'
  if (passwordStrength.value <= 3) return 'Good'
  return 'Strong'
}

const getPasswordStrengthTextColor = () => {
  if (passwordStrength.value <= 1) return 'text-red-600 dark:text-red-400'
  if (passwordStrength.value <= 2) return 'text-yellow-600 dark:text-yellow-400'
  if (passwordStrength.value <= 3) return 'text-blue-600 dark:text-blue-400'
  return 'text-green-600 dark:text-green-400'
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const startEditProfile = () => {
  editingProfile.value = true
  profileForm.fullName = authStore.user?.full_name || ''
  profileForm.email = authStore.user?.email || ''
}

const cancelEditProfile = () => {
  editingProfile.value = false
  Object.keys(profileErrors).forEach(key => {
    profileErrors[key] = ''
  })
}

const validateProfile = () => {
  Object.keys(profileErrors).forEach(key => {
    profileErrors[key] = ''
  })
  
  let isValid = true
  
  if (!profileForm.fullName.trim()) {
    profileErrors.fullName = 'Full name is required'
    isValid = false
  }
  
  if (!profileForm.email) {
    profileErrors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(profileForm.email)) {
    profileErrors.email = 'Please enter a valid email address'
    isValid = false
  }
  
  return isValid
}

const saveProfile = async () => {
  if (!validateProfile()) return
  
  try {
    isUpdatingProfile.value = true
    
    await authStore.updateProfile({
      full_name: profileForm.fullName.trim(),
      email: profileForm.email
    })
    
    editingProfile.value = false
  } catch (error) {
    console.error('Update profile error:', error)
    
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach(err => {
          if (err.loc?.includes('email')) {
            profileErrors.email = err.msg
          } else if (err.loc?.includes('full_name')) {
            profileErrors.fullName = err.msg
          }
        })
      }
    }
  } finally {
    isUpdatingProfile.value = false
  }
}

const startChangePassword = () => {
  changingPassword.value = true
}

const cancelChangePassword = () => {
  changingPassword.value = false
  Object.keys(passwordForm).forEach(key => {
    passwordForm[key] = ''
  })
  Object.keys(passwordErrors).forEach(key => {
    passwordErrors[key] = ''
  })
}

const validatePassword = () => {
  Object.keys(passwordErrors).forEach(key => {
    passwordErrors[key] = ''
  })
  
  let isValid = true
  
  if (!passwordForm.currentPassword) {
    passwordErrors.currentPassword = 'Current password is required'
    isValid = false
  }
  
  if (!passwordForm.newPassword) {
    passwordErrors.newPassword = 'New password is required'
    isValid = false
  } else if (passwordForm.newPassword.length < 8) {
    passwordErrors.newPassword = 'Password must be at least 8 characters'
    isValid = false
  } else if (passwordStrength.value < 2) {
    passwordErrors.newPassword = 'Password is too weak'
    isValid = false
  }
  
  if (!passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Please confirm your password'
    isValid = false
  } else if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordErrors.confirmPassword = 'Passwords do not match'
    isValid = false
  }
  
  return isValid
}

const savePassword = async () => {
  if (!validatePassword()) return
  
  try {
    isUpdatingPassword.value = true
    
    await authStore.changePassword({
      current_password: passwordForm.currentPassword,
      new_password: passwordForm.newPassword
    })
    
    changingPassword.value = false
    Object.keys(passwordForm).forEach(key => {
      passwordForm[key] = ''
    })
  } catch (error) {
    console.error('Change password error:', error)
    
    if (error.response?.status === 400) {
      passwordErrors.currentPassword = 'Current password is incorrect'
    } else if (error.response?.status === 422) {
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach(err => {
          if (err.loc?.includes('current_password')) {
            passwordErrors.currentPassword = err.msg
          } else if (err.loc?.includes('new_password')) {
            passwordErrors.newPassword = err.msg
          }
        })
      }
    }
  } finally {
    isUpdatingPassword.value = false
  }
}

const confirmDeleteAccount = () => {
  showDeleteModal.value = true
}

const deleteAccount = async () => {
  try {
    // This would need to be implemented in the backend
    // await authStore.deleteAccount()
    showDeleteModal.value = false
    await authStore.logout()
    router.push('/login')
  } catch (error) {
    console.error('Delete account error:', error)
  }
}

onMounted(() => {
  // Load user preferences if available
  // This would typically come from the backend
})
</script>