import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Layouts
import MainLayout from '@/components/Layout/MainLayout.vue'

// Auth pages
import LoginView from '@/views/Auth/LoginView.vue'
import RegisterView from '@/views/Auth/RegisterView.vue'
import ForgotPasswordView from '@/views/Auth/ForgotPasswordView.vue'

// Dashboard pages
import DashboardView from '@/views/Dashboard/DashboardView.vue'
import ChatView from '@/views/Chat/ChatView.vue'
import ProfileView from '@/views/Profile/ProfileView.vue'

// Admin pages
import AdminDashboard from '@/views/Admin/AdminDashboard.vue'
import AdminUsers from '@/views/Admin/AdminUsers.vue'
import AdminChats from '@/views/Admin/AdminChats.vue'
import AdminSettings from '@/views/Admin/AdminSettings.vue'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  // Auth routes (no layout wrapper)
  {
    path: '/auth/login',
    name: 'Login',
    component: LoginView,
    meta: { requiresGuest: true, title: 'Sign In' }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: RegisterView,
    meta: { requiresGuest: true, title: 'Sign Up' }
  },
  {
    path: '/auth/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPasswordView,
    meta: { requiresGuest: true, title: 'Forgot Password' }
  },
  // Dashboard routes (with layout)
  {
    path: '/dashboard',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Dashboard',
        component: DashboardView,
        meta: { title: 'Dashboard' }
      }
    ]
  },
  {
    path: '/chat',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Chat',
        component: ChatView,
        meta: { title: 'Chat' }
      }
    ]
  },
  {
    path: '/profile',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Profile',
        component: ProfileView,
        meta: { title: 'Profile' }
      }
    ]
  },
  // Admin routes (with layout)
  {
    path: '/admin',
    component: MainLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard,
        meta: { title: 'Admin Dashboard' }
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: AdminUsers,
        meta: { title: 'User Management' }
      },
      {
        path: 'chats',
        name: 'AdminChats',
        component: AdminChats,
        meta: { title: 'Chat Management' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: AdminSettings,
        meta: { title: 'Admin Settings' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page Not Found' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - Chat Bot` : 'Chat Bot'
  
  // Check if route requires authentication
  if (to.meta.requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/auth/login')
      return
    }
    
    // Check if route requires admin privileges
    if (to.meta.requiresAdmin && !authStore.user?.is_admin) {
      next('/dashboard')
      return
    }
  }
  
  // Check if route requires guest (not authenticated)
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/dashboard')
    return
  }
  
  next()
})

export default router