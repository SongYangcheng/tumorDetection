<template>
    <div ref="chartRef" :style="{ width: width, height: height }" class="echart-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { EChartsOption } from 'echarts'

interface Props {
    option: EChartsOption
    width?: string
    height?: string
    theme?: string
}

const props = withDefaults(defineProps<Props>(), {
    width: '100%',
    height: '300px',
    theme: 'dark'
})

const chartRef = ref<HTMLElement>()
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
    if (!chartRef.value) return

    // 初始化图表实例
    chartInstance = echarts.init(chartRef.value, props.theme)
    chartInstance.setOption(props.option)

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize)
}

const handleResize = () => {
    chartInstance?.resize()
}

const updateChart = () => {
    if (chartInstance) {
        chartInstance.setOption(props.option, true)
    }
}

// 监听option变化
watch(() => props.option, () => {
    updateChart()
}, { deep: true })

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
