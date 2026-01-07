<template>
  <div class="workbench-container">
    <div class="workbench-header">
      <h2>智能分割工作台</h2>
      <p class="subtitle">基于YOLO11的脑肿瘤智能分割</p>
    </div>

    <div class="workbench-content">
      <!-- 左侧：配置面板 -->
      <div class="config-panel">
        <div class="panel-card">
          <h3 class="panel-title">分割配置</h3>

          <!-- 模型类型选择 -->
          <div class="form-group">
            <label class="form-label">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3" />
                <path d="M12 1v6m0 6v6M5.6 5.6l4.2 4.2m4.2 4.2l4.2 4.2M1 12h6m6 0h6M5.6 18.4l4.2-4.2m4.2-4.2l4.2-4.2" />
              </svg>
              模型类型
            </label>
            <div class="radio-group">
              <label class="radio-label">
                <input type="radio" v-model="modelType" value="yolo" @change="onModelTypeChange" />
                <span>YOLO11 (快速，实时)</span>
              </label>
              <label class="radio-label">
                <input type="radio" v-model="modelType" value="unet" @change="onModelTypeChange" />
                <span>UNet (精确，深度学习)</span>
              </label>
            </div>
            <span class="form-hint">YOLO适合快速检测，UNet适合精确分割</span>
          </div>

          <div class="form-group">
            <label class="form-label">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z" />
                <polyline points="13 2 13 9 20 9" />
              </svg>
              模型权重文件
            </label>
            <select v-model="weightPath" class="form-select">
              <option value="" v-if="modelType === 'yolo'">默认YOLO模型（Yolov11_best.pt）</option>
              <option value="" v-if="modelType === 'unet'">默认UNet模型（ResNeXt50_best.pt）</option>
              <option v-for="weight in availableWeights" :key="weight.path" :value="weight.path">
                {{ weight.name }} {{ weight.size ? `(${weight.size})` : '' }}
              </option>
            </select>
            <span class="form-hint">选择训练好的权重文件</span>
          </div>

          <div class="form-group">
            <label class="form-label">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 6v6l4 2" />
              </svg>
              置信度阈值
            </label>
            <div class="slider-group">
              <input v-model.number="conf" type="range" min="0" max="1" step="0.01" class="slider" />
              <span class="slider-value">{{ (conf * 100).toFixed(0) }}%</span>
            </div>
            <span class="form-hint">控制检测敏感度，越高越精确</span>
          </div>

          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button class="btn btn-primary" :disabled="running || !imageId" @click="runSeg">
              <svg v-if="!running" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3" />
              </svg>
              <span v-if="running" class="spinner"></span>
              {{ running ? '分割中...' : '开始分割' }}
            </button>
            <button class="btn btn-secondary" :disabled="running || !imageId" @click="compareModels">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" />
              </svg>
              {{ running ? '对比中...' : '模型对比' }}
            </button>
            <button class="btn btn-secondary" :disabled="!overlay || running" @click="exportOverlay">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              导出结果
            </button>
          </div>

          <!-- 错误提示 -->
          <transition name="fade">
            <div v-if="error" class="alert alert-error">
              <span>{{ error }}</span>
              <button @click="error = ''" class="alert-close" type="button">×</button>
            </div>
          </transition>

          <!-- 提示信息 -->
          <div v-if="!imageId" class="info-box">
            <div>
              <p style="margin: 0 0 8px 0; font-weight: 600;">请从数据管理页面选择影像</p>
              <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                操作流程：数据管理 → 选择影像 → 开始分析 → 配置参数 → 开始分割
              </p>
            </div>
          </div>

          <div v-else-if="!running && !overlay && !error" class="info-box success">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <div>
              <p style="margin: 0 0 8px 0; font-weight: 600;">影像已加载成功</p>
              <p style="margin: 0; font-size: 12px; opacity: 0.8;">
                影像ID: {{ imageId }} | 配置参数后点击"开始分割"按钮
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：结果展示 -->
      <div class="result-panel">
        <!-- 模型对比结果 -->
        <div v-if="comparisonResult" class="panel-card comparison-panel">
          <h3 class="panel-title">模型对比结果</h3>

          <div class="comparison-images">
            <div class="comparison-col">
              <h4>YOLO11 结果</h4>
              <img :src="comparisonResult.yolo_overlay_url" alt="YOLO结果" />
              <div class="metrics-card">
                <div class="metric-item">
                  <span class="metric-label">肿瘤占比</span>
                  <span class="metric-value">{{ (comparisonResult.yolo_metrics.tumor_ratio).toFixed(2) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">实例数</span>
                  <span class="metric-value">{{ comparisonResult.yolo_metrics.num_instances }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">置信度</span>
                  <span class="metric-value">{{ (comparisonResult.yolo_metrics.avg_confidence * 100).toFixed(1)
                  }}%</span>
                </div>
              </div>
            </div>

            <div class="comparison-col">
              <h4>UNet 结果</h4>
              <img :src="comparisonResult.unet_overlay_url" alt="UNet结果" />
              <div class="metrics-card">
                <div class="metric-item">
                  <span class="metric-label">肿瘤占比</span>
                  <span class="metric-value">{{ (comparisonResult.unet_metrics.tumor_ratio).toFixed(2) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">实例数</span>
                  <span class="metric-value">{{ comparisonResult.unet_metrics.num_instances }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">置信度</span>
                  <span class="metric-value">{{ (comparisonResult.unet_metrics.avg_confidence * 100).toFixed(1)
                  }}%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="diff-summary">
            <h4>差异分析</h4>
            <div class="diff-items">
              <div class="diff-item">
                <span class="diff-label">肿瘤比例差异</span>
                <span class="diff-value" :class="getDiffClass(comparisonResult.metrics_diff.tumor_ratio_diff)">
                  {{ comparisonResult.metrics_diff.tumor_ratio_diff > 0 ? '+' : '' }}{{
                    comparisonResult.metrics_diff.tumor_ratio_diff.toFixed(2) }}%
                </span>
              </div>
              <div class="diff-item">
                <span class="diff-label">置信度差异</span>
                <span class="diff-value" :class="getDiffClass(comparisonResult.metrics_diff.confidence_diff)">
                  {{ comparisonResult.metrics_diff.confidence_diff > 0 ? '+' : '' }}{{
                    (comparisonResult.metrics_diff.confidence_diff * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="diff-item">
                <span class="diff-label">实例数差异</span>
                <span class="diff-value" :class="getDiffClass(comparisonResult.metrics_diff.instances_diff)">
                  {{ comparisonResult.metrics_diff.instances_diff > 0 ? '+' : '' }}{{
                    comparisonResult.metrics_diff.instances_diff }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 分割结果 - 仅在非对比模式下显示 -->
        <div v-if="!comparisonResult" class="panel-card">
          <h3 class="panel-title">分割结果</h3>

          <div class="result-viewer">
            <div v-if="running" class="loading-state">
              <div class="loading-spinner"></div>
              <p>正在处理中，请稍候...</p>
            </div>

            <div v-else-if="overlay" class="result-image">
              <img :src="overlay" alt="分割结果" />
            </div>

            <div v-else class="empty-state">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                <circle cx="8.5" cy="8.5" r="1.5" />
                <polyline points="21 15 16 10 5 21" />
              </svg>
              <p>暂无分割结果</p>
              <span>配置参数后点击"开始分割"</span>
            </div>
          </div>
        </div>

        <!-- 肿瘤详细信息 - 仅在非对比模式下显示 -->
        <div v-if="tumorInfo && !running && !comparisonResult" class="panel-card tumor-details">
          <div class="details-header">
            <button class="btn btn-report" @click="viewAnalysisReport">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
              </svg>
              查看完整报告
            </button>
          </div>

          <div class="info-grid">
            <div class="info-item">
              <div class="info-icon" style="background: #FEF3C7;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2">
                  <path
                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">肿瘤实例数</span>
                <span class="info-value">{{ tumorInfo.num_instances }}</span>
              </div>
            </div>

            <div class="info-item">
              <div class="info-icon" style="background: #DBEAFE;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <rect x="7" y="7" width="10" height="10" />
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">肿瘤面积占比</span>
                <span class="info-value">{{ tumorInfo.tumor_ratio.toFixed(2) }}%</span>
              </div>
            </div>

            <div class="info-item">
              <div class="info-icon" style="background: #DCFCE7;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">平均置信度</span>
                <span class="info-value">{{ (tumorInfo.avg_confidence * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div class="info-item">
              <div class="info-icon" style="background: #FCE7F3;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EC4899" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">风险等级</span>
                <span class="info-value" :class="`risk-${tumorInfo.risk_level}`">
                  {{ getRiskLabel(tumorInfo.risk_level) }}
                </span>
              </div>
            </div>

            <!-- <div class="info-item">
              <div class="info-icon" style="background: #F3E8FF;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="2">
                  <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                </svg>
              </div>
              <div class="info-content">
                <span class="info-label">手术可达性</span>
                <span class="info-value">{{ getAccessibilityLabel(tumorInfo.surgical_accessibility) }}</span>
              </div>
            </div> -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'
import type { YoloInstance } from '@/services/api'

const ROOT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const conf = ref(0.25)
const running = ref(false)
const overlay = ref<string>('')
const error = ref('')
const imageId = ref<string>('')
const weightPath = ref<string>('')
const modelType = ref<'yolo' | 'unet'>('yolo')
const availableWeights = ref<any[]>([])
const comparisonResult = ref<any>(null)

interface TumorInfo {
  has_tumor: boolean
  num_instances: number
  tumor_ratio: number
  avg_confidence: number
  risk_level: string
  surgical_accessibility: string
  location: string
  instances: YoloInstance[]
}

const tumorInfo = ref<TumorInfo | null>(null)

const route = useRoute()
const router = useRouter()

onMounted(async () => {
  const q = route.query?.imageId as string | undefined
  const w = route.query?.weightPath as string | undefined

  console.log('[WorkbenchView加载] imageId:', q)

  if (q) {
    imageId.value = q
    try {
      const info = await api.getMedicalImage(q)
      // 可以在这里预加载图像信息
    } catch (err) {
      console.error('加载图像信息失败:', err)
    }
  }

  if (w) {
    weightPath.value = w
  } else {
    const saved = localStorage.getItem('model_weight_path')
    if (saved) weightPath.value = saved
  }

  // 加载可用的权重文件
  try {
    const weights = await api.listWeights()
    // 根据模型类型加载权重
    onModelTypeChange()
  } catch (err) {
    console.error('加载权重列表失败:', err)
  }
})

const runSeg = async () => {
  running.value = true
  overlay.value = ''
  error.value = ''
  tumorInfo.value = null
  comparisonResult.value = null // 清除对比结果

  try {
    if (!imageId.value) {
      throw new Error('未指定影像ID')
    }

    // 保存权重路径
    if (weightPath.value) {
      localStorage.setItem('model_weight_path', weightPath.value)
    }

    // 使用新的模型预测API
    const res = await api.predictWithModel(Number(imageId.value), {
      model_type: modelType.value,
      weight_path: weightPath.value || '',
      conf_threshold: conf.value
    })

    console.log('后端返回的完整数据:', res)
    console.log('data:', res?.data)

    const data = res?.data || {}
    overlay.value = data.overlay_url || ''

    if (!overlay.value) {
      // 即使没有overlay，也显示提示信息而不是报错
      error.value = `${modelType.value === 'yolo' ? 'YOLO' : 'UNet'}模型未检测到肿瘤区域，请尝试调整置信度阈值`
      tumorInfo.value = {
        has_tumor: false,
        num_instances: 0,
        tumor_ratio: 0,
        avg_confidence: 0,
        risk_level: 'low',
        surgical_accessibility: 'moderate',
        location: '未检测到',
        instances: []
      }
      return
    }

    // 提取肿瘤详细信息
    tumorInfo.value = {
      has_tumor: data.has_tumor !== undefined ? data.has_tumor : false,
      num_instances: data.num_instances || 0,
      tumor_ratio: data.tumor_ratio || 0,
      avg_confidence: data.avg_confidence || 0,
      risk_level: data.risk_level || 'low',
      surgical_accessibility: data.surgical_accessibility || 'moderate',
      location: data.location || '位置未知',
      instances: data.instances || []
    }
    console.log('分割完成，肿瘤信息已提取:', tumorInfo.value)
  } catch (e: any) {
    error.value = e?.message || '分割失败，请检查网络连接和参数配置'
    console.error('分割错误:', e)
  } finally {
    running.value = false
  }
}

const getRiskLabel = (level: string) => {
  const labels: Record<string, string> = {
    low: '低风险',
    medium: '中风险',
    high: '高风险'
  }
  return labels[level] || level
}

const getAccessibilityLabel = (accessibility: string) => {
  const labels: Record<string, string> = {
    easy: '易接近',
    moderate: '中等',
    difficult: '困难'
  }
  return labels[accessibility] || accessibility
}

// 模型类型切换时更新可用权重
const onModelTypeChange = async () => {
  try {
    const weights = await api.listWeights()
    if (modelType.value === 'yolo') {
      availableWeights.value = weights.yolo_weights || []
    } else {
      availableWeights.value = weights.unet_weights || []
    }
    // 重置权重选择
    weightPath.value = ''
  } catch (err) {
    console.error('加载权重列表失败:', err)
    availableWeights.value = []
  }
}

// 模型对比
const compareModels = async () => {
  running.value = true
  error.value = ''
  comparisonResult.value = null

  try {
    if (!imageId.value) {
      throw new Error('未指定影像ID')
    }

    const res = await api.compareModels(Number(imageId.value), {
      yolo_weight: 'weights/Yolov11_best.pt',
      unet_weight: 'weights/ResNeXt50_best.pt',
      conf_threshold: conf.value
    })

    console.log('模型对比结果:', res)
    comparisonResult.value = res?.data || null

    if (!comparisonResult.value) {
      throw new Error('对比失败')
    }
  } catch (e: any) {
    error.value = e?.message || '模型对比失败'
    console.error('对比错误:', e)
  } finally {
    running.value = false
  }
}

const viewAnalysisReport = () => {
  if (imageId.value) {
    console.log('跳转到分析报告页面，imageId:', imageId.value)
    router.push({ path: '/analysis-report', query: { imageId: imageId.value } })
  } else {
    console.error('无法跳转到分析报告：imageId 缺失')
    error.value = '无法生成报告：未找到影像ID'
  }
}

const exportOverlay = () => {
  if (!overlay.value) return

  const a = document.createElement('a')
  a.href = overlay.value
  a.download = `segmentation-result-${Date.now()}.png`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

const getDiffClass = (diff: number) => {
  if (diff > 0) return 'diff-positive'
  if (diff < 0) return 'diff-negative'
  return 'diff-neutral'
}
</script>

<style scoped>
.workbench-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.workbench-header {
  margin-bottom: 32px;
}

.workbench-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 8px 0;
}

.subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.workbench-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
}

@media (max-width: 1024px) {
  .workbench-content {
    grid-template-columns: 1fr;
  }
}

/* 面板卡片 */
.panel-card {
  background: var(--card-background);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid var(--border-color);
}

.panel-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 表单组 */
.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.form-label svg {
  color: var(--primary);
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-background);
  color: var(--text);
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--input-background);
  color: var(--text);
  transition: all 0.2s;
  cursor: pointer;
}

.form-select:hover {
  border-color: var(--primary);
}

.form-select:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.form-hint {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-top: 6px;
}

/* 滑块组 */
.slider-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.slider {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: var(--border-color);
  outline: none;
  -webkit-appearance: none;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
  transition: transform 0.2s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--primary);
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(37, 99, 235, 0.3);
}

.slider-value {
  min-width: 50px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-secondary {
  background: var(--surface);
  color: var(--text);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--border-color);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 加载动画 */
.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 警告框 */
.alert {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  margin-top: 16px;
  font-size: 14px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.alert svg {
  flex-shrink: 0;
}

.alert span {
  flex: 1;
}

.alert-close {
  background: none;
  border: none;
  color: inherit;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.6;
  transition: opacity 0.2s;
}

.alert-close:hover {
  opacity: 1;
}

/* 信息框 */
.info-box {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  margin-top: 16px;
  background: rgba(37, 99, 235, 0.08);
  border: 1px solid rgba(37, 99, 235, 0.2);
  color: var(--primary);
  font-size: 13px;
}

.info-box.success {
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.2);
  color: #10B981;
}

.info-box svg {
  flex-shrink: 0;
  margin-top: 2px;
}

.info-box p {
  margin: 0;
}

/* 结果查看器 */
.result-viewer {
  min-height: 500px;
  background: var(--surface);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-state {
  text-align: center;
  color: var(--text-muted);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border-color);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

.loading-state p {
  margin: 0;
  font-size: 14px;
}

.result-image {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-image img {
  max-width: 100%;
  max-height: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.empty-state {
  text-align: center;
  color: var(--text-muted);
}

.empty-state svg {
  margin-bottom: 16px;
  opacity: 0.3;
}

.empty-state p {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 500;
  color: var(--text);
}

.empty-state span {
  font-size: 13px;
  display: block;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 肿瘤详细信息 */
.tumor-details {
  margin-top: 24px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.btn-report {
  padding: 8px 16px;
  background: linear-gradient(135deg, #10B981, #059669);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-report:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(16, 185, 129, 0.3);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.info-item.full-width {
  grid-column: 1 / -1;
}

.info-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.info-value.has-tumor {
  color: #EF4444;
}

.info-value.risk-low {
  color: #10B981;
}

.info-value.risk-medium {
  color: #F59E0B;
}

.info-value.risk-high {
  color: #EF4444;
}

/* 肿瘤实例详情 */
.instances-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.instances-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 16px 0;
}

.instances-list {
  display: grid;
  gap: 12px;
}

.instance-card {
  padding: 14px;
  background: var(--surface);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  transition: all 0.2s;
}

.instance-card:hover {
  border-color: var(--primary);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

.instance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.instance-id {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.instance-conf {
  font-size: 13px;
  font-weight: 600;
  color: #10B981;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.instance-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--text-muted);
}

/* 模型类型选择 */
.radio-group {
  display: flex;
  gap: 16px;
  margin-top: 8px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  transition: all 0.2s;
}

.radio-label:hover {
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.05);
}

.radio-label input[type="radio"] {
  margin: 0;
  cursor: pointer;
}

.radio-label span {
  font-size: 14px;
  color: var(--text);
}

/* 模型对比结果 */
.comparison-panel {
  margin-bottom: 20px;
}

.comparison-images {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin: 16px 0;
}

.comparison-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.comparison-col h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0;
  padding: 8px 12px;
  background: var(--surface);
  border-radius: 8px;
}

.comparison-col img {
  width: 100%;
  border-radius: 12px;
  border: 2px solid var(--border-color);
  transition: all 0.2s;
}

.comparison-col img:hover {
  border-color: var(--primary);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.metrics-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.metric-label {
  font-size: 13px;
  color: var(--text-muted);
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary);
}

.diff-summary {
  margin-top: 16px;
  padding: 16px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border-color);
}

.diff-summary h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 12px 0;
}

.diff-items {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.diff-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  background: var(--background);
  border-radius: 8px;
}

.diff-label {
  font-size: 12px;
  color: var(--text-muted);
}

.diff-value {
  font-size: 16px;
  font-weight: 700;
}

.diff-value.diff-positive {
  color: #EF4444;
}

.diff-value.diff-negative {
  color: #10B981;
}

.diff-value.diff-neutral {
  color: var(--text-muted);
}
</style>
