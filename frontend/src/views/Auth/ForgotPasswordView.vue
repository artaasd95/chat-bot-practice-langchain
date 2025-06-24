<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Header -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center mb-6">
          <KeyIcon class="h-8 w-8 text-white" />
        </div>
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white">
          {{ step === 'request' ? 'Reset Password' : 'Check Your Email' }}
        </h2>
        <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {{ step === 'request' 
            ? 'Enter your email address and we\'ll send you a link to reset your password.' 
            : 'We\'ve sent a password reset link to your email address.' 
          }}
        </p>
      </div>

      <!-- Request Form -->
      <div v-if="step === 'request'" class="card">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Email Address
            </label>
            <div class="relative">
              <input
                id="email"
                v-model="form.email"
                type="email"
                required
                class="input-field pl-10"
                :class="{
                  'border-red-300 dark:border-red-600 focus:border-red-500 focus:ring-red-500': errors.email,
                  'border-green-300 dark:border-green-600 focus:border-green-500 focus:ring-green-500': form.email && !errors.email
                }"
                placeholder="Enter your email address"
              />
              <EnvelopeIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            </div>
            <p v-if="errors.email" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.email }}
            </p>
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading || !form.email"
              class="btn-primary w-full"
            >
              <ArrowPathIcon v-if="isLoading" class="animate-spin -ml-1 mr-3 h-5 w-5" />
              {{ isLoading ? 'Sending...' : 'Send Reset Link' }}
            </button>
          </div>
        </form>
      </div>

      <!-- Success Message -->
      <div v-else class="card text-center">
        <div class="mx-auto h-16 w-16 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mb-6">
          <CheckCircleIcon class="h-8 w-8 text-green-600 dark:text-green-400" />
        </div>
        
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          Reset Link Sent!
        </h3>
        
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          We've sent a password reset link to <strong>{{ form.email }}</strong>. 
          Please check your email and follow the instructions to reset your password.
        </p>
        
        <div class="space-y-3">
          <button
            @click="resendEmail"
            :disabled="isResending || countdown > 0"
            class="btn-secondary w-full"
          >
            <ArrowPathIcon v-if="isResending" class="animate-spin -ml-1 mr-3 h-5 w-5" />
            {{ isResending ? 'Resending...' : countdown > 0 ? `Resend in ${countdown}s` : 'Resend Email' }}
          </button>
          
          <button
            @click="goBack"
            class="btn-outline w-full"
          >
            Try Different Email
          </button>
        </div>
      </div>

      <!-- Back to Login -->
      <div class="text-center">
        <router-link
          to="/auth/login"
          class="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors duration-200"
        >
          <ArrowLeftIcon class="h-4 w-4 mr-2" />
          Back to Login
        </router-link>
      </div>

      <!-- Help Section -->
      <div class="card bg-gray-50 dark:bg-gray-800/50">
        <div class="flex items-start space-x-3">
          <InformationCircleIcon class="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
          <div class="text-sm text-gray-600 dark:text-gray-400">
            <p class="font-medium text-gray-900 dark:text-white mb-1">Need help?</p>
            <ul class="space-y-1 text-xs">
              <li>• Check your spam/junk folder</li>
              <li>• Make sure you entered the correct email address</li>
              <li>• The reset link expires in 1 hour</li>
              <li>• Contact support if you continue having issues</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'
import {
  KeyIcon,
  EnvelopeIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  ArrowLeftIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const toast = useToast()

const step = ref('request') // 'request' or 'sent'
const isLoading = ref(false)
const isResending = ref(false)
const countdown = ref(0)
let countdownInterval = null

const form = reactive({
  email: ''
})

const errors = reactive({
  email: ''
})

const validateForm = () => {
  errors.email = ''
  
  if (!form.email) {
    errors.email = 'Email is required'
    return false
  }
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(form.email)) {
    errors.email = 'Please enter a valid email address'
    return false
  }
  
  return true
}

const handleSubmit = async () => {
  if (!validateForm()) return
  
  isLoading.value = true
  
  try {
    await authStore.forgotPassword(form.email)
    step.value = 'sent'
    startCountdown()
    toast.success('Password reset link sent successfully')
  } catch (error) {
    console.error('Forgot password error:', error)
    
    if (error.response?.status === 404) {
      errors.email = 'No account found with this email address'
    } else if (error.response?.status === 429) {
      errors.email = 'Too many requests. Please try again later'
    } else {
      toast.error('Failed to send reset link. Please try again.')
    }
  } finally {
    isLoading.value = false
  }
}

const resendEmail = async () => {
  isResending.value = true
  
  try {
    await authStore.forgotPassword(form.email)
    startCountdown()
    toast.success('Reset link sent again')
  } catch (error) {
    console.error('Resend email error:', error)
    toast.error('Failed to resend email. Please try again.')
  } finally {
    isResending.value = false
  }
}

const startCountdown = () => {
  countdown.value = 60
  countdownInterval = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  }, 1000)
}

const goBack = () => {
  step.value = 'request'
  form.email = ''
  errors.email = ''
  if (countdownInterval) {
    clearInterval(countdownInterval)
    countdownInterval = null
  }
  countdown.value = 0
}

onUnmounted(() => {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
})
</script>