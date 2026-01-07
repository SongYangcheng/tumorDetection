<template>
    <button class="button-component" :class="[variant, size, { loading, disabled }]" :type="type"
        :disabled="disabled || loading">
        <span v-if="loading" class="spinner"></span>
        <slot />
    </button>
</template>

<script setup lang="ts">

interface Props {
    variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost'
    size?: 'sm' | 'md' | 'lg'
    loading?: boolean
    disabled?: boolean
    type?: 'button' | 'submit' | 'reset'
}

withDefaults(defineProps<Props>(), {
    variant: 'primary',
    size: 'md',
    loading: false,
    disabled: false,
    type: 'button'
})

</script>

<style scoped>
.button-component {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: none;
    font-family: inherit;
}

/* 大小变体 */
.sm {
    padding: 6px 12px;
    font-size: 12px;
}

.md {
    padding: 10px 16px;
    font-size: 14px;
}

.lg {
    padding: 12px 24px;
    font-size: 16px;
}

/* 颜色变体 */
.primary {
    background: linear-gradient(135deg, #3b82f6, #2563eb);
    color: white;
}

.primary:hover:not(.disabled) {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.secondary {
    background: var(--surface-variant);
    color: var(--text);
    border: 1px solid var(--border-color);
}

.secondary:hover:not(.disabled) {
    background: var(--surface-hover);
}

.danger {
    background: #ef4444;
    color: white;
}

.danger:hover:not(.disabled) {
    background: #dc2626;
}

.success {
    background: #22c55e;
    color: white;
}

.success:hover:not(.disabled) {
    background: #16a34a;
}

.ghost {
    background: transparent;
    color: var(--text-secondary);
    border: 1px solid var(--border-color);
}

.ghost:hover:not(.disabled) {
    background: var(--surface-variant);
}

/* 状态 */
.disabled,
.button-component:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.loading {
    opacity: 0.7;
    cursor: wait;
}

.button-component:disabled:hover {
    transform: none;
    box-shadow: none;
}

.spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    animation: spin 0.6s linear infinite;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}
</style>
