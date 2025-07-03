<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center justify-between">
            <div>
              <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                User Management
              </h1>
              <p class="text-gray-600 dark:text-gray-400">
                Manage user accounts and permissions
              </p>
            </div>
            <div class="flex items-center space-x-3">
              <button
                @click="exportUsers"
                class="btn-secondary"
              >
                <ArrowDownTrayIcon class="w-4 h-4 mr-2" />
                Export
              </button>
              <button
                @click="showCreateModal = true"
                class="btn-primary"
              >
                <UserPlusIcon class="w-4 h-4 mr-2" />
                Add User
              </button>
            </div>
          </div>
        </div>

        <!-- Filters and Search -->
        <div class="card mb-8">
          <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <!-- Search -->
            <div class="md:col-span-2">
              <div class="relative">
                <input
                  v-model="searchQuery"
                  type="text"
                  placeholder="Search users by name or email..."
                  class="input-field pl-10"
                />
                <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              </div>
            </div>
            
            <!-- Role Filter -->
            <div>
              <select v-model="selectedRole" class="input-field">
                <option value="">All Roles</option>
                <option value="admin">Admin</option>
                <option value="user">User</option>
              </select>
            </div>
            
            <!-- Status Filter -->
            <div>
              <select v-model="selectedStatus" class="input-field">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Users Stats -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Total Users</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ totalUsers }}</p>
              </div>
              <div class="w-10 h-10 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <UsersIcon class="w-5 h-5 text-blue-600 dark:text-blue-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Active Users</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ activeUsers }}</p>
              </div>
              <div class="w-10 h-10 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                <CheckCircleIcon class="w-5 h-5 text-green-600 dark:text-green-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">Admins</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ adminUsers }}</p>
              </div>
              <div class="w-10 h-10 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <ShieldCheckIcon class="w-5 h-5 text-purple-600 dark:text-purple-400" />
              </div>
            </div>
          </div>
          
          <div class="card">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-sm font-medium text-gray-600 dark:text-gray-400">New This Month</p>
                <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ newUsersThisMonth }}</p>
              </div>
              <div class="w-10 h-10 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                <UserPlusIcon class="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
          </div>
        </div>

        <!-- Users Table -->
        <div class="card">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    <input
                      type="checkbox"
                      v-model="selectAll"
                      @change="toggleSelectAll"
                      class="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                    />
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    User
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Role
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Last Login
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Created
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <template v-if="isLoading">
                  <tr v-for="i in 5" :key="`skeleton-${i}`" class="animate-pulse">
                  <td class="px-6 py-4">
                    <div class="w-4 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                      <div class="space-y-2">
                        <div class="w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                        <div class="w-32 h-3 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-16 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-20 h-6 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="w-24 h-4 bg-gray-200 dark:bg-gray-700 rounded"></div>
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex justify-end space-x-2">
                      <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                      <div class="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded"></div>
                    </div>
                  </td>
                </tr>
                </template>
                
                <template v-else>
                  <tr v-for="user in filteredUsers" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                  <td class="px-6 py-4">
                    <input
                      type="checkbox"
                      v-model="selectedUsers"
                      :value="user.id"
                      class="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                    />
                  </td>
                  <td class="px-6 py-4">
                    <div class="flex items-center space-x-3">
                      <div class="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                        <span class="text-white text-sm font-medium">
                          {{ getUserInitials(user.full_name) }}
                        </span>
                      </div>
                      <div>
                        <div class="text-sm font-medium text-gray-900 dark:text-white">
                          {{ user.full_name }}
                        </div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">
                          {{ user.email }}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="user.role === 'admin' 
                            ? 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'">
                      {{ user.role }}
                    </span>
                  </td>
                  <td class="px-6 py-4">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="user.is_active 
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'">
                      {{ user.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(user.last_login) }}
                  </td>
                  <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">
                    {{ formatDate(user.created_at) }}
                  </td>
                  <td class="px-6 py-4 text-right">
                    <div class="flex justify-end items-center space-x-2">
                      <button
                        @click="editUser(user)"
                        class="p-2 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-200"
                        title="Edit user"
                      >
                        <PencilIcon class="w-4 h-4" />
                      </button>
                      <button
                        @click="toggleUserStatus(user)"
                        class="p-2 transition-colors duration-200"
                        :class="user.is_active 
                          ? 'text-gray-400 hover:text-red-600 dark:hover:text-red-400'
                          : 'text-gray-400 hover:text-green-600 dark:hover:text-green-400'"
                        :title="user.is_active ? 'Deactivate user' : 'Activate user'"
                      >
                        <XMarkIcon v-if="user.is_active" class="w-4 h-4" />
                        <CheckIcon v-else class="w-4 h-4" />
                      </button>
                      <button
                        @click="deleteUser(user)"
                        class="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-200"
                        title="Delete user"
                      >
                        <TrashIcon class="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                  </tr>
                </template>

                <tr v-if="!isLoading && filteredUsers.length === 0">
                  <td colspan="7" class="px-6 py-12 text-center">
                    <UsersIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p class="text-gray-600 dark:text-gray-400">No users found</p>
                  </td>
                </tr>
              </tbody>
              </table>
            </div>
            
            <!-- Pagination -->
            <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-700 dark:text-gray-300">
                  Showing {{ (currentPage - 1) * pageSize + 1 }} to {{ Math.min(currentPage * pageSize, totalUsers) }} of {{ totalUsers }} results
                </div>
                <div class="flex items-center space-x-2">
                  <button
                    @click="currentPage--"
                    :disabled="currentPage === 1"
                    class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Previous
                  </button>
                  <span class="px-3 py-1 text-sm bg-primary-600 text-white rounded-md">
                    {{ currentPage }}
                  </span>
                  <button
                    @click="currentPage++"
                    :disabled="currentPage === totalPages"
                    class="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    Next
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Create/Edit User Modal -->
          <div v-if="showCreateModal || showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md mx-4">
              <div class="flex items-center justify-between mb-6">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                  {{ showCreateModal ? 'Create New User' : 'Edit User' }}
                </h3>
                <button
                  @click="closeModal"
                  class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <XMarkIcon class="w-6 h-6" />
                </button>
              </div>
              
              <form @submit.prevent="saveUser" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Full Name
                  </label>
                  <input
                    v-model="userForm.fullName"
                    type="text"
                    required
                    class="input-field"
                    :class="{ 'border-red-500 dark:border-red-400': userErrors.fullName }"
                  />
                  <p v-if="userErrors.fullName" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ userErrors.fullName }}
                  </p>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email Address
                  </label>
                  <input
                    v-model="userForm.email"
                    type="email"
                    required
                    class="input-field"
                    :class="{ 'border-red-500 dark:border-red-400': userErrors.email }"
                  />
                  <p v-if="userErrors.email" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ userErrors.email }}
                  </p>
                </div>
                
                <div v-if="showCreateModal">
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Password
                  </label>
                  <input
                    v-model="userForm.password"
                    type="password"
                    required
                    class="input-field"
                    :class="{ 'border-red-500 dark:border-red-400': userErrors.password }"
                  />
                  <p v-if="userErrors.password" class="mt-1 text-sm text-red-600 dark:text-red-400">
                    {{ userErrors.password }}
                  </p>
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Role
                  </label>
                  <select
                    v-model="userForm.role"
                    class="input-field"
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>
                
                <div class="flex items-center">
                  <input
                    v-model="userForm.isActive"
                    type="checkbox"
                    id="isActive"
                    class="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                  />
                  <label for="isActive" class="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Active user
                  </label>
                </div>
                
                <div class="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    @click="closeModal"
                    class="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    :disabled="isSaving"
                    class="btn-primary"
                  >
                    <div v-if="isSaving" class="loading-dots mr-2">
                      <div></div>
                      <div></div>
                      <div></div>
                    </div>
                    {{ showCreateModal ? 'Create New User' : 'Save Changes' }}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useAdminStore } from '@/stores/admin'
