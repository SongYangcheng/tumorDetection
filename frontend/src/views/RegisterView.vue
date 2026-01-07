<template>
  <div class="register-container">
    <div class="register-card">
      <!-- Logo和标题 -->
      <div class="register-header">
        <div class="logo" aria-label="NeuroVision Logo">NeuroVision</div>
        <h1>创建账户</h1>
        <p class="subtitle">加入脑肿瘤智能检测系统</p>
      </div>

      <!-- 消息提示 -->
      <AlertMessage v-model="showErrorAlert" type="error" :message="errorMessage" :auto-dismiss="5000" />

      <AlertMessage v-model="showSuccessAlert" type="success" :message="successMessage" :dismissible="false" />

      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister" class="register-form" novalidate>
        <!-- 用户名 -->
        <div class="form-group">
          <label for="username" class="form-label">用户名</label>
          <input id="username" v-model.trim="form.username" type="text" placeholder="3-20个字符,支持字母、数字、下划线" required
            :disabled="isLoading" :aria-invalid="!!errors.username"
            :aria-describedby="errors.username ? 'username-error' : undefined" autocomplete="username"
            class="form-control" @blur="validateField('username')" @input="debouncedValidateUsername" />
          <Transition name="error-slide">
            <span v-if="errors.username" id="username-error" class="field-error" role="alert">
              {{ errors.username }}
            </span>
          </Transition>
        </div>

        <!-- 电子邮箱 -->
        <div class="form-group">
          <label for="email" class="form-label">电子邮箱</label>
          <input id="email" v-model.trim="form.email" type="email" placeholder="your.email@example.com" required
            :disabled="isLoading" :aria-invalid="!!errors.email"
            :aria-describedby="errors.email ? 'email-error' : undefined" autocomplete="email" class="form-control"
            @blur="validateField('email')" @input="debouncedValidateEmail" />
          <Transition name="error-slide">
            <span v-if="errors.email" id="email-error" class="field-error" role="alert">
              {{ errors.email }}
            </span>
          </Transition>
        </div>

        <!-- 密码 -->
        <PasswordField id="password" v-model="form.password" label="密码" placeholder="至少6个字符,建议包含大小写字母、数字和特殊字符" required
          :disabled="isLoading" :error="errors.password" :show-strength="true" autocomplete="new-password"
          @blur="validateField('password')" @input="debouncedValidatePassword" />

        <!-- 确认密码 -->
        <PasswordField id="confirmPassword" v-model="confirmPassword" label="确认密码" placeholder="再次输入密码" required
          :disabled="isLoading" :error="errors.confirmPassword" autocomplete="new-password"
          @blur="validateField('confirmPassword')" @input="debouncedValidateConfirmPassword" />

        <!-- 用户协议 -->
        <label class="checkbox-group">
          <input v-model="acceptTerms" type="checkbox" required :aria-invalid="showTermsError"
            aria-describedby="terms-error" />
          <span>
            我已阅读并同意
            <a href="#" class="inline-link" @click.prevent="showTermsModal" tabindex="0">
              用户协议
            </a>
            和
            <a href="#" class="inline-link" @click.prevent="showPrivacyModal" tabindex="0">
              隐私政策
            </a>
          </span>
        </label>
        <Transition name="error-slide">
          <span v-if="showTermsError" id="terms-error" class="field-error" role="alert">
            请先阅读并同意用户协议和隐私政策
          </span>
        </Transition>

        <!-- 注册按钮 -->
        <button type="submit" class="btn-primary" :disabled="isLoading || !isFormValid" :aria-busy="isLoading">
          <span v-if="isLoading" class="loading-spinner" aria-hidden="true"></span>
          {{ isLoading ? '注册中...' : '注册账户' }}
        </button>
      </form>

      <!-- 登录链接 -->
      <div class="register-footer">
        <span>已有账号?</span>
        <router-link to="/login" class="login-link">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useFormValidation, debounce } from '@/composables/useFormValidation'
import AlertMessage from '@/components/AlertMessage.vue'
import PasswordField from '@/components/PasswordField.vue'
import type { RegisterForm } from '@/types'

const router = useRouter()
const userStore = useUserStore()

// 表单验证
const {
  errors,
  hasErrors,
  validateUsername,
  validateEmail,
  validatePassword,
  validateConfirmPassword,
  setFieldError,
  clearFieldError,
  clearAllErrors
} = useFormValidation()

// 表单数据
const form = ref<RegisterForm>({
  username: '',
  email: '',
  password: ''
})

const confirmPassword = ref('')
const acceptTerms = ref(false)

// 状态
const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')
const showErrorAlert = ref(false)
const showSuccessAlert = ref(false)
const showTermsError = ref(false)

// 表单验证状态
const isFormValid = computed(() => {
  return (
    form.value.username.length >= 3 &&
    form.value.username.length <= 20 &&
    form.value.email.length > 0 &&
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.value.email) &&
    form.value.password.length >= 6 &&
    confirmPassword.value === form.value.password &&
    acceptTerms.value &&
    !hasErrors.value
  )
})

/**
 * 验证单个字段
 */
