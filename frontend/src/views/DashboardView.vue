<template>
  <div class="dashboard-view">
    <!-- 顶部导航栏 -->
    <header class="dashboard-header">
      <div class="header-content">
        <div class="header-title">
          <h1>临床仪表板</h1>
          <p class="subtitle">实时医学影像分析监控</p>
        </div>
        <div class="header-actions">
          <button class="refresh-btn" @click="refreshData" :disabled="loading">
            <span v-if="!loading">刷新数据</span>
            <span v-else>加载中...</span>
          </button>
          <span class="last-update">更新于 {{ lastUpdateTime }}</span>
        </div>
      </div>
    </header>

    <!-- 主容器 -->
    <main class="dashboard-main">
      <!-- 错误提示 -->
      <div v-if="error" class="error-alert">
        <span>{{ error }}</span>
        <button @click="error = null" class="close-btn">×</button>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="spinner"></div>
        <p>正在加载仪表板数据...</p>
      </div>

      <!-- 内容区域 -->
      <div v-else class="dashboard-content">
        <!-- 关键统计指标 -->
        <section class="stats-section">
          <div class="stats-grid">
            <div class="stat-card" v-for="stat in statsCards" :key="stat.id">
              <div class="stat-icon" :style="{ background: stat.gradient }">
                {{ stat.icon }}
              </div>
              <div class="stat-info">
                <div class="stat-label">{{ stat.label }}</div>
                <div class="stat-value">{{ stat.value }}</div>
                <div class="stat-change" :class="stat.trend">
                  {{ stat.change }}
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 图表区域 -->
        <section class="charts-section">
          <div class="charts-grid">
            <!-- 案例趋势图 -->
            <div class="chart-card">
              <h3>案例趋势</h3>
              <EChart :option="casesTrendOption" height="280px" />
            </div>

            <!-- 检测结果分布 -->
            <div class="chart-card">
              <h3>检测结果分布</h3>
              <EChart :option="detectionDistOption" height="280px" />
            </div>

            <!-- 影像模态分布 -->
            <div class="chart-card">
              <h3>影像模态统计</h3>
              <EChart :option="modalityDistOption" height="280px" />
            </div>

            <!-- 处理时间趋势 -->
            <div class="chart-card">
              <h3>处理时间趋势</h3>
              <EChart :option="processingTimeOption" height="280px" />
            </div>
          </div>
        </section>

        <!-- 最近病例 -->
        <section class="recent-cases-section">
          <div class="section-header">
            <h2>最近病例</h2>
            <router-link to="/data" class="view-all-btn">查看全部</router-link>
          </div>

          <div class="cases-table">
            <div class="table-header">
              <div class="col">病例ID</div>
              <div class="col">患者信息</div>
              <div class="col">影像类型</div>
              <div class="col">扫描日期</div>
              <div class="col">检测结果</div>
              <div class="col">状态</div>
              <div class="col">操作</div>
            </div>

            <div v-if="recentCases.length > 0" class="table-body">
              <div v-for="caseItem in recentCases" :key="caseItem.id" class="table-row">
                <div class="col">{{ caseItem.id }}</div>
                <div class="col">
                  <div class="patient-info">
                    <div class="patient-name">{{ caseItem.patient_name || '未命名' }}</div>
                    <div class="patient-id">ID: {{ caseItem.patient_id || '--' }}</div>
                  </div>
                </div>
                <div class="col">{{ caseItem.modality || 'MRI' }}</div>
                <div class="col">{{ formatDate(caseItem.scan_date) }}</div>
                <div class="col">
                  <span :class="['result-badge', caseItem.tumor_detected ? 'positive' : 'negative']">
                    {{ caseItem.tumor_detected ? '检出肿瘤' : '未检出' }}
                  </span>
                </div>
                <div class="col">
                  <span class="status-badge" :class="getStatusClass(caseItem.status)">
                    {{ getStatusText(caseItem.status) }}
                  </span>
                </div>
                <div class="col actions">
                  <button class="action-btn" @click="viewCase(caseItem.id)">查看</button>
                </div>
              </div>
            </div>

            <div v-else class="empty-state">
              暂无病例数据
            </div>
          </div>
        </section>

        <!-- 系统监控 -->
        <section class="system-section">
          <div class="system-grid">
            <!-- 系统状态 -->
            <div class="system-card">
              <h3>系统状态</h3>
              <div class="system-metrics">
                <div class="metric-item">
                  <span class="metric-label">服务器状态</span>
                  <span class="metric-value healthy">运行中</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">API调用</span>
                  <span class="metric-value">{{ systemStatus.apiCalls }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">响应时间</span>
                  <span class="metric-value">{{ systemStatus.avgResponseTime }}ms</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">存储使用</span>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: systemStatus.storageUsage + '%' }"></div>
                  </div>
                  <span class="metric-value">{{ systemStatus.storageUsage }}%</span>
                </div>
              </div>
            </div>

            <!-- 模型信息 -->
            <div class="model-card">
              <h3>模型信息</h3>
              <div class="model-info">
                <div class="info-item">
                  <span class="info-label">模型版本</span>
                  <span class="info-value">{{ modelInfo.version }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">准确率</span>
                  <span class="info-value">{{ (modelInfo.accuracy * 100).toFixed(1) }}%</span>
                </div>
                <div class="info-item">
                  <span class="info-label">平均推理时间</span>
                  <span class="info-value">{{ modelInfo.avgInferenceTime }}ms</span>
                </div>
                <div class="info-item">
                  <span class="info-label">最后更新</span>
                  <span class="info-value">{{ formatDate(modelInfo.lastUpdated) }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import EChart from '@/components/charts/EChart.vue'
import type { EChartsOption } from 'echarts'
import { api } from '@/services/api'

const router = useRouter()

// 数据状态
const loading = ref(false)
const error = ref<string | null>(null)
const lastUpdateTime = ref('--:--:--')

// 统计数据
const dashboardStats = ref({
  totalCases: 0,
  todayCases: 0,
  detectedTumors: 0,
  avgAccuracy: 0.89
})

const recentCases = ref<any[]>([])

const systemStatus = ref({
  apiCalls: 0,
  avgResponseTime: 245,
  storageUsage: 45
})

const modelInfo = ref({
  version: 'YOLO11n',
  accuracy: 0.892,
  avgInferenceTime: 180,
  lastUpdated: new Date().toISOString()
})

// 统计卡片
const statsCards = computed(() => [
  {
    id: 'total',
    label: '总病例数',
    value: dashboardStats.value.totalCases,
    change: '',
    trend: ''
  },
  {
    id: 'today',
    label: '今日新增',
    value: dashboardStats.value.todayCases,
    change: '+12%',
    trend: 'up'
  },
  {
    id: 'detected',
    label: '检出肿瘤',
    value: dashboardStats.value.detectedTumors,
    change: '+8',
    trend: 'up'
  },
  {
    id: 'accuracy',
    label: '平均准确率',
    value: (dashboardStats.value.avgAccuracy * 100).toFixed(1) + '%',
    change: '+2.3%',
    trend: 'up'
  }
])

// ECharts配置
const chartBaseOption = {
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true
  },
  tooltip: {
    trigger: 'axis',
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    borderColor: '#333',
    textStyle: {
      color: '#fff'
    }
  }
}

// 案例趋势图配置
const casesTrendOption = computed<EChartsOption>(() => ({
  ...chartBaseOption,
  xAxis: {
    type: 'category',
    data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' },
    splitLine: { lineStyle: { color: '#333', type: 'dashed' } }
  },
  series: [
    {
      name: '上传病例',
      type: 'line',
      data: [23, 34, 28, 45, 52, 38, 41],
      smooth: true,
      itemStyle: { color: '#667eea' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(102, 126, 234, 0.5)' },
            { offset: 1, color: 'rgba(102, 126, 234, 0.05)' }
          ]
        }
      }
    }
  ]
}))

