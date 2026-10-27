import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import apiClient from '@/api/client'
import type { User } from '@/types'

function readStoredUser(): User | null {
  try {
    const raw = localStorage.getItem('aicte_user')
    return raw ? JSON.parse(raw) as User : null
  } catch {
    return null
  }
}

function isExplicitDemoSession() {
  try { return sessionStorage.getItem('casework_demo_mode') === '1' } catch { return false }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('aicte_token'))
  const user = ref<User | null>(readStoredUser())
  const loading = ref(false)
  const error = ref<string | null>(null)

  // A development identity is accepted only after the user explicitly enters the
  // offline demo. It is never treated as a valid API credential.
  const isAuthenticated = computed(() => Boolean(
    token.value && user.value && (token.value !== 'dev_bypass_token' || isExplicitDemoSession())
  ))
  const isSystemAdmin = computed(() => ['SYSTEM_ADMIN', 'ADMIN', 'admin'].includes((user.value?.role || '').trim()))
  const isIndustry = computed(() => ['INDUSTRY', 'OFFICER', 'officer', 'senior_authority'].includes((user.value?.role || '').trim()))
  const isUser = computed(() => ['USER', 'user', 'citizen'].includes((user.value?.role || '').trim()))
  const isAdmin = computed(() => isSystemAdmin.value)
  const isOfficer = computed(() => isIndustry.value)
  const isSeniorAuthority = computed(() => user.value?.role === 'senior_authority')
  const userBureauCode = computed(() => user.value?.bureau_code || null)
  const roleDisplay = computed(() => {
    if (isSystemAdmin.value) return 'System Administrator'
    if (isIndustry.value) return 'Industry / Department'
    return 'Citizen Complainant'
  })


  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const response = await apiClient.post('/auth/login', { email, password })
      if (!response.data?.token || !response.data?.user) {
        throw new Error('The server did not return a valid session.')
      }
      try { sessionStorage.removeItem('casework_demo_mode') } catch { /* unavailable storage */ }
      token.value = response.data.token
      user.value = response.data.user
      localStorage.setItem('aicte_token', response.data.token)
      localStorage.setItem('aicte_user', JSON.stringify(response.data.user))
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Authentication failed. Please verify your credentials and API connection.'
      return false
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!token.value) return
    if (token.value === 'dev_bypass_token' && isExplicitDemoSession()) return

    try {
      const response = await apiClient.get('/auth/me')
      if (response.data?.user) {
        user.value = response.data.user
        localStorage.setItem('aicte_user', JSON.stringify(response.data.user))
      } else {
        throw new Error('Session could not be verified.')
      }
    } catch {
      token.value = null
      user.value = null
      localStorage.removeItem('aicte_token')
      localStorage.removeItem('aicte_user')
    }
  }

  async function logout() {
    try {
      if (token.value && token.value !== 'dev_bypass_token') {
        await apiClient.post('/auth/logout')
      }
    } catch {
      // Clear the local session even when the API is unavailable.
    } finally {
      token.value = null
      user.value = null
      error.value = null
      localStorage.removeItem('aicte_token')
      localStorage.removeItem('aicte_user')
      try { sessionStorage.removeItem('casework_demo_mode') } catch { /* unavailable storage */ }
    }
  }

  return {
    token, user, loading, error, isAuthenticated, isAdmin, isOfficer,
    isSeniorAuthority, isSystemAdmin, isIndustry, isUser, roleDisplay,
    userBureauCode, login, logout, fetchMe,
  }

})
