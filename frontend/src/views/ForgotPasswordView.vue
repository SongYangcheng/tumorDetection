<template>
    <div class="forgot-container">
        <div class="forgot-card">
            <!-- Logo和标题 -->
            <div class="forgot-header">
                <div class="logo">NeuroVision</div>
                <h1>忘记密码</h1>
                <p class="subtitle">输入邮箱地址以重置密码</p>
            </div>

            <!-- Alert Messages -->
            <transition name="alert-slide">
                <div v-if="error" class="alert alert-error">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10" />
                        <line x1="12" y1="8" x2="12" y2="12" />
                        <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                    <span>{{ error }}</span>
                    <button class="alert-close" @click="error = ''">×</button>
                </div>
            </transition>

            <transition name="alert-slide">
                <div v-if="success" class="alert alert-success">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                        <polyline points="22 4 12 14.01 9 11.01"></polyline>
                    </svg>
                    <span>{{ success }}</span>
                </div>
            </transition>

            <!-- Form -->
            <form v-if="!success" class="forgot-form" @submit.prevent="handleSubmit">
                <div class="form-group">
                    <label for="email" class="form-label">邮箱地址</label>
                    <input id="email" v-model="email" type="email" class="form-control" placeholder="输入你的注册邮箱" required
                        :disabled="loading" />
                    <p class="form-hint">我们将发送重置密码链接到此邮箱</p>
                </div>

                <!-- Submit Button -->
                <button type="submit" class="btn-primary" :disabled="loading || !email">
                    <span v-if="loading" class="loading-spinner"></span>
                    {{ loading ? '发送中...' : '发送重置链接' }}
                </button>
            </form>

            <!-- Back to Login -->
            <div class="forgot-footer">
                <router-link to="/login" class="back-link">← 返回登录</router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref('')

const handleSubmit = async () => {
    loading.value = true
    error.value = ''

    try {
        // 这是一个占位符，实际密码重置功能需要后端支持
        // 现在只是演示UI
        success.value = `重置链接已发送到 ${email.value}。请检查你的邮箱。`
        email.value = ''

        // 3秒后返回登录页
        setTimeout(() => {
            router.push('/login')
        }, 3000)
    } catch (err: any) {
        error.value = err.message || '发送失败，请稍后重试'
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
.forgot-container {
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

.forgot-card {
    width: 100%;
    max-width: 460px;
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

.forgot-header {
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

.forgot-header h1 {
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

/* 警告提示 */
.alert {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 24px;
    font-size: 14px;
}

.alert-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #ef4444;
}

.alert-success {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #22c55e;
}

.alert svg {
    flex-shrink: 0;
}

.alert span {
    flex: 1;
}

.alert-close {
    background: none;
    border: none;
    color: inherit;
    font-size: 24px;
    cursor: pointer;
    padding: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.alert-close:hover {
    opacity: 1;
}

.alert-slide-enter-active,
.alert-slide-leave-active {
    transition: all 0.3s ease;
}

.alert-slide-enter-from,
.alert-slide-leave-to {
    opacity: 0;
    transform: translateY(-10px);
}

/* 表单 */
.forgot-form {
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

.form-hint {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
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
.forgot-footer {
    margin-top: 24px;
    text-align: center;
    font-size: 14px;
}

.back-link {
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
    transition: color 0.2s;
}

.back-link:hover {
    color: var(--primary-hover);
}

/* 响应式设计 */
@media (max-width: 480px) {
    .forgot-card {
        padding: 32px 24px;
    }

    .forgot-header h1 {
        font-size: 24px;
    }

    .logo {
        font-size: 24px;
    }
}
</style>
