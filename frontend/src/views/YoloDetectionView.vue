<template>
  <div class="yolo-detection-results">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>正在进行YOLO11脑肿瘤检测...</p>
    </div>

    <!-- 检测失败 -->
    <div v-else-if="error" class="error-state">
      <p>{{ error }}</p>
      <button @click="retryDetection" class="retry-btn">重试</button>
    </div>

    <!-- 检测成功 -->
    <div v-else-if="results" class="results-container">
      <!-- 顶部摘要 -->
      <div class="summary-section">
        <div class="summary-header">
          <h2>YOLO11脑肿瘤检测报告</h2>
          <span class="detection-time">{{ formatTime(results.diagnostic_report.detection_time) }}</span>
        </div>

        <!-- 诊断结论 -->
        <div class="diagnosis-box" :class="results.has_tumor ? 'has-tumor' : 'no-tumor'">
          <div class="diagnosis-result">
            <div class="text">
              <p class="label">诊断结论</p>
              <p class="value">
                {{ results.diagnostic_report.recommendation }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 关键指标 -->
      <div class="metrics-section">
        <h3>关键指标</h3>
        <div class="metrics-grid">
          <div class="metric-card">
            <span class="metric-label">肿瘤检测</span>
            <span class="metric-value">{{ results.num_instances }}</span>
            <span class="metric-unit">个实例</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">肿瘤占比</span>
            <span class="metric-value">{{ results.tumor_ratio }}</span>
            <span class="metric-unit">%</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">平均置信度</span>
            <span class="metric-value">{{ (results.avg_confidence * 100).toFixed(1) }}</span>
            <span class="metric-unit">%</span>
          </div>
          <div class="metric-card">
            <span class="metric-label">推理耗时</span>
            <span class="metric-value">{{ results.inference_time }}</span>
            <span class="metric-unit">秒</span>
          </div>
        </div>
      </div>

      <!-- 术前规划信息 -->
      <div class="surgical-planning-section">
        <h3>术前规划参考</h3>
        <div class="planning-grid">
          <!-- 风险等级 -->
          <div class="planning-card">
            <div class="card-header">
              <span class="title">风险等级</span>
            </div>
            <div class="card-content">
              <span class="risk-badge" :class="`risk-${results.risk_level}`">
                {{ riskLevelText(results.risk_level) }}
              </span>
            </div>
          </div>

          <!-- 手术可达性 -->
          <div class="planning-card">
            <div class="card-header">
              <span class="title">手术可达性</span>
            </div>
            <div class="card-content">
              <span class="accessibility-badge" :class="`access-${results.surgical_accessibility}`">
                {{ accessibilityText(results.surgical_accessibility) }}
              </span>
            </div>
          </div>

          <!-- 肿瘤位置 -->
          <div class="planning-card">
            <div class="card-header">
              <span class="title">肿瘤位置</span>
            </div>
            <div class="card-content">
              <p class="location-text">{{ results.location }}</p>
            </div>
          </div>

          <!-- 分割质量 -->
          <div class="planning-card">
            <div class="card-header">
              <span class="title">分割质量</span>
            </div>
            <div class="card-content">
              <div class="quality-bar">
                <div class="quality-fill" :style="{ width: (results.segmentation_quality * 100) + '%' }"></div>
              </div>
              <span class="quality-text">{{ (results.segmentation_quality * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分割掩码可视化 -->
      <div class="visualization-section">
        <h3>分割结果可视化</h3>
        <div class="visualization-grid">
          <!-- 原始图像 -->
          <div class="viz-card">
            <h4>原始影像</h4>
            <img v-if="originalImage" :src="originalImage" alt="原始影像" class="viz-image" />
          </div>

          <!-- 分割掩码 -->
          <div class="viz-card">
            <h4>分割掩码</h4>
            <img v-if="results.mask_url" :src="`http://127.0.0.1:8000${results.mask_url}`" alt="分割掩码"
              class="viz-image" />
          </div>

          <!-- 掩码叠加 -->
          <div class="viz-card">
            <h4>掩码叠加</h4>
            <img v-if="results.overlay_url" :src="`http://127.0.0.1:8000${results.overlay_url}`" alt="掩码叠加"
              class="viz-image" />
          </div>
        </div>
      </div>

      <!-- 实例详情 -->
      <div v-if="results.instances && results.instances.length > 0" class="instances-section">
        <h3>检测实例详情</h3>
        <div class="instances-table">
          <table>
            <thead>
              <tr>
                <th>实例ID</th>
                <th>置信度</th>
                <th>位置 (x1, y1)</th>
                <th>大小 (x2, y2)</th>
                <th>面积 (像素²)</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="instance in results.instances" :key="instance.instance_id">
                <td>#{{ instance.instance_id }}</td>
                <td>
                  <span class="confidence-badge">{{ (instance.confidence * 100).toFixed(1) }}%</span>
                </td>
                <td>({{ instance.bbox.x1 }}, {{ instance.bbox.y1 }})</td>
                <td>({{ instance.bbox.x2 }}, {{ instance.bbox.y2 }})</td>
                <td>{{ instance.area.toLocaleString() }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 行动按钮 -->
      <div class="action-buttons">
        <button @click="openPreOpPlanning" class="btn btn-primary">
          跳转到术前规划
        </button>
        <button @click="downloadReport" class="btn btn-secondary">
          下载报告
        </button>
        <button @click="goBack" class="btn btn-outline">
          返回
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '@/services/api'
import type { YoloResultsResponse } from '@/services/api'

const router = useRouter()
const route = useRoute()

const imageId = computed(() => parseInt(route.params.imageId as string))
const loading = ref(false)
const error = ref('')
const results = ref<YoloResultsResponse['data'] | null>(null)
const originalImage = ref('')

// 风险等级文本
const riskLevelText = (level: string) => {
  const map: Record<string, string> = {
    low: '低风险',
    medium: '中等风险',
    high: '高风险'
  }
  return map[level] || level
}

// 手术可达性文本
const accessibilityText = (access: string) => {
  const map: Record<string, string> = {
    easy: '易于接近',
    moderate: '中等难度',
    difficult: '难以接近'
  }
  return map[access] || access
}

// 格式化时间
const formatTime = (timeStr: string) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 获取YOLO检测结果
const fetchResults = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.getYoloResults(imageId.value)
    if (response.success) {
      results.value = response.data
      // 获取原始图像
      const imageData = await api.getMedicalImage(imageId.value)
      if (imageData.preview_url) {
        originalImage.value = `http://127.0.0.1:8000${imageData.preview_url}`
      }
    } else {
      error.value = response.message || '获取结果失败'
    }
  } catch (err: any) {
    error.value = err.message || '获取结果失败'
  } finally {
    loading.value = false
  }
}

// 执行检测（如果还未检测）
const performDetection = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api.yoloDetect(imageId.value)
    if (response.success) {
      results.value = response.data
      const imageData = await api.getMedicalImage(imageId.value)
      if (imageData.preview_url) {
        originalImage.value = `http://127.0.0.1:8000${imageData.preview_url}`
      }
    } else {
      error.value = response.message || '检测失败'
    }
  } catch (err: any) {
    error.value = err.message || '检测失败'
  } finally {
    loading.value = false
  }
}

// 重试检测
const retryDetection = async () => {
  await performDetection()
}

// 跳转到术前规划
const openPreOpPlanning = () => {
  router.push(`/preop-planning/${imageId.value}`)
}

// 下载报告
const downloadReport = () => {
  if (!results.value) return

  const report = {
    title: 'YOLO11脑肿瘤检测报告',
    timestamp: new Date().toLocaleString('zh-CN'),
    diagnostic_report: results.value.diagnostic_report,
    metrics: {
      tumor_detected: results.value.has_tumor,
      num_instances: results.value.num_instances,
      tumor_ratio: results.value.tumor_ratio,
      avg_confidence: results.value.avg_confidence,
      tumor_pixels: results.value.tumor_pixels,
      total_pixels: results.value.total_pixels
    },
    surgical_planning: {
      risk_level: results.value.risk_level,
      surgical_accessibility: results.value.surgical_accessibility,
      location: results.value.location
    },
    quality_metrics: {
      segmentation_quality: results.value.segmentation_quality,
      inference_time: results.value.inference_time,
      model_version: results.value.model_version
    }
  }

  const dataStr = JSON.stringify(report, null, 2)
  const element = document.createElement('a')
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(dataStr))
  element.setAttribute('download', `yolo_report_${imageId.value}_${Date.now()}.json`)
  element.style.display = 'none'
  document.body.appendChild(element)
  element.click()
  document.body.removeChild(element)
}