import {
  ArrowDownTrayIcon,
  UserPlusIcon,
  MagnifyingGlassIcon,
  UsersIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  PencilIcon,
  XMarkIcon,
  CheckIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const adminStore = useAdminStore()

const isLoading = ref(false)
const isSaving = ref(false)
const showCreateModal = ref(false)
const showEditModal = ref(false)
const selectAll = ref(false)
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = ref(10)

const searchQuery = ref('')
const selectedRole = ref('')
const selectedStatus = ref('')

const userForm = reactive({
  id: null,
  fullName: '',
  email: '',
  password: '',
  role: 'user',
  isActive: true
})

const userErrors = reactive({
  fullName: '',
  email: '',
  password: ''
})

const filteredUsers = computed(() => {
  let users = adminStore.users || []
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    users = users.filter(user => 
      user.full_name.toLowerCase().includes(query) ||
      user.email.toLowerCase().includes(query)
    )
  }
  
  if (selectedRole.value) {
    users = users.filter(user => user.role === selectedRole.value)
  }
  
  if (selectedStatus.value) {
    const isActive = selectedStatus.value === 'active'
    users = users.filter(user => user.is_active === isActive)
  }
  
  return users
})

const totalUsers = computed(() => filteredUsers.value.length)
const activeUsers = computed(() => filteredUsers.value.filter(user => user.is_active).length)
const adminUsers = computed(() => filteredUsers.value.filter(user => user.role === 'admin').length)
const newUsersThisMonth = computed(() => {
  const thisMonth = new Date()
  thisMonth.setDate(1)
  return filteredUsers.value.filter(user => new Date(user.created_at) >= thisMonth).length
})

