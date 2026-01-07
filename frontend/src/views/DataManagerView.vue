<template>
  <div class="data-manager">
    <!-- 页面头部 -->
    <header class="manager-header">
      <div class="header-content">
        <h1>病例管理</h1>
        <p class="subtitle">医学影像与检测结果数据管理</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" @click="showUploadPanel = !showUploadPanel">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
          {{ showUploadPanel ? '收起上传面板' : '上传新病例' }}
        </button>
      </div>
    </header>

    <!-- 上传面板 -->
    <div v-if="showUploadPanel" class="upload-panel">
      <div class="panel-content">
        <h2>批量上传病例影像</h2>

        <div class="upload-grid">
          <div class="upload-area">
            <input type="file" multiple accept=".dcm,.nii,.nii.gz,.png,.jpg,.jpeg,.tif,.tiff" style="display: none"
              ref="fileInput" @change="onFiles" />
            <div class="upload-zone" @click="fileInput?.click()" :class="{ 'drag-over': dragOver }"
              @dragover.prevent="dragOver = true" @dragleave="dragOver = false" @drop.prevent="handleDrop">
              <svg class="upload-icon" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="1.5">
                <path d="M3 15v4c0 1.1.9 2 2 2h14a2 2 0 0 0 2-2v-4M17 9l-5-5-5 5M12 4v12" />
              </svg>
              <h3>选择或拖拽文件</h3>
              <p>点击此处选择文件，或将文件拖拽到此区域</p>
              <p class="formats">支持格式：DCM, NIfTI (.nii, .nii.gz), PNG, JPG, TIFF</p>
            </div>

            <!-- 已选文件 -->
            <div v-if="files.length > 0" class="files-preview">
              <div class="files-count">已选择 {{ files.length }} 个文件</div>
              <div class="file-list">
                <div v-for="(file, idx) in files" :key="idx" class="file-item">
                  <span>{{ file.name }}</span>
                  <button class="remove-btn" @click.stop="removeFile(idx)">×</button>
                </div>
              </div>
            </div>
          </div>

          <div class="upload-metadata">
            <h3>患者信息</h3>
            <div class="form-group">
              <label>患者ID <span class="required">*</span></label>
              <input v-model="meta.patientId" type="text" placeholder="例如：P001" class="form-input" required />
            </div>
            <div class="form-group">
              <label>患者姓名 <span class="required">*</span></label>
              <input v-model="meta.patientName" type="text" placeholder="输入患者姓名" class="form-input" required />
            </div>
            <div class="form-group">
              <label>影像类型 <span class="required">*</span></label>
              <select v-model="meta.scanType" class="form-select" required>
                <option value="">请选择影像类型</option>
                <option value="MRI">MRI（磁共振）</option>
                <option value="CT">CT（计算机断层）</option>
                <option value="PET">PET（正电子发射）</option>
                <option value="X-Ray">X-Ray（X光）</option>
                <option value="Ultrasound">Ultrasound（超声）</option>
              </select>
            </div>
            <div class="form-group">
              <label>扫描日期 <span class="required">*</span></label>
              <input v-model="meta.scanDate" type="date" class="form-input" required />
            </div>
            <div class="form-group">
              <label>备注</label>
              <textarea v-model="meta.notes" placeholder="输入其他信息（可选）" class="form-textarea" rows="3"></textarea>
            </div>

            <div class="upload-actions">
              <button class="btn btn-primary" :disabled="uploading || files.length === 0" @click="upload">
                <svg v-if="!uploading" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                  stroke-width="2">
                  <polyline points="16 16 12 12 8 16" />
                  <line x1="12" y1="12" x2="12" y2="21" />
                  <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3" />
                </svg>
                <span v-if="uploading" class="spinner"></span>
                {{ uploading ? '上传中...' : '开始上传' }}
              </button>
              <button class="btn btn-outline" @click="resetUpload" :disabled="uploading">取消</button>
            </div>

            <div v-if="uploading" class="progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <div class="progress-text">{{ uploadProgress }}%</div>
            </div>
          </div>
        </div>

        <div v-if="error" class="alert alert-error">
          <span>{{ error }}</span>
          <button @click="error = ''">&times;</button>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <main class="manager-main">
      <!-- 搜索和过滤 -->
      <div class="filters-section">
        <div class="search-box">
          <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="2">
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input v-model="filters.query" type="text" placeholder="搜索患者ID、名称或病例号..." class="search-input"
            @keyup.enter="loadDatasets" />
        </div>
        <div class="filter-group">
          <input v-model="filters.date" type="date" class="filter-input" />
          <select v-model="filters.status" class="filter-input">
            <option value="">全部状态</option>
            <option value="new">新建</option>
            <option value="processing">处理中</option>
            <option value="completed">已完成</option>
          </select>
          <button class="btn btn-sm" @click="loadDatasets">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.35-4.35" />
            </svg>
            搜索
          </button>
        </div>
      </div>

      <!-- 数据网格 -->
      <div class="data-grid">
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="paged.length > 0" class="cases-table">
          <div class="table-header">
            <div class="col-id">病例ID</div>
            <div class="col-patient">患者信息</div>
            <div class="col-type">影像类型</div>
            <div class="col-date">扫描日期</div>
            <div class="col-status">状态</div>
            <div class="col-actions">操作</div>
          </div>

          <div v-for="d in paged" :key="d.id" class="table-row" @click="select(d)">
            <div class="col-id">{{ d.id }}</div>
            <div class="col-patient">
              <div class="patient-name">{{ d.patient_name || '未命名' }}</div>
              <div class="patient-id">ID: {{ d.patient_id || '--' }}</div>
            </div>
            <div class="col-type">{{ d.modality || '--' }}</div>
            <div class="col-date">{{ formatDate(d.scan_date) }}</div>
            <div class="col-status">
              <span class="status-badge" :class="getStatusClass(d.status)">
                {{ getStatusLabel(d.status) }}
              </span>
            </div>
            <div class="col-actions">
              <button class="action-btn analyze-btn" @click.stop="goAnalyze(d)">分析</button>
              <button class="action-btn delete-btn" @click.stop="remove(d.id)">删除</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <svg class="empty-icon" width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            stroke-width="1.5">
            <path
              d="M9 2a1 1 0 0 0-1 1v2H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2V3a1 1 0 1 0-2 0v2H10V3a1 1 0 0 0-1-1z" />
            <path d="M4 9h16" />
          </svg>
          <div class="empty-title">暂无病例数据</div>
          <div class="empty-desc">点击上方"上传新病例"按钮添加医学影像数据</div>
          <button class="btn btn-primary" @click="showUploadPanel = true" style="margin-top: 16px;">
            立即上传
          </button>
        </div>

        <!-- 分页 -->
        <div v-if="totalPages > 1" class="pagination">
          <button class="pagination-btn" :disabled="page === 1" @click="prev">
            上一页
          </button>
          <div class="pagination-info">
            第 {{ page }} / {{ totalPages }} 页 （共 {{ datasets.length }} 条）
          </div>
          <button class="pagination-btn" :disabled="page === totalPages" @click="next">
            下一页
          </button>
        </div>
      </div>

      <!-- 详情面板 -->
      <div v-if="selected" class="detail-panel">
        <h2>病例详情</h2>
        <div class="detail-content">
          <div class="viewer-section">
            <div class="image-preview">
              <img v-if="getImageUrl(selected)" :src="getImageUrl(selected)" alt="图像预览" @error="handleImageError" />
              <div v-else class="no-preview">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
                <p>无预览图像</p>
              </div>
            </div>
          </div>

          <div class="info-section">
            <div class="info-group">
              <div class="info-label">病例ID</div>
              <div class="info-value">{{ selected.id }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">患者ID</div>
              <div class="info-value">{{ selected.patient_id || '--' }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">患者姓名</div>
              <div class="info-value">{{ selected.patient_name || '--' }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">影像模态</div>
              <div class="info-value">{{ selected.modality || '--' }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">扫描日期</div>
              <div class="info-value">{{ formatDate(selected.scan_date) }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">文件名</div>
              <div class="info-value">{{ selected.name }}</div>
            </div>
            <div class="info-group">
              <div class="info-label">状态</div>
              <div class="info-value">
                <span class="status-badge" :class="getStatusClass(selected.status)">
                  {{ getStatusLabel(selected.status) }}
                </span>
              </div>
            </div>

            <div class="actions-footer">
              <button class="btn btn-primary" @click="goAnalyze(selected)">开始分析</button>
              <button class="btn btn-outline" @click="selected = null">关闭</button>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 成功提示 -->
    <transition name="fade">
      <div v-if="toast" class="toast-message">
        [OK] {{ toast }}
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { api } from '@/services/api'
import { useRouter } from 'vue-router'

interface Dataset {
  id: string | number
  name: string
  patient_id?: string
  patient_name?: string
  modality?: string
  scan_date?: string
  preview_url?: string
  file_url?: string
  status?: string
}

const files = ref<File[]>([])
const fileInput = ref<HTMLInputElement>()
const uploading = ref(false)
const uploadProgress = ref(0)
const error = ref('')
const toast = ref('')
const showUploadPanel = ref(false)
const dragOver = ref(false)
const loading = ref(false)
const meta = ref({ patientId: '', patientName: '', scanType: '', scanDate: '', notes: '' })
const filters = ref({ query: '', date: '', status: '' })
const datasets = ref<Dataset[]>([])
const selected = ref<Dataset | null>(null)
const page = ref(1)
const pageSize = ref(10)
const router = useRouter()

const paged = computed(() => {
  const start = (page.value - 1) * pageSize.value
  const end = start + pageSize.value
  return datasets.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(datasets.value.length / pageSize.value)
})

const onFiles = (e: Event) => {
  const t = e.target as HTMLInputElement
  files.value = t.files ? Array.from(t.files) : []
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  dragOver.value = false
  const droppedFiles = e.dataTransfer?.files
  if (droppedFiles) {
    files.value = Array.from(droppedFiles)
  }
}

const removeFile = (idx: number) => {
  files.value.splice(idx, 1)
}

const resetUpload = () => {
  files.value = []
  meta.value = { patientId: '', patientName: '', scanType: '', scanDate: '', notes: '' }
  error.value = ''
  showUploadPanel.value = false
}

const upload = async () => {
  if (files.value.length === 0) {
    error.value = '请先选择文件'
    return
  }

  // 验证必填字段
  if (!meta.value.patientId || !meta.value.patientName || !meta.value.scanType || !meta.value.scanDate) {
    error.value = '请填写所有必填字段（患者ID、姓名、影像类型、扫描日期）'
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  error.value = ''

  try {
    const total = files.value.length
    let completed = 0

    console.log('[开始上传]', total, '个文件')

    // 逐个上传文件
    for (const file of files.value) {
      console.log('上传文件:', file.name)
      const result = await api.uploadDataset([file], meta.value)
      console.log('上传成功:', result)
      completed++
      uploadProgress.value = Math.round((completed / total) * 100)
    }

    console.log('[所有文件上传完成] 准备刷新列表')
    toast.value = `成功上传 ${total} 个文件`

    // 刷新数据列表
    await loadDatasets()
    console.log('[数据列表已刷新] 当前数据条数:', datasets.value.length)

    resetUpload()
    setTimeout(() => { toast.value = '' }, 3000)
  } catch (e: any) {
    console.error('[上传失败]', e)
    error.value = e?.message || '上传失败'
  } finally {
    uploading.value = false
  }
}

const remove = async (id: string | number) => {
  if (!confirm('确认删除该病例？删除后不可恢复')) return
  try {
    await api.deleteDataset(id)
    toast.value = '已删除'
    await loadDatasets()
    if (selected.value?.id === id) selected.value = null
    setTimeout(() => { toast.value = '' }, 3000)
  } catch (e: any) {
    error.value = e?.message || '删除失败'
  }
}

const loadDatasets = async () => {
  loading.value = true
  console.log('[开始加载数据列表]')
  try {
    const result = await api.listDatasets(filters.value)
    console.log('[获取到数据]', result.length, '条')
    console.log('数据详情:', result)
    datasets.value = result
    page.value = 1
  } catch (e: any) {
    console.error('[加载数据失败]', e)
    error.value = e?.message || '加载数据失败'
  } finally {
    loading.value = false
  }
}

const select = (d: Dataset) => {
  selected.value = d
}

const goAnalyze = (d: Dataset) => {
  console.log('[跳转到处理与分割页面] imageId:', d.id)
  router.push({ path: '/workbench', query: { imageId: String(d.id) } })
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '--'
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

const getStatusClass = (status?: string) => {
  const map: Record<string, string> = {
    'new': 'new',
    'processing': 'processing',
    'completed': 'completed'
  }
  return map[status || ''] || 'new'
}

const getStatusLabel = (status?: string) => {
  const map: Record<string, string> = {
    'new': '新建',
    'processing': '处理中',
    'completed': '已完成'
  }
  return map[status || ''] || '未知'
}

const prev = () => { if (page.value > 1) page.value-- }
const next = () => { if (page.value < totalPages.value) page.value++ }

const ROOT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const getImageUrl = (dataset: Dataset) => {
  const url = dataset.preview_url || dataset.file_url
  if (!url) return ''
  return url.startsWith('http') ? url : `${ROOT_BASE_URL}${url}`
}

const handleImageError = (e: Event) => {
  console.error('图像加载失败:', e)
  const img = e.target as HTMLImageElement
  img.style.display = 'none'
}

onMounted(() => {
  loadDatasets()
})
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.data-manager {
  width: 100%;
  min-height: 100vh;
  background: transparent;
  padding: 24px;
}

/* 页面头部 */
.manager-header {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(34, 211, 238, 0.04));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.header-content h1 {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 8px 0;
  color: var(--text);
}

.header-content .subtitle {
  font-size: 14px;
  color: var(--text-muted);
  margin: 0;
}

.header-actions {
  flex-shrink: 0;
}

/* 上传面板 */
.upload-panel {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
  margin-bottom: 32px;
  backdrop-filter: blur(8px);
}

.panel-content h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 24px 0;
  color: var(--text);
}

.upload-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  margin-bottom: 24px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.upload-zone {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-lg);
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--primary);
  background: linear-gradient(145deg, rgba(37, 99, 235, 0.08), rgba(37, 99, 235, 0.04));
}

.upload-icon {
  margin-bottom: 16px;
  color: var(--primary);
  opacity: 0.6;
}

.upload-zone h3 {
  font-size: 16px;
  margin: 0 0 8px 0;
  color: var(--text);
}

.upload-zone p {
  font-size: 13px;
  color: var(--text-muted);
  margin: 0 0 4px 0;
}

.upload-zone .formats {
  font-size: 12px;
}

.files-preview {
  background: linear-gradient(145deg, rgba(34, 211, 238, 0.1), rgba(34, 211, 238, 0.05));
  border: 1px solid rgba(34, 211, 238, 0.3);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.files-count {
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-sm);
  font-size: 13px;
  color: var(--text-muted);
}

.remove-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: var(--text-muted);
}

.remove-btn:hover {
  color: #ef4444;
}

.upload-metadata {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.upload-metadata h3 {
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.form-group {
  margin-bottom: 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
  text-transform: uppercase;
}

.form-group label .required {
  color: #ef4444;
  margin-left: 2px;
}

.form-input,
.form-select,
.form-textarea {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  font-size: 14px;
  font-family: inherit;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.08);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.upload-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.progress {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary), var(--accent));
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
}

/* 按钮 */
.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  border: none;
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.3s;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn svg {
  flex-shrink: 0;
}

.btn-primary {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(37, 99, 235, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

.btn-outline {
  background: transparent;
  color: var(--text);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-outline:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
}

.btn-sm {
  padding: 8px 16px;
  font-size: 13px;
}

/* 主要内容区 */
.manager-main {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 过滤器 */
.filters-section {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 16px;
}

.search-box {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 42px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.08);
}

.filter-group {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

.filter-input {
  padding: 10px 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  font-size: 13px;
}

.filter-input:focus {
  outline: none;
  border-color: var(--primary);
}

/* 数据网格 */
.data-grid {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 80px 1fr 120px 120px 100px 120px;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.05);
  font-weight: 600;
  font-size: 13px;
  color: var(--text-muted);
  text-transform: uppercase;
}

.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 120px 120px 100px 120px;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  align-items: center;
  cursor: pointer;
  transition: background 0.2s;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.col-id {
  font-weight: 600;
  color: var(--primary);
}

.col-patient {
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

.col-status {
  text-align: center;
}

.status-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.new {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.processing {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(34, 211, 238, 0.15);
  color: #06b6d4;
}

.col-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.analyze-btn {
  background: linear-gradient(135deg, var(--primary), var(--primary-2));
  color: white;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.2);
}

.analyze-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.delete-btn {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.2);
}

.empty-state {
  padding: 80px 40px;
  text-align: center;
  color: var(--text-muted);
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.02), rgba(255, 255, 255, 0.01));
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

.empty-icon {
  margin: 0 auto 24px;
  opacity: 0.3;
  color: var(--text-muted);
}

.empty-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

/* 加载状态 */
.loading-state {
  padding: 80px 40px;
  text-align: center;
  color: var(--text-muted);
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  margin: 0;
  font-size: 14px;
}

.empty-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text);
  margin-bottom: 8px;
}

.empty-desc {
  font-size: 14px;
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
}

.pagination-btn {
  padding: 8px 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.1);
}

.pagination-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  font-size: 13px;
  color: var(--text-muted);
}

