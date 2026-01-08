import { watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'
import { darkTheme, lightTheme } from './echarts-theme'
import type { EChartsOption } from 'echarts'

/**
 * 使用响应式的ECharts主题
 * 当系统主题切换时自动更新图表
 */
export function useEChartsTheme(chartInstance: any) {
    const themeStore = useThemeStore()
    const { currentTheme } = storeToRefs(themeStore)

    // 获取当前主题配置
    const getThemeOption = () => {
        return currentTheme.value === 'dark' ? darkTheme : lightTheme
    }

    // 监听主题变化，自动更新图表
    watch(currentTheme, () => {
        if (chartInstance.value) {
            const currentOption = chartInstance.value.getOption()
            const themeOption = getThemeOption()

            // 合并主题配置并更新
            chartInstance.value.setOption({
                ...themeOption,
                ...currentOption
            }, true)
        }
    })

    return {
        getThemeOption,
        currentTheme
    }
}

/**
 * 应用主题到ECharts配置
 */
export function applyThemeToOption(option: EChartsOption): EChartsOption {
    const themeStore = useThemeStore()
    const theme = themeStore.currentTheme === 'dark' ? darkTheme : lightTheme

    // 深度合并配置，排除radar等复杂类型
    const result: any = {
        ...option,
        // 基础颜色
        color: option.color || theme.color,
        backgroundColor: option.backgroundColor || theme.backgroundColor,

        // 文本样式
        textStyle: {
            ...theme.textStyle,
            ...option.textStyle
        },

        // 标题
        title: option.title || theme.title,

        // 图例
        legend: option.legend || theme.legend,

        // 工具提示
        tooltip: {
            ...theme.tooltip,
            ...option.tooltip
        },

        // 坐标轴
        xAxis: option.xAxis || theme.categoryAxis,
        yAxis: option.yAxis || theme.valueAxis,

        // 时间轴
        timeline: option.timeline || theme.timeline
    }

    return result as EChartsOption
}

/**
 * 获取当前主题的颜色数组
 */
export function getThemeColors(): string[] {
    const themeStore = useThemeStore()
    const theme = themeStore.currentTheme === 'dark' ? darkTheme : lightTheme
    return theme.color as string[]
}