const totalPages = computed(() => Math.ceil(totalUsers.value / pageSize.value))

const getUserInitials = (fullName) => {
  if (!fullName) return 'U'
  return fullName
    .split(' ')
    .map(name => name.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const formatDate = (dateString) => {
  if (!dateString) return 'Never'
  return new Date(dateString).toLocaleDateString()
}

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedUsers.value = filteredUsers.value.map(user => user.id)
  } else {
    selectedUsers.value = []
  }
}

const editUser = (user) => {
  userForm.id = user.id
  userForm.fullName = user.full_name
  userForm.email = user.email
  userForm.role = user.role
  userForm.isActive = user.is_active
  showEditModal.value = true
}

const toggleUserStatus = async (user) => {
  try {
    await adminStore.toggleUserStatus(user.id)
  } catch (error) {
    console.error('Failed to toggle user status:', error)
  }
}

const deleteUser = async (user) => {
  if (confirm(`Are you sure you want to delete ${user.full_name}?`)) {
    try {
      await adminStore.deleteUser(user.id)
    } catch (error) {
      console.error('Failed to delete user:', error)
    }
  }
}

const closeModal = () => {
  showCreateModal.value = false
  showEditModal.value = false
  Object.keys(userForm).forEach(key => {
    if (key === 'role') userForm[key] = 'user'
    else if (key === 'isActive') userForm[key] = true
    else userForm[key] = key === 'id' ? null : ''
  })
  Object.keys(userErrors).forEach(key => {
    userErrors[key] = ''
  })
}

const validateUser = () => {
  Object.keys(userErrors).forEach(key => {
    userErrors[key] = ''
  })
  
  let isValid = true
  
  if (!userForm.fullName.trim()) {
    userErrors.fullName = 'Full name is required'
    isValid = false
  }
  
  if (!userForm.email) {
    userErrors.email = 'Email is required'
    isValid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userForm.email)) {
    userErrors.email = 'Please enter a valid email address'
    isValid = false
  }
  
  if (showCreateModal.value && !userForm.password) {
    userErrors.password = 'Password is required'
    isValid = false
  } else if (showCreateModal.value && userForm.password.length < 8) {
    userErrors.password = 'Password must be at least 8 characters'
    isValid = false
  }
  
  return isValid
}

const saveUser = async () => {
  if (!validateUser()) return
  
  try {
    isSaving.value = true
    
    const userData = {
      full_name: userForm.fullName.trim(),
      email: userForm.email,
      role: userForm.role,
      is_active: userForm.isActive
    }
    
    if (showCreateModal.value) {
      userData.password = userForm.password
      await adminStore.createUser(userData)
    } else {
      await adminStore.updateUser(userForm.id, userData)
    }
    
    closeModal()
  } catch (error) {
    console.error('Save user error:', error)
    
    if (error.response?.status === 422) {
      const detail = error.response.data?.detail
      if (Array.isArray(detail)) {
        detail.forEach(err => {
          if (err.loc?.includes('email')) {
            userErrors.email = err.msg
          } else if (err.loc?.includes('full_name')) {
            userErrors.fullName = err.msg
          } else if (err.loc?.includes('password')) {
            userErrors.password = err.msg
          }
        })
      }
    }
  } finally {
    isSaving.value = false
  }
}

const exportUsers = async () => {
  try {
    await adminStore.exportUsers()
  } catch (error) {
    console.error('Failed to export users:', error)
  }
}

watch(selectedUsers, (newVal) => {
  selectAll.value = newVal.length === filteredUsers.value.length && newVal.length > 0
})

onMounted(() => {
  adminStore.fetchUsers()
})
</script>