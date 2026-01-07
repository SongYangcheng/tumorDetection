<template>
    <div class="form-select-group">
        <label v-if="label" :for="id" class="form-label">
            {{ label }}
            <span v-if="required" class="required">*</span>
        </label>
        <div class="select-wrapper">
            <select :id="id" :value="modelValue" :required="required" :disabled="disabled"
                :class="{ 'has-error': error }" class="form-select" @change="handleChange">
                <option v-if="placeholder" value="">{{ placeholder }}</option>
                <option v-for="opt in options" :key="opt.value" :value="opt.value">
                    {{ opt.label }}
                </option>
            </select>
            <span class="select-arrow">▼</span>
        </div>
        <div v-if="error" class="error-message">{{ error }}</div>
    </div>
</template>

<script setup lang="ts">

interface Option {
    label: string
    value: string | number
}

interface Props {
    modelValue: string | number | undefined
    label?: string
    placeholder?: string
    options: Option[]
    required?: boolean
    disabled?: boolean
    error?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
    'update:modelValue': [value: string | number]
}>()

const id = Math.random().toString(36).substring(7)

const handleChange = (e: Event) => {
    const target = e.target as HTMLSelectElement
    emit('update:modelValue', target.value)
}
</script>

<style scoped>
.form-select-group {
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

.select-wrapper {
    position: relative;
}

.form-select {
    width: 100%;
    padding: 10px 12px;
    padding-right: 32px;
    border: 1px solid var(--border-color);
    border-radius: 8px;
    background: var(--input-bg);
    color: var(--text);
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
    appearance: none;
    -webkit-appearance: none;
    -moz-appearance: none;
}

.form-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-select:disabled {
    background: var(--surface-variant);
    cursor: not-allowed;
    opacity: 0.6;
}

.form-select.has-error {
    border-color: #ef4444;
}

.select-arrow {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: var(--text-muted);
    font-size: 12px;
}

.error-message {
    font-size: 12px;
    color: #ef4444;
    font-weight: 500;
}
</style>
