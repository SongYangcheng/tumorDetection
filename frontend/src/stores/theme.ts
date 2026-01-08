import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type Theme = 'dark' | 'light'

export const useThemeStore = defineStore('theme', () => {
    // 从localStorage读取保存的主题，默认为dark
    const currentTheme = ref<Theme>((localStorage.getItem('theme') as Theme) || 'dark')

    // 应用主题到DOM
    const applyTheme = (theme: Theme) => {
        document.documentElement.setAttribute('data-theme', theme)
    }

    // 切换主题
    const toggleTheme = () => {
        currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
    }

    // 设置特定主题
    const setTheme = (theme: Theme) => {
        currentTheme.value = theme
    }

    // 监听主题变化，保存到localStorage并应用
    watch(
        currentTheme,
        (newTheme) => {
            localStorage.setItem('theme', newTheme)
            applyTheme(newTheme)
        },
        { immediate: true }
    )

    return {
        currentTheme,
        toggleTheme,
        setTheme
    }
})