/* 详情面板 */
.detail-panel {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 32px;
  margin-top: 16px;
}

.detail-panel h2 {
  margin: 0 0 24px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text);
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.viewer-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.image-preview {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
  overflow: hidden;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.no-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text-muted);
}

.no-preview svg {
  opacity: 0.3;
}

.no-preview p {
  margin: 0;
  font-size: 14px;
}

.viewer-controls {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-group label {
  min-width: 60px;
  font-weight: 600;
  font-size: 13px;
  color: var(--text);
}

.control-group input[type="range"] {
  flex: 1;
  accent-color: var(--primary);
}

.control-group span {
  min-width: 40px;
  text-align: right;
  color: var(--text-muted);
  font-size: 13px;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-group {
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.info-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.info-value {
  font-size: 14px;
  color: var(--text);
  font-weight: 500;
  word-break: break-all;
}

.actions-footer {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.actions-footer .btn {
  flex: 1;
}

/* 提示 */
.toast-message {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: rgba(34, 211, 238, 0.15);
  color: #06b6d4;
  border: 1px solid rgba(34, 211, 238, 0.3);
  padding: 16px 24px;
  border-radius: var(--radius-md);
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(34, 211, 238, 0.2);
  animation: slideIn 0.3s ease;
  backdrop-filter: blur(8px);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes slideIn {
  from {
    transform: translateX(400px);
    opacity: 0;
  }

  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.alert {
  padding: 16px;
  border-radius: var(--radius-md);
  margin-bottom: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.alert button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 20px;
}

/* 响应式 */
@media (max-width: 1200px) {
  .upload-grid {
    grid-template-columns: 1fr;
  }

  .detail-content {
    grid-template-columns: 1fr;
  }

  .table-header,
  .table-row {
    grid-template-columns: 60px 1fr 100px 80px 80px;
  }

  .col-actions {
    flex-direction: column;
  }
}

@media (max-width: 768px) {
  .data-manager {
    padding: 12px;
  }

  .manager-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    padding: 20px;
  }

  .header-content h1 {
    font-size: 24px;
  }

  .filters-section {
    flex-direction: column;
  }

  .filter-group {
    width: 100%;
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
  }

  .col-id::before {
    content: "ID: ";
    font-weight: 600;
  }

  .col-patient::before {
    content: "患者: ";
    font-weight: 600;
  }

  .col-type::before {
    content: "类型: ";
    font-weight: 600;
  }

  .col-date::before {
    content: "日期: ";
    font-weight: 600;
  }

  .col-status::before {
    content: "状态: ";
    font-weight: 600;
  }

  .action-btn {
    width: 100%;
  }

  .col-actions {
    flex-direction: row;
    width: 100%;
  }

  .action-btn {
    flex: 1;
  }
}
</style>
