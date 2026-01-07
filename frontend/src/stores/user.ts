import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authService } from '../services/auth'
import type { UserProfile } from '../services/auth'

export const useUserStore = defineStore('user', () => {
  // 用户状态
  const user = ref<UserProfile | null>(null)
  const isAuthenticated = ref(authService.isLoggedIn())

  // 登录
  const login = async (username: string, password: string) => {
    const response = await authService.login({
      username,
      password,
    })

    user.value = response.user
    isAuthenticated.value = true

    return response
  }

  // 注册
  const register = async (username: string, email: string, password: string) => {
    return await authService.register({
      username,
      email,
      password,
    })
  }

  // 获取用户资料
  const fetchProfile = async () => {
    if (!authService.isLoggedIn()) {
      throw new Error('用户未登录')
    }

    const response = await authService.getProfile()
    user.value = response.user

    return response
  }

  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    return await authService.changePassword({
      current_password: oldPassword,
      new_password: newPassword,
    })
  }

  // 登出
  const logout = () => {
    authService.logout()
    user.value = null
    isAuthenticated.value = false
  }

  // 检查登录状态
  const checkAuthStatus = () => {
    isAuthenticated.value = authService.isLoggedIn()
    if (isAuthenticated.value && !user.value) {
      // 如果已登录但没有用户信息，尝试获取
      fetchProfile().catch(() => {
        // 如果获取失败，执行登出
        logout()
      })
    }
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    fetchProfile,
    changePassword,
    logout,
    checkAuthStatus,
  }
})
