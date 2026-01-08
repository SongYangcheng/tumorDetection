<template>
  <div class="radiomics-view">
    <div class="page-header">
      <div>
        <h1>影像组学分析</h1>
        <p class="subtitle">基于深度特征提取的肿瘤影像组学分析</p>
      </div>
      <button class="btn btn-primary" @click="extractFeatures" :disabled="loading || !selectedImage">
        <svg v-if="!loading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
          <polyline points="7 10 12 15 17 10" />
          <line x1="12" y1="15" x2="12" y2="3" />
        </svg>
        <span class="spinner" v-else></span>
        {{ loading ? '提取中...' : '提取特征' }}
      </button>
    </div>

    <!-- 图像选择器 -->
    <div class="card image-selector" v-if="!selectedImage">
      <h3>选择医学影像</h3>
      <div class="image-grid">
        <div v-for="img in images" :key="img.id" class="image-card" @click="selectImage(img)">
          <img :src="img.preview_url || img.file_url" :alt="img.filename" />
          <div class="image-info">
            <p class="filename">{{ img.filename }}</p>
            <p class="date">{{ formatDate(img.uploaded_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 特征展示区 -->
    <div v-if="selectedImage" class="radiomics-content">
      <!-- 图像信息卡片 -->
      <div class="card image-info-card">
        <div class="card-header">
          <h3>影像信息</h3>
          <button class="btn" @click="changeImage">更换影像</button>
        </div>
        <div class="image-preview">
          <img :src="selectedImage.preview_url || selectedImage.file_url" :alt="selectedImage.filename" />
        </div>
        <div class="info-list">
          <div class="info-item">
            <span class="label">文件名:</span>
            <span class="value">{{ selectedImage.filename }}</span>
          </div>
          <div class="info-item">
            <span class="label">上传时间:</span>
            <span class="value">{{ formatDate(selectedImage.uploaded_at) }}</span>
          </div>
          <div class="info-item">
            <span class="label">影像尺寸:</span>
            <span class="value">{{ selectedImage.width }} × {{ selectedImage.height }}</span>
          </div>
        </div>
      </div>

      <!-- 特征可视化 -->
      <div class="features-panel">
        <!-- 形状特征 -->
        <div class="card feature-card">
          <h3>形状特征</h3>
          <div v-if="features.shape" class="feature-chart" ref="shapeChart"></div>
          <div v-else class="empty-state">
            <p>暂无数据</p>
            <p class="hint">点击"提取特征"按钮开始分析</p>
          </div>
        </div>

        <!-- 一阶统计特征 -->
        <div class="card feature-card">
          <h3>一阶统计特征</h3>
          <div v-if="features.firstOrder" class="feature-chart" ref="firstOrderChart"></div>
          <div v-else class="empty-state">
            <p>暂无数据</p>
            <p class="hint">点击"提取特征"按钮开始分析</p>
          </div>
        </div>

        <!-- 纹理特征 -->
        <div class="card feature-card">
          <h3>纹理特征（GLCM）</h3>
          <div v-if="features.texture" class="feature-chart" ref="textureChart"></div>
          <div v-else class="empty-state">
            <p>暂无数据</p>
            <p class="hint">点击"提取特征"按钮开始分析</p>
          </div>
        </div>

        <!-- 小波特征 -->
        <div class="card feature-card">
          <h3>小波变换特征</h3>
          <div v-if="features.wavelet" class="feature-chart" ref="waveletChart"></div>
          <div v-else class="empty-state">
            <p>暂无数据</p>
            <p class="hint">点击"提取特征"按钮开始分析</p>
          </div>
        </div>

        <!-- 综合雷达图 -->
        <div class="card feature-card full-width">
          <h3>综合特征雷达图</h3>
          <div v-if="features.shape" class="feature-chart large" ref="radarChart"></div>
          <div v-else class="empty-state">
            <p>暂无数据</p>
            <p class="hint">点击"提取特征"按钮开始分析</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts } from 'echarts'
import { applyThemeToOption, useEChartsTheme } from '@/utils/echarts-utils'
import { storeToRefs } from 'pinia'
import { useThemeStore } from '@/stores/theme'

interface MedicalImage {
  id: number
  filename: string
  file_url: string
  preview_url?: string
  uploaded_at: string
  width?: number
  height?: number
}

interface RadiomicsFeatures {
  shape?: any
  firstOrder?: any
  texture?: any
  wavelet?: any
}

const images = ref<MedicalImage[]>([])
const selectedImage = ref<MedicalImage | null>(null)
const loading = ref(false)
const features = ref<RadiomicsFeatures>({})

// ECharts 实例
const shapeChart = ref<HTMLElement>()
const firstOrderChart = ref<HTMLElement>()
const textureChart = ref<HTMLElement>()
const waveletChart = ref<HTMLElement>()
const radarChart = ref<HTMLElement>()

let shapeChartInstance: ECharts | null = null
let firstOrderChartInstance: ECharts | null = null
let textureChartInstance: ECharts | null = null
let waveletChartInstance: ECharts | null = null
let radarChartInstance: ECharts | null = null

const themeStore = useThemeStore()
const { currentTheme } = storeToRefs(themeStore)

// 监听主题变化
watch(currentTheme, () => {
  nextTick(() => {
    if (features.value.shape) {
      renderCharts()
    }
  })
})

onMounted(() => {
  fetchImages()
})

onUnmounted(() => {
  // 销毁图表实例
  shapeChartInstance?.dispose()
  firstOrderChartInstance?.dispose()
  textureChartInstance?.dispose()
  waveletChartInstance?.dispose()
  radarChartInstance?.dispose()
})

const fetchImages = async () => {
  try {
    // 模拟数据
    images.value = [
      {
        id: 1,
        filename: 'brain_mri_001.png',
        file_url: '/api/placeholder/400/400',
        preview_url: '/api/placeholder/200/200',
        uploaded_at: new Date().toISOString(),
        width: 512,
        height: 512
      }
    ]
  } catch (error) {
    console.error('Failed to fetch images:', error)
  }
}

const selectImage = (img: MedicalImage) => {
  selectedImage.value = img
  features.value = {}
}

const changeImage = () => {
  selectedImage.value = null
  features.value = {}
}

const extractFeatures = async () => {
  if (!selectedImage.value) return

  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 2000))

    // 模拟特征数据
    features.value = {
      shape: {
        area: 1234.5,
        perimeter: 156.7,
        circularity: 0.89,
        convexity: 0.92,
        eccentricity: 0.65,
        solidity: 0.91
      },
      firstOrder: {
        mean: 145.2,
        std: 32.4,
        skewness: 0.45,
        kurtosis: 2.1,
        energy: 0.78,
        entropy: 4.2
      },
      texture: {
        contrast: 23.5,
        correlation: 0.87,
        energy: 0.65,
        homogeneity: 0.82
      },
      wavelet: {
        ll_energy: 0.72,
        lh_energy: 0.15,
        hl_energy: 0.08,
        hh_energy: 0.05
      }
    }

    await nextTick()
    renderCharts()
  } catch (error) {
    console.error('Failed to extract features:', error)
  } finally {
    loading.value = false
  }
}