// 检测结果分布
const detectionDistOption = computed<EChartsOption>(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} ({d}%)'
  },
  legend: {
    orient: 'vertical',
    right: '10%',
    top: 'center',
    textStyle: { color: '#999' }
  },
  series: [
    {
      name: '检测结果',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      data: [
        { value: 245, name: '检出肿瘤', itemStyle: { color: '#f5576c' } },
        { value: 455, name: '未检出', itemStyle: { color: '#43e97b' } }
      ],
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        color: '#999'
      }
    }
  ]
}))

// 影像模态分布
const modalityDistOption = computed<EChartsOption>(() => ({
  ...chartBaseOption,
  xAxis: {
    type: 'category',
    data: ['MRI', 'CT', 'PET', 'X-Ray'],
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' }
  },
  yAxis: {
    type: 'value',
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' },
    splitLine: { lineStyle: { color: '#333', type: 'dashed' } }
  },
  series: [
    {
      name: '数量',
      type: 'bar',
      data: [
        { value: 380, itemStyle: { color: '#667eea' } },
        { value: 220, itemStyle: { color: '#f093fb' } },
        { value: 85, itemStyle: { color: '#4facfe' } },
        { value: 15, itemStyle: { color: '#43e97b' } }
      ],
      barWidth: '50%'
    }
  ]
}))

