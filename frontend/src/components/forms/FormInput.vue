<template>
    <div class="form-group">
        <label v-if="label" :for="id" class="form-label">
            {{ label }}
            <span v-if="required" class="required">*</span>
        </label>
        <input :id="id" :type="type" :placeholder="placeholder" :required="required" :disabled="disabled"
            :value="modelValue" :class="{ 'has-error': error }" class="form-input" @input="handleInput" />
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="hint" class="hint-message">{{ hint }}</div>
    </div>
</template>

<script setup lang="ts">

interface Props {
    modelValue: string | number
    label?: string
    placeholder?: string
    type?: 'text' | 'email' | 'password' | 'number' | 'date' | 'tel'
    required?: boolean
    disabled?: boolean
    error?: string
    hint?: string
}

const props = withDefaults(defineProps<Props>(), {
    type: 'text',
    required: false,
    disabled: false
})

const emit = defineEmits<{
    'update:modelValue': [value: string | number]
}>()

const id = Math.random().toString(36).substring(7)

const handleInput = (e: Event) => {
    const target = e.target as HTMLInputElement
    emit('update:modelValue', target.value)
}
</script>

<style scoped>
.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 16px;
}

.form-label {
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
    display: flex;
    align-items: center;
    gap: 4px;
}

.required {
    color: #ef4444;
}

.form-input {
    padding: 10px 12px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--input-bg);
    color: var(--text);
    font-size: 14px;
    transition: all 0.3s ease;
}

.form-input:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    background: var(--input-focus-bg);
}

.form-input:disabled {
    background: var(--surface-variant);
    cursor: not-allowed;
    opacity: 0.6;
}

.form-input.has-error {
    border-color: #ef4444;
}

.form-input.has-error:focus {
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.error-message {
    font-size: 12px;
    color: #ef4444;
    font-weight: 500;
}

.hint-message {
    font-size: 12px;
    color: var(--text-muted);
}
</style>