// 返回
const goBack = () => {
  router.back()
}

onMounted(async () => {
  // 先尝试获取已有结果，如果没有则执行检测
  const response = await api.getYoloResults(imageId.value).catch(() => null)
  if (response?.success && response.data) {
    results.value = response.data
  } else {
    await performDetection()
  }
})
</script>

<style scoped>
.yolo-detection-results {
  width: 100%;
  min-height: 100vh;
  background: transparent;
  padding: 24px;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 16px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid var(--primary-2);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-state {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.error-state p {
  color: #ff6b6b;
  font-weight: 600;
}

.retry-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
}

.retry-btn:hover {
  transform: translateY(-2px);
}

.results-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 摘要部分 */
.summary-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-header h2 {
  margin: 0;
  color: var(--text);
  font-size: 24px;
}

.detection-time {
  color: var(--text-muted);
  font-size: 14px;
}

.diagnosis-box {
  padding: 20px;
  border-radius: var(--radius-md);
  border: 2px solid;
  transition: all 0.3s;
}

.diagnosis-box.has-tumor {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
}

.diagnosis-box.no-tumor {
  background: rgba(16, 185, 129, 0.1);
  border-color: rgba(16, 185, 129, 0.3);
}

.diagnosis-result {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.diagnosis-result .text {
  flex: 1;
}

.diagnosis-result .label {
  color: var(--text-muted);
  font-size: 14px;
  margin: 0;
}

.diagnosis-result .value {
  color: var(--text);
  font-size: 18px;
  font-weight: 600;
  margin: 8px 0 0 0;
}

/* 指标部分 */
.metrics-section h3,
.surgical-planning-section h3,
.visualization-section h3,
.instances-section h3 {
  color: var(--text);
  margin: 0 0 16px 0;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 16px;
  text-align: center;
  backdrop-filter: blur(8px);
}

.metric-label {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.metric-value {
  display: block;
  color: var(--text);
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 4px;
}

.metric-unit {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
}

/* 术前规划部分 */
.surgical-planning-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.planning-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.planning-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 16px;
}

.card-header {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
}

.card-header .title {
  color: var(--text);
  font-weight: 600;
}

.card-content {
  color: var(--text);
}

.risk-badge,
.accessibility-badge {
  display: inline-block;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 14px;
}

.risk-low {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.risk-medium {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.risk-high {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.access-easy {
  background: rgba(16, 185, 129, 0.15);
  color: #10B981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.access-moderate {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.access-difficult {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.location-text {
  margin: 0;
  color: var(--text);
  line-height: 1.5;
}

.quality-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.quality-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--primary-2));
  transition: width 0.3s ease;
}

.quality-text {
  display: block;
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 4px;
}

/* 可视化部分 */
.visualization-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.visualization-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.viz-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-md);
  padding: 12px;
  overflow: hidden;
}

.viz-card h4 {
  color: var(--text);
  margin: 0 0 12px 0;
  font-size: 14px;
}

.viz-image {
  width: 100%;
  height: auto;
  max-height: 300px;
  object-fit: contain;
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.02);
}

/* 实例表格 */
.instances-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.instances-table {
  overflow-x: auto;
}

.instances-table table {
  width: 100%;
  border-collapse: collapse;
}

.instances-table th {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.instances-table td {
  color: var(--text);
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.instances-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.confidence-badge {
  background: rgba(37, 99, 235, 0.15);
  color: #38bdf8;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 12px;
}

/* 行动按钮 */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.btn {
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.btn-secondary {
  background: linear-gradient(135deg, var(--accent), var(--primary-2));
  color: white;
  box-shadow: 0 4px 12px rgba(34, 211, 238, 0.3);
}

.btn-secondary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(34, 211, 238, 0.4);
}

.btn-outline {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--border);
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
}

@media (max-width: 768px) {
  .yolo-detection-results {
    padding: 12px;
  }

  .metrics-grid,
  .planning-grid,
  .visualization-grid {
    grid-template-columns: 1fr;
  }

  .summary-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .action-buttons {
    flex-direction: column;
  }

  .btn {
    width: 100%;
  }
}
</style>
