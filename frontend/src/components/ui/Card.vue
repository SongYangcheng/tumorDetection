<template>
    <div class="card-component" :class="{ 'card-hover': interactive, [variant]: true }">
        <slot />
    </div>
</template>

<script setup lang="ts">
interface Props {
    variant?: 'default' | 'elevated' | 'outlined' | 'filled'
    interactive?: boolean
}

withDefaults(defineProps<Props>(), {
    variant: 'default',
    interactive: false
})
</script>

<style scoped>
.card-component {
    border-radius: 12px;
    padding: 16px;
    transition: all 0.3s ease;
}

.default {
    background: var(--card-bg);
    border: 1px solid var(--border-color);
}

.elevated {
    background: var(--card-bg);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.outlined {
    background: transparent;
    border: 2px solid var(--border-color);
}

.filled {
    background: var(--surface-variant);
}

.card-hover:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
</style>