// 处理时间趋势
const processingTimeOption = computed<EChartsOption>(() => ({
  ...chartBaseOption,
  xAxis: {
    type: 'category',
    data: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00'],
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' }
  },
  yAxis: {
    type: 'value',
    name: '毫秒',
    axisLine: { lineStyle: { color: '#666' } },
    axisLabel: { color: '#999' },
    splitLine: { lineStyle: { color: '#333', type: 'dashed' } }
  },
  series: [
    {
      name: '处理时间',
      type: 'line',
      data: [245, 238, 225, 212, 198, 205],
      smooth: true,
      itemStyle: { color: '#00f2fe' },
      lineStyle: { width: 3 }
    }
  ]
}))

// 方法
const formatDate = (dateString?: string) => {
  if (!dateString) return '--'
  return new Date(dateString).toLocaleDateString('zh-CN')
}

const getStatusClass = (status?: string) => {
  const map: Record<string, string> = {
    'pending': 'pending',
    'processing': 'processing',
    'completed': 'completed',
    'failed': 'failed'
  }
  return map[status || ''] || 'pending'
}

const getStatusText = (status?: string) => {
  const map: Record<string, string> = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return map[status || ''] || '未知'
}

const refreshData = async () => {
  loading.value = true
  error.value = null

  try {
    // 获取仪表板统计
    const stats = await api.getDashboardStats()
    if (stats) {
      dashboardStats.value = {
        totalCases: stats.totalImages || 0,
        todayCases: stats.todayCases || 0,
        detectedTumors: stats.detectedTumors || 0,
        avgAccuracy: stats.modelAccuracy || 0.89
      }
    }

    // 获取最近病例
    const cases = await api.getRecentCases()
    if (cases && Array.isArray(cases)) {
      recentCases.value = cases.slice(0, 10)
    }

    lastUpdateTime.value = new Date().toLocaleTimeString('zh-CN')
  } catch (err: any) {
    error.value = err.message || '加载数据失败'
    console.error('Dashboard error:', err)
  } finally {
    loading.value = false
  }
}

const viewCase = (caseId: number) => {
  router.push(`/results?imageId=${caseId}`)
}

