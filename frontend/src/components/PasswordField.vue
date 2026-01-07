<template>
  <div class="password-field">
    <label v-if="label" :for="id" class="form-label">{{ label }}</label>
    <div class="password-input">
      <input
        :id="id"
        :value="modelValue"
        :type="showPassword ? 'text' : 'password'"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :aria-invalid="!!error"
        :aria-describedby="error ? `${id}-error` : undefined"
        class="form-control"
        @input="handleInput"
        @blur="$emit('blur')"
        @focus="$emit('focus')"
      />
      <button
        type="button"
        @click="togglePassword"
        class="password-toggle"
        :aria-label="showPassword ? '隐藏密码' : '显示密码'"
        tabindex="-1"
      >
        <svg v-if="!showPassword" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
          <circle cx="12" cy="12" r="3"/>
        </svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
          <line x1="1" y1="1" x2="23" y2="23"/>
        </svg>
      </button>
    </div>
    
    <!-- 密码强度指示器 -->
    <div v-if="showStrength && modelValue" class="password-strength">
      <div class="strength-bar" :class="strength.class" :style="{ width: `${(strength.score / 6) * 100}%` }"></div>
      <span class="strength-text">密码强度: {{ strength.text }}</span>
    </div>
    
    <!-- 错误提示 -->
    <Transition name="error-slide">
      <span v-if="error" :id="`${id}-error`" class="field-error" role="alert">
        {{ error }}
      </span>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PasswordStrength } from '../types'
import { useFormValidation } from '../composables/useFormValidation'

interface Props {
  id: string
  modelValue: string
  label?: string
  placeholder?: string
  required?: boolean
  disabled?: boolean
  autocomplete?: string
  error?: string
  showStrength?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请输入密码',
  autocomplete: 'current-password',
  showStrength: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  blur: []
  focus: []
}>()

const showPassword = ref(false)
const { calculatePasswordStrength } = useFormValidation()

const strength = computed((): PasswordStrength => {
  return calculatePasswordStrength(props.modelValue)
})

const handleInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}
</script>

<style scoped>
.password-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.password-input {
  position: relative;
}

.form-control {
  width: 100%;
  padding: 12px 48px 12px 16px;
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

.password-toggle {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: var(--text);
}

.password-strength {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.strength-bar {
  height: 4px;
  border-radius: 2px;
  transition: all 0.3s;
}

.strength-bar.weak {
  background: #ef4444;
}

.strength-bar.medium {
  background: #f59e0b;
}

.strength-bar.strong {
  background: #22c55e;
}

.strength-text {
  font-size: 12px;
  color: var(--text-muted);
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
</style>
