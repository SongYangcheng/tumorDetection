import { ref, computed } from 'vue'
import type { FormErrors, PasswordStrength } from '../types'

/**
 * 表单验证组合式函数
 */
export function useFormValidation() {
  const errors = ref<FormErrors>({})

  /**
   * 验证用户名
   */
  const validateUsername = (username: string): string => {
    if (!username) {
      return '请输入用户名'
    }
    if (username.length < 3) {
      return '用户名至少需要3个字符'
    }
    if (username.length > 20) {
      return '用户名不能超过20个字符'
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      return '用户名只能包含字母、数字、下划线和连字符'
    }
    return ''
  }

  /**
   * 验证邮箱
   */
  const validateEmail = (email: string): string => {
    if (!email) {
      return '请输入邮箱地址'
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!emailRegex.test(email)) {
      return '请输入有效的邮箱地址'
    }
    return ''
  }

  /**
   * 验证密码
   */
  const validatePassword = (password: string, minLength = 6): string => {
    if (!password) {
      return '请输入密码'
    }
    if (password.length < minLength) {
      return `密码至少需要${minLength}个字符`
    }
    if (password.length > 50) {
      return '密码不能超过50个字符'
    }
    return ''
  }

  /**
   * 验证确认密码
   */
  const validateConfirmPassword = (password: string, confirmPassword: string): string => {
    if (!confirmPassword) {
      return '请再次输入密码'
    }
    if (password !== confirmPassword) {
      return '两次输入的密码不一致'
    }
    return ''
  }

  /**
   * 计算密码强度
   */
  const calculatePasswordStrength = (password: string): PasswordStrength => {
    if (!password) {
      return { score: 0, class: '', text: '' }
    }

    let score = 0
    
    // 长度评分
    if (password.length >= 6) score++
    if (password.length >= 8) score++
    if (password.length >= 12) score++
    
    // 复杂度评分
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[^a-zA-Z0-9]/.test(password)) score++

    if (score <= 2) {
      return { score, class: 'weak', text: '弱' }
    }
    if (score <= 4) {
      return { score, class: 'medium', text: '中等' }
    }
    return { score, class: 'strong', text: '强' }
  }

  /**
   * 设置字段错误
   */
  const setFieldError = (field: string, message: string) => {
    errors.value[field] = message
  }

  /**
   * 清除字段错误
   */
  const clearFieldError = (field: string) => {
    delete errors.value[field]
  }

  /**
   * 清除所有错误
   */
  const clearAllErrors = () => {
    errors.value = {}
  }

  /**
   * 检查是否有错误
   */
  const hasErrors = computed(() => {
    return Object.keys(errors.value).length > 0
  })

  return {
    errors,
    hasErrors,
    validateUsername,
    validateEmail,
    validatePassword,
    validateConfirmPassword,
    calculatePasswordStrength,
    setFieldError,
    clearFieldError,
    clearAllErrors
  }
}

/**
 * 防抖函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }
    
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}
