import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // State
  const theme = ref('light')
  
  // Getters
  const isDark = computed(() => theme.value === 'dark')
  const isLight = computed(() => theme.value === 'light')
  
  // Actions
  const setTheme = (newTheme) => {
    theme.value = newTheme
    localStorage.setItem('theme', newTheme)
    updateDocumentClass()
  }
  
  const toggleTheme = () => {
    setTheme(isDark.value ? 'light' : 'dark')
  }
  
  const initializeTheme = () => {
    // Get theme from localStorage or system preference
    const savedTheme = localStorage.getItem('theme')
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    
    theme.value = savedTheme || systemTheme
    updateDocumentClass()
    
    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      if (!localStorage.getItem('theme')) {
        theme.value = e.matches ? 'dark' : 'light'
        updateDocumentClass()
      }
    })
  }
  
  const updateDocumentClass = () => {
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }
  
  return {
    theme,
    isDark,
    isLight,
    setTheme,
    toggleTheme,
    initializeTheme
  }
})