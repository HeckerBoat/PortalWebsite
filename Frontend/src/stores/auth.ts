import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as apiLogin, getMe, type UserInfo } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem('token') || '')
  const user = ref<UserInfo | null>(null)

  const isAdmin = () => user.value?.role === 'admin'

  async function login(account: string, password: string) {
    const res = await apiLogin({ account, password })
    token.value = res.data.token
    user.value = res.data.user
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res
  }

  function loadUserFromStorage() {
    const raw = localStorage.getItem('user')
    if (raw) {
      try {
        user.value = JSON.parse(raw)
      } catch {
        user.value = null
      }
    }
  }

  async function fetchMe() {
    try {
      const res = await getMe()
      user.value = res.data
      localStorage.setItem('user', JSON.stringify(res.data))
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return { token, user, isAdmin, login, loadUserFromStorage, fetchMe, logout }
})