const validateField = (field: keyof RegisterForm | 'confirmPassword') => {
  clearFieldError(field)
  showTermsError.value = false

  let error = ''
  switch (field) {
    case 'username':
      error = validateUsername(form.value.username)
      break
    case 'email':
      error = validateEmail(form.value.email)
      break
    case 'password':
      error = validatePassword(form.value.password)
      // 重新验证确认密码
      if (confirmPassword.value) {
        const confirmError = validateConfirmPassword(form.value.password, confirmPassword.value)
        if (confirmError) {
          setFieldError('confirmPassword', confirmError)
        } else {
          clearFieldError('confirmPassword')
        }
      }
      break
    case 'confirmPassword':
      error = validateConfirmPassword(form.value.password, confirmPassword.value)
      break
  }

  if (error) {
    setFieldError(field, error)
  }
}

// 防抖验证函数
const debouncedValidateUsername = debounce(() => validateField('username'), 500)
const debouncedValidateEmail = debounce(() => validateField('email'), 500)
const debouncedValidatePassword = debounce(() => validateField('password'), 500)
const debouncedValidateConfirmPassword = debounce(() => validateField('confirmPassword'), 500)

/**
 * 显示错误提示
 */
const showError = (message: string) => {
  errorMessage.value = message
  showErrorAlert.value = true
}

/**
 * 显示成功提示
 */
const showSuccess = (message: string) => {
  successMessage.value = message
  showSuccessAlert.value = true
}

/**
 * 显示用户协议弹窗
 */
const showTermsModal = () => {
  // TODO: 实现用户协议弹窗
  console.log('显示用户协议')
}

/**
 * 显示隐私政策弹窗
 */
const showPrivacyModal = () => {
  // TODO: 实现隐私政策弹窗
  console.log('显示隐私政策')
}

/**
 * 处理注册
 */
const handleRegister = async () => {
  if (!isFormValid.value || isLoading.value) {
    if (!acceptTerms.value) {
      showTermsError.value = true
    }
    return
  }

  // 清除之前的错误
  clearAllErrors()
  showErrorAlert.value = false
  showSuccessAlert.value = false
  showTermsError.value = false

  // 最终验证
  const usernameError = validateUsername(form.value.username)
  const emailError = validateEmail(form.value.email)
  const passwordError = validatePassword(form.value.password)
  const confirmError = validateConfirmPassword(form.value.password, confirmPassword.value)

  if (usernameError) {
    setFieldError('username', usernameError)
    return
  }
  if (emailError) {
    setFieldError('email', emailError)
    return
  }
  if (passwordError) {
    setFieldError('password', passwordError)
    return
  }
  if (confirmError) {
    setFieldError('confirmPassword', confirmError)
    return
  }

  isLoading.value = true

  try {
    // 使用 Pinia store 注册
    await userStore.register(
      form.value.username,
      form.value.email,
      form.value.password
    )

    showSuccess('注册成功!3秒后跳转到登录页面...')

    // 清空表单
    form.value = { username: '', email: '', password: '' }
    confirmPassword.value = ''
    acceptTerms.value = false

    // 3秒后跳转
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (error: any) {
    console.error('注册失败:', error)
    const message = error.message || '注册失败,请稍后重试'
    showError(message)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  position: fixed;
  top: 0;
  left: 0;
}

.register-card {
  width: 100%;
  max-width: 520px;
  background: var(--card-background);
  border-radius: 20px;
  padding: 48px 40px;
  box-shadow:
    0 10px 40px rgba(37, 99, 235, 0.12),
    0 2px 8px rgba(0, 0, 0, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
  border: 1px solid rgba(37, 99, 235, 0.15);
  animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  max-height: 90vh;
  overflow-y: auto;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.register-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  font-size: 28px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 16px;
}

.register-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

/* 表单 */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.form-control {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-background);
  color: var(--text);
  transition: all 0.2s;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-control:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-control[aria-invalid="true"] {
  border-color: #ef4444;
}

.field-error {
  font-size: 12px;
  color: #ef4444;
}

.error-slide-enter-active,
.error-slide-leave-active {
  transition: all 0.2s ease;
}

.error-slide-enter-from,
.error-slide-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}

.checkbox-group {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
  color: var(--text);
  line-height: 1.6;
}

.checkbox-group input {
  cursor: pointer;
  width: 16px;
  height: 16px;
  margin-top: 2px;
  flex-shrink: 0;
}

.checkbox-group input[aria-invalid="true"] {
  outline: 2px solid #ef4444;
}

.inline-link {
  color: var(--primary);
  text-decoration: none;
  transition: color 0.2s;
}

.inline-link:hover,
.inline-link:focus {
  color: var(--primary-hover);
  outline: none;
  text-decoration: underline;
}

.btn-primary {
  width: 100%;
  padding: 14px 24px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.btn-primary:focus {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 页脚 */
.register-footer {
  margin-top: 24px;
  text-align: center;
  font-size: 14px;
  color: var(--text-muted);
}

.login-link {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  margin-left: 4px;
  transition: color 0.2s;
}

.login-link:hover,
.login-link:focus {
  color: var(--primary-hover);
  outline: none;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-card {
    padding: 32px 24px;
  }

  .register-header h1 {
    font-size: 24px;
  }

  .logo {
    font-size: 24px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .register-card {
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  }
}
</style>