const renderCharts = () => {
  renderShapeChart()
  renderFirstOrderChart()
  renderTextureChart()
  renderWaveletChart()
  renderRadarChart()
}

const renderShapeChart = () => {
  if (!shapeChart.value || !features.value.shape) return

  if (!shapeChartInstance) {
    shapeChartInstance = echarts.init(shapeChart.value)
  }

  const option = applyThemeToOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    xAxis: {
      type: 'category',
      data: ['面积', '周长', '圆度', '凸度', '偏心率', '实心度']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'bar',
      data: [
        features.value.shape.area / 10,
        features.value.shape.perimeter,
        features.value.shape.circularity * 100,
        features.value.shape.convexity * 100,
        features.value.shape.eccentricity * 100,
        features.value.shape.solidity * 100
      ],
      itemStyle: {
        borderRadius: [8, 8, 0, 0]
      }
    }]
  })

  shapeChartInstance.setOption(option)
}

const renderFirstOrderChart = () => {
  if (!firstOrderChart.value || !features.value.firstOrder) return

  if (!firstOrderChartInstance) {
    firstOrderChartInstance = echarts.init(firstOrderChart.value)
  }

  const option = applyThemeToOption({
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      avoidLabelOverlap: false,
      label: {
        show: true,
        position: 'outside'
      },
      data: [
        { value: features.value.firstOrder.mean, name: '均值' },
        { value: features.value.firstOrder.std, name: '标准差' },
        { value: features.value.firstOrder.energy * 100, name: '能量' },
        { value: features.value.firstOrder.entropy * 10, name: '熵' }
      ]
    }]
  })

  firstOrderChartInstance.setOption(option)
}