onMounted(() => {
  refreshData()
  // 每5分钟自动刷新
  setInterval(refreshData, 5 * 60 * 1000)
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.dashboard-view {
  width: 100%;
  min-height: 100vh;
  background: transparent;
  padding: 24px;
}

/* 头部 */
.dashboard-header {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(34, 211, 238, 0.04));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 28px 32px;
  margin-bottom: 32px;
  box-shadow: var(--shadow);
  backdrop-filter: blur(8px);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.5px;
}

.header-title .subtitle {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 20px;
  align-items: center;
}

.refresh-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.refresh-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.last-update {
  color: var(--text-muted);
  font-size: 13px;
  font-weight: 500;
}

/* 主容器 */
.dashboard-main {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.error-alert {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #ff6b6b;
  font-weight: 500;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #ff6b6b;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #ff8c8c;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 20px;
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

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

/* 统计卡片 */
.stats-section {
  margin-bottom: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.stat-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s;
  backdrop-filter: blur(8px);
}

.stat-card:hover {
  transform: translateY(-4px);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 13px;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: 800;
  color: var(--text);
  line-height: 1;
  margin-bottom: 8px;
}

.stat-change {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}

.stat-change.up {
  color: #43e97b;
}

.stat-change.down {
  color: #f5576c;
}

/* 图表区域 */
.charts-section {
  margin-bottom: 8px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 20px;
}

.chart-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  backdrop-filter: blur(8px);
  transition: all 0.3s;
}

.chart-card:hover {
  border-color: rgba(255, 255, 255, 0.12);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

/* 最近病例 */
.recent-cases-section {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  backdrop-filter: blur(8px);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.view-all-btn {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: opacity 0.2s;
}

.view-all-btn:hover {
  opacity: 0.8;
}

.cases-table {
  width: 100%;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 1fr 100px 120px 120px 100px 80px;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.table-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 100px 120px 120px 100px 80px;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  align-items: center;
  transition: all 0.2s;
  cursor: pointer;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
}

.col {
  font-size: 14px;
  color: var(--text);
}

.patient-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.patient-name {
  font-weight: 600;
  color: var(--text);
}

.patient-id {
  font-size: 12px;
  color: var(--text-muted);
}

.result-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.result-badge.positive {
  background: rgba(245, 87, 108, 0.15);
  color: #f5576c;
}

.result-badge.negative {
  background: rgba(67, 233, 123, 0.15);
  color: #43e97b;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.status-badge.processing {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.completed {
  background: rgba(34, 211, 238, 0.15);
  color: #06b6d4;
}

.status-badge.failed {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.actions {
  display: flex;
  justify-content: center;
}

.action-btn {
  padding: 6px 14px;
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 12px;
  font-weight: 600;
  transition: all 0.2s;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.empty-state {
  padding: 48px;
  text-align: center;
  color: var(--text-muted);
  font-size: 14px;
}

/* 系统监控 */
.system-section {
  margin-bottom: 8px;
}

.system-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.system-card,
.model-card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
  backdrop-filter: blur(8px);
}

.system-card h3,
.model-card h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.system-metrics,
.model-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.metric-item,
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.metric-item:last-child,
.info-item:last-child {
  border-bottom: none;
}

.metric-label,
.info-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-muted);
}

.metric-value,
.info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.metric-value.healthy {
  color: #43e97b;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
  margin: 0 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  transition: width 0.3s;
}

/* 响应式 */
@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .table-header,
  .table-row {
    grid-template-columns: 60px 1fr 80px 100px 80px 60px;
  }

  .col:nth-child(4) {
    display: none;
  }
}

@media (max-width: 768px) {
  .dashboard-view {
    padding: 12px;
  }

  .dashboard-header {
    padding: 20px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .header-title h1 {
    font-size: 24px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .system-grid {
    grid-template-columns: 1fr;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }

  .table-row {
    padding: 12px;
  }

  .col {
    display: flex;
    justify-content: space-between;
  }

  .col::before {
    content: attr(data-label);
    font-weight: 600;
    color: var(--text-muted);
    font-size: 12px;
  }
}
</style>
