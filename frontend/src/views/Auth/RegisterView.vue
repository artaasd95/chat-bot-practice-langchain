<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mb-4">
          <svg class="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z"/>
            <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z"/>
          </svg>
        </div>
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
          Create your account
        </h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Join us and start chatting with AI
        </p>
      </div>

      <!-- Register Form -->
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
        <form @submit.prevent="handleRegister" class="space-y-6">
          <!-- Full Name Field -->
          <div>
            <label for="fullName" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Full Name
            </label>
            <div class="relative">
              <input
                id="fullName"
                v-model="form.fullName"
                type="text"
                required
                class="input-field pl-10"
                :class="{ 'border-red-500 dark:border-red-400': errors.fullName }"
                placeholder="Enter your full name"
              />
              <UserIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            <p v-if="errors.fullName" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.fullName }}
            </p>
          </div>

          <!-- Email Field -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email address
            </label>
            <div class="relative">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="input-field pl-10"
                :class="{ 'border-red-500 dark:border-red-400': errors.email }"
                placeholder="Enter your email"
              />
              <EnvelopeIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            </div>
            <p v-if="errors.email" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.email }}
            </p>
          </div>

          <!-- Password Field -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Password
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="input-field pl-10 pr-10"
                :class="{ 'border-red-500 dark:border-red-400': errors.password }"
                placeholder="Create a password"
              />
              <LockClosedIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <EyeIcon v-if="!showPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <p v-if="errors.password" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.password }}
            </p>
            
            <!-- Password Strength Indicator -->
            <div v-if="form.password" class="mt-2">
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

          <!-- Confirm Password Field -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Confirm Password
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                required
                class="input-field pl-10 pr-10"
                :class="{ 'border-red-500 dark:border-red-400': errors.confirmPassword }"
                placeholder="Confirm your password"
              />
              <LockClosedIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <EyeIcon v-if="!showConfirmPassword" class="w-5 h-5" />
                <EyeSlashIcon v-else class="w-5 h-5" />
              </button>
            </div>
            <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.confirmPassword }}
            </p>
          </div>

          <!-- Terms and Conditions -->
          <div class="flex items-start">
            <input
              id="terms"
              v-model="form.acceptTerms"
              type="checkbox"
              required
              class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 rounded mt-1"
            />
            <label for="terms" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              I agree to the
              <a href="#" class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300">
                Terms of Service
              </a>
              and
              <a href="#" class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300">
                Privacy Policy
              </a>
            </label>
          </div>
          <p v-if="errors.acceptTerms" class="text-sm text-red-600 dark:text-red-400">
            {{ errors.acceptTerms }}
          </p>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="isLoading"
            class="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <div v-if="isLoading" class="loading-dots">
              <div></div>
              <div></div>
              <div></div>
            </div>
            <span v-else>Create account</span>
          </button>
        </form>

        <!-- Divider -->
        <div class="mt-6">
          <div class="relative">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t border-gray-300 dark:border-gray-600"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                Already have an account?
              </span>
            </div>
          </div>
        </div>

        <!-- Login Link -->
        <div class="mt-6 text-center">
          <router-link
            to="/login"
            class="text-primary-600 dark:text-primary-400 hover:text-primary-500 dark:hover:text-primary-300 font-medium"
          >
            Sign in to your account
          </router-link>
        </div>
      </div>

      <!-- Theme Toggle -->
      <div class="text-center">
        <button
          @click="themeStore.toggleTheme()"
          class="inline-flex items-center space-x-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
        >
          <SunIcon v-if="themeStore.isDark" class="w-4 h-4" />
          <MoonIcon v-else class="w-4 h-4" />
          <span>{{ themeStore.isDark ? 'Light' : 'Dark' }} mode</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import {
  UserIcon,
  EnvelopeIcon,
  LockClosedIcon,
  EyeIcon,
  EyeSlashIcon,
  SunIcon,
  MoonIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const themeStore = useThemeStore()

const isLoading = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const form = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: false
})

const errors = reactive({
  fullName: '',
  email: '',
  password: '',
  confirmPassword: '',
  acceptTerms: ''
})

const passwordStrength = computed(() => {
  const password = form.password
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

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => {
    errors[key] = ''
  })
  
  let isValid = true
  
  // Full name validation
  if (!form.fullName.trim()) {
    errors.fullName = 'Full name is required'
    isValid = false
  } else if (form.fullName.trim().length < 2) {
    errors.fullName = 'Full name must be at least 2 characters'
    isValid = false
  }
  
  // Email validation
  if (!form.email) {
    errors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    isValid = false
  }
  
  // Password validation
  if (!form.password) {
    errors.password = 'Password is required'
    isValid = false
  } else if (form.password.length < 8) {
    errors.password = 'Password must be at least 8 characters'
    isValid = false
  } else if (passwordStrength.value < 2) {
    errors.password = 'Password is too weak. Include uppercase, lowercase, numbers, and special characters'
    isValid = false
  }
  
  // Confirm password validation
  if (!form.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password'
    isValid = false
  } else if (form.password !== form.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match'
    isValid = false
  }
  
  // Terms validation
  if (!form.acceptTerms) {
    errors.acceptTerms = 'You must accept the terms and conditions'
    isValid = false
  }
  
  return isValid
}

const handleRegister = async () => {
  if (!validateForm()) return
  
  try {
    isLoading.value = true
    
    await authStore.register({
      full_name: form.fullName.trim(),
      email: form.email,
      password: form.password
    })
    
    // Redirect to dashboard
    router.push('/dashboard')
    
  } catch (error) {
    console.error('Registration error:', error)
    
    // Handle specific error cases
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach(err => {
          if (err.loc?.includes('email')) {
            errors.email = err.msg
          } else if (err.loc?.includes('password')) {
            errors.password = err.msg
          } else if (err.loc?.includes('full_name')) {
            errors.fullName = err.msg
          }
        })
      } else if (typeof detail === 'string') {
        if (detail.includes('email')) {
          errors.email = detail
        } else {
          errors.email = 'Registration failed. Please try again.'
        }
      }
    }
  } finally {
    isLoading.value = false
  }
}
</script>