const renderTextureChart = () => {
  if (!textureChart.value || !features.value.texture) return

  if (!textureChartInstance) {
    textureChartInstance = echarts.init(textureChart.value)
  }

  const option = applyThemeToOption({
    tooltip: {
      trigger: 'axis'
    },
    radar: {
      indicator: [
        { name: '对比度', max: 30 },
        { name: '相关性', max: 1 },
        { name: '能量', max: 1 },
        { name: '同质性', max: 1 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          features.value.texture.contrast,
          features.value.texture.correlation,
          features.value.texture.energy,
          features.value.texture.homogeneity
        ],
        name: '纹理特征'
      }]
    }]
  })

  textureChartInstance.setOption(option)
}

const renderWaveletChart = () => {
  if (!waveletChart.value || !features.value.wavelet) return

  if (!waveletChartInstance) {
    waveletChartInstance = echarts.init(waveletChart.value)
  }

  const option = applyThemeToOption({
    tooltip: {
      trigger: 'item'
    },
    series: [{
      type: 'pie',
      radius: '65%',
      data: [
        { value: features.value.wavelet.ll_energy, name: 'LL (低频)' },
        { value: features.value.wavelet.lh_energy, name: 'LH' },
        { value: features.value.wavelet.hl_energy, name: 'HL' },
        { value: features.value.wavelet.hh_energy, name: 'HH (高频)' }
      ],
      label: {
        formatter: '{b}: {d}%'
      }
    }]
  })

  waveletChartInstance.setOption(option)
}

const renderRadarChart = () => {
  if (!radarChart.value || !features.value.shape) return

  if (!radarChartInstance) {
    radarChartInstance = echarts.init(radarChart.value)
  }

  const option = applyThemeToOption({
    tooltip: {},
    radar: {
      indicator: [
        { name: '形状规则性', max: 100 },
        { name: '密度均匀性', max: 100 },
        { name: '纹理复杂度', max: 100 },
        { name: '边界清晰度', max: 100 },
        { name: '频域特征', max: 100 },
        { name: '整体质量', max: 100 }
      ]
    },
    series: [{
      type: 'radar',
      data: [{
        value: [
          features.value.shape.circularity * 100,
          85,
          features.value.texture?.contrast || 75,
          90,
          features.value.wavelet?.ll_energy ? features.value.wavelet.ll_energy * 100 : 80,
          88
        ],
        name: '综合评估',
        areaStyle: {
          opacity: 0.3
        }
      }]
    }]
  })

  radarChartInstance.setOption(option)
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 窗口大小改变时重新渲染图表
window.addEventListener('resize', () => {
  shapeChartInstance?.resize()
  firstOrderChartInstance?.resize()
  textureChartInstance?.resize()
  waveletChartInstance?.resize()
  radarChartInstance?.resize()
})
</script>

<style scoped>
.radiomics-view {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
}

.page-header h1 {
  margin: 0;
  font-size: 2rem;
  font-weight: 800;
  color: var(--text);
}

.subtitle {
  margin: 0.5rem 0 0;
  color: var(--text-muted);
}

.image-selector {
  padding: 2rem;
}

.image-selector h3 {
  margin: 0 0 1.5rem;
  color: var(--text);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.image-card {
  padding: 1rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.image-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow);
}

.image-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  margin-bottom: 0.5rem;
}

.image-info {
  text-align: center;
}

.filename {
  margin: 0.5rem 0 0.25rem;
  font-weight: 600;
  color: var(--text);
  font-size: 0.875rem;
}

.date {
  margin: 0;
  color: var(--text-muted);
  font-size: 0.75rem;
}

.radiomics-content {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 1.5rem;
}

.image-info-card {
  padding: 1.5rem;
  height: fit-content;
  position: sticky;
  top: 1rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: var(--text);
}

.image-preview img {
  width: 100%;
  border-radius: var(--radius-md);
  margin-bottom: 1rem;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--border);
}

.info-item .label {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.info-item .value {
  color: var(--text);
  font-weight: 600;
  font-size: 0.875rem;
}

.features-panel {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.feature-card {
  padding: 1.5rem;
}

.feature-card.full-width {
  grid-column: 1 / -1;
}

.feature-card h3 {
  margin: 0 0 1rem;
  font-size: 1rem;
  color: var(--text);
}

.feature-chart {
  width: 100%;
  height: 300px;
}

.feature-chart.large {
  height: 400px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-muted);
}

.empty-state p {
  margin: 0.25rem 0;
}

.hint {
  font-size: 0.875rem;
  color: var(--text-disabled);
}

.spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 1024px) {
  .radiomics-content {
    grid-template-columns: 1fr;
  }

  .image-info-card {
    position: relative;
    top: 0;
  }

  .features-panel {
    grid-template-columns: 1fr;
  }
}
</style>
