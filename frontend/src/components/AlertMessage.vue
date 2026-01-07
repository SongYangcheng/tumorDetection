<template>
  <Transition name="alert-slide">
    <div v-if="modelValue" :class="['alert', `alert-${type}`]" role="alert" :aria-live="type === 'error' ? 'assertive' : 'polite'">
      <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <component :is="iconPath" />
      </svg>
      <span class="alert-message">{{ message }}</span>
      <button
        v-if="dismissible"
        @click="handleClose"
        class="alert-close"
        type="button"
        aria-label="关闭提示"
      >
        ×
      </button>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  type?: 'error' | 'success' | 'info' | 'warning'
  message: string
  dismissible?: boolean
  autoDismiss?: number // 自动关闭时间(毫秒)
}

const props = withDefaults(defineProps<Props>(), {
  type: 'info',
  dismissible: true,
  autoDismiss: 0
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

// 图标组件
const iconPath = computed(() => {
  switch (props.type) {
    case 'error':
      return `
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="8" x2="12" y2="12"/>
        <line x1="12" y1="16" x2="12.01" y2="16"/>
      `
    case 'success':
      return `
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
        <polyline points="22 4 12 14.01 9 11.01"/>
      `
    case 'warning':
      return `
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      `
    default:
      return `
        <circle cx="12" cy="12" r="10"/>
        <line x1="12" y1="16" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12.01" y2="8"/>
      `
  }
})

const handleClose = () => {
  emit('update:modelValue', false)
}

// 自动关闭
if (props.autoDismiss > 0) {
  setTimeout(() => {
    handleClose()
  }, props.autoDismiss)
}
</script>

<style scoped>
.alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 14px;
  animation: shake 0.3s ease-in-out;
}

.alert-icon {
  flex-shrink: 0;
}

.alert-message {
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

.alert-warning {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #f59e0b;
}

.alert-info {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #3b82f6;
}

/* 动画 */
.alert-slide-enter-active,
.alert-slide-leave-active {
  transition: all 0.3s ease;
}

.alert-slide-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.alert-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
