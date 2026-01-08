<template>
    <div ref="chartRef" :style="{ width: width, height: height }" class="echart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'
import { applyThemeToOption } from '@/utils/echarts-utils'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'

interface Props {
    option: EChartsOption
    width?: string
    height?: string
}

const props = withDefaults(defineProps<Props>(), {
    width: '100%',
    height: '300px'
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const themeStore = useThemeStore()
const { currentTheme } = storeToRefs(themeStore)

const initChart = () => {
    if (!chartRef.value) return

    // 初始化图表实例
    chartInstance = echarts.init(chartRef.value)
    updateChart()

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
}

const handleResize = () => {
    chartInstance?.resize()
}

const updateChart = () => {
    if (chartInstance) {
        // 应用主题化配置
        const themedOption = applyThemeToOption(props.option)
        chartInstance.setOption(themedOption, true)
    }
}

// 监听option变化
watch(() => props.option, () => {
    updateChart()
}, { deep: true })

// 监听主题变化
watch(currentTheme, () => {
    nextTick(() => {
        updateChart()
    })
})

onMounted(async () => {
    await nextTick()
    initChart()
})

onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
    chartInstance?.dispose()
    chartInstance = null
})
</script>

<style scoped>
.echart-container {
    width: 100%;
    height: 100%;
}
</style>
