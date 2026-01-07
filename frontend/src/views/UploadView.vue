<template>
    <div class="upload-container">
        <!-- 页面头部 -->
        <header class="upload-header">
            <div class="header-content">
                <h1>医学影像上传</h1>
                <p class="subtitle">上传脑部医学影像进行AI辅助诊断分析</p>
            </div>
            <div class="header-stats">
                <div class="stat">
                    <div class="stat-label">支持格式</div>
                    <div class="stat-value">6+</div>
                </div>
                <div class="divider"></div>
                <div class="stat">
                    <div class="stat-label">最大文件</div>
                    <div class="stat-value">500MB</div>
                </div>
                <div class="divider"></div>
                <div class="stat">
                    <div class="stat-label">处理速度</div>
                    <div class="stat-value">&lt;1s</div>
                </div>
            </div>
        </header>

        <!-- 主内容区 -->
        <main class="upload-main">
            <!-- 错误提示 -->
            <div v-if="error" class="alert alert-error">
                <div class="alert-icon">!</div>
                <div class="alert-content">
                    <div class="alert-title">上传失败</div>
                    <div class="alert-message">{{ error }}</div>
                </div>
                <button class="alert-close" @click="error = ''">&times;</button>
            </div>

            <!-- 成功提示 -->
            <div v-if="success" class="alert alert-success">
                <div class="alert-icon">✓</div>
                <div class="alert-content">
                    <div class="alert-title">上传成功</div>
                    <div class="alert-message">图像已上传，即将进行分析...</div>
                </div>
            </div>

            <!-- 内容网格 -->
            <div class="upload-grid">
                <!-- 左侧：上传区 -->
                <div class="upload-zone-container">
                    <div class="upload-zone" :class="{ 'drag-over': dragOver }" @drop="handleDrop"
                        @dragover.prevent="dragOver = true" @dragleave="dragOver = false">
                        <input ref="fileInput" type="file" accept="image/*,.dcm,.nii,.nii.gz" style="display: none"
                            @change="handleFileChange" />

                        <div class="upload-content" @click="fileInput?.click()">
                            <div class="upload-icon">📤</div>
                            <h3 class="upload-title">上传医学影像</h3>
                            <p class="upload-instruction">点击选择或拖拽文件到此处</p>
                            <p class="upload-formats">支持：PNG, JPG, DICOM, NIfTI等</p>
                        </div>
                    </div>

                    <!-- 文件信息 -->
                    <div v-if="selectedFile" class="file-selected">
                        <div class="file-item">
                            <div class="file-icon">📄</div>
                            <div class="file-details">
                                <div class="file-name">{{ selectedFile.name }}</div>
                                <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                            </div>
                            <button class="file-remove" @click="clearFile">×</button>
                        </div>
                    </div>

                    <!-- 进度条 -->
                    <div v-if="uploading" class="progress-section">
                        <div class="progress-label">
                            <span>{{ uploadStatus }}</span>
                            <span class="progress-percent">{{ progress }}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: progress + '%' }"></div>
                        </div>
                    </div>
                </div>

                <!-- 右侧：患者信息表单 -->
                <div class="form-container">
                    <h2>患者信息</h2>
                    <form class="patient-form" @submit.prevent="handleSubmit">
                        <div class="form-group">
                            <label class="form-label">患者ID *</label>
                            <input v-model="formData.patientId" type="text" class="form-input" placeholder="P001"
                                required />
                            <span class="form-hint">唯一患者标识符</span>
                        </div>

                        <div class="form-group">
                            <label class="form-label">患者姓名 *</label>
                            <input v-model="formData.patientName" type="text" class="form-input" placeholder="张三"
                                required />
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">年龄 *</label>
                                <input v-model.number="formData.age" type="number" class="form-input" placeholder="45"
                                    min="0" max="150" required />
                            </div>

                            <div class="form-group">
                                <label class="form-label">性别 *</label>
                                <select v-model="formData.gender" class="form-select" required>
                                    <option value="">请选择</option>
                                    <option value="M">男性</option>
                                    <option value="F">女性</option>
                                    <option value="O">其他</option>
                                </select>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label class="form-label">扫描日期 *</label>
                                <input v-model="formData.scanDate" type="date" class="form-input" required />
                            </div>

                            <div class="form-group">
                                <label class="form-label">影像模态 *</label>
                                <select v-model="formData.modality" class="form-select" required>
                                    <option value="">请选择</option>
                                    <option value="MRI">MRI</option>
                                    <option value="CT">CT</option>
                                    <option value="X-Ray">X-Ray</option>
                                    <option value="PET">PET</option>
                                    <option value="SPECT">SPECT</option>
                                </select>
                            </div>
                        </div>

                        <!-- 提交按钮 -->
                        <div class="form-actions">
                            <button type="submit" class="btn btn-primary" :disabled="!selectedFile || uploading">
                                {{ uploading ? '上传中...' : '上传并分析' }}
                            </button>
                            <button type="reset" class="btn btn-outline" :disabled="uploading" @click="resetForm">
                                重置
                            </button>
                        </div>
                    </form>
                </div>
            </div>

            <!-- 最近上传 -->
            <section v-if="recentUploads.length > 0" class="recent-uploads">
                <h2>最近上传</h2>
                <div class="uploads-grid">
                    <div v-for="upload in recentUploads" :key="upload.id" class="upload-card">
                        <div class="upload-card-header">
                            <div class="upload-card-info">
                                <div class="upload-card-name">{{ upload.name }}</div>
                                <div class="upload-card-date">{{ formatDate(upload.date) }}</div>
                            </div>
                            <span class="status-badge" :class="upload.status">
                                {{ upload.status === 'completed' ? '已完成' : '处理中' }}
                            </span>
                        </div>
                    </div>
                </div>
            </section>
        </main>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()
const fileInput = ref<HTMLInputElement>()
const selectedFile = ref<File | null>(null)
const dragOver = ref(false)
const uploading = ref(false)
const progress = ref(0)
const uploadStatus = ref('')
const error = ref('')
const success = ref(false)
const recentUploads = ref<any[]>([])

const formData = ref({
    patientId: '',
    patientName: '',
    age: 45,
    gender: '',
    scanDate: new Date().toISOString().split('T')[0],
    modality: ''
})

const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
}

const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('zh-CN')
}

const handleFileChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0]
    if (file) {
        selectedFile.value = file
    }
}

const handleDrop = (event: DragEvent) => {
    dragOver.value = false
    const files = event.dataTransfer?.files
    if (files?.[0]) {
        selectedFile.value = files[0]
    }
}

const clearFile = () => {
    selectedFile.value = null
    if (fileInput.value) {
        fileInput.value.value = ''
    }
}

const resetForm = () => {
    formData.value = {
        patientId: '',
        patientName: '',
        age: 45,
        gender: '',
        scanDate: new Date().toISOString().split('T')[0],
        modality: ''
    }
    clearFile()
    error.value = ''
}

const handleSubmit = async () => {
    if (!selectedFile.value) {
        error.value = '请先选择文件'
        return
    }

    uploading.value = true
    error.value = ''
    success.value = false
    progress.value = 0
    uploadStatus.value = '初始化...'

    try {
        const progressInterval = setInterval(() => {
            progress.value = Math.min(progress.value + Math.random() * 30, 90)
            updateUploadStatus()
        }, 300)

        uploadStatus.value = '上传中'
        const result = await api.uploadImage(selectedFile.value)
        clearInterval(progressInterval)
        progress.value = 100
        uploadStatus.value = '完成'

        localStorage.setItem('currentImageId', result.image_id?.toString() || '')

        success.value = true

        setTimeout(() => {
            router.push(`/results?imageId=${result.image_id}`)
        }, 2000)
    } catch (err) {
        error.value = err instanceof Error ? err.message : '上传失败，请重试'
    } finally {
        uploading.value = false
        progress.value = 0
    }
}

const updateUploadStatus = () => {
    const statuses = ['准备文件...', '上传中...', '处理中...', '即将完成...']
    const index = Math.floor((progress.value / 100) * (statuses.length - 1))
    uploadStatus.value = statuses[index]
}

const loadRecentUploads = async () => {
    try {
        const uploads = await api.listMedicalImages()
        recentUploads.value = uploads.images?.slice(0, 5) || []
    } catch (err) {
        console.error('加载最近上传失败:', err)
    }
}

onMounted(() => {
    loadRecentUploads()
})
</script>

<style scoped>
* {
    box-sizing: border-box;
}

.upload-container {
    width: 100%;
    min-height: 100vh;
    background: transparent;
    padding: 24px;
}

/* 页面头部 */
.upload-header {
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(34, 211, 238, 0.04));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 32px;
    margin-bottom: 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 40px;
}

.header-content h1 {
    font-size: 36px;
    font-weight: 800;
    margin: 0 0 8px 0;
    color: var(--text);
}

.header-content .subtitle {
    font-size: 15px;
    color: var(--text-muted);
    margin: 0;
}

.header-stats {
    display: flex;
    align-items: center;
    gap: 24px;
}

.stat {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary);
}

.divider {
    width: 1px;
    height: 40px;
    background: rgba(255, 255, 255, 0.1);
}

/* 主容器 */
.upload-main {
    display: flex;
    flex-direction: column;
    gap: 32px;
}

/* 提示消息 */
.alert {
    display: flex;
    gap: 16px;
    padding: 16px 20px;
    border-radius: var(--radius-lg);
    border: 1px solid;
    animation: slideDown 0.3s ease;
}

.alert-error {
    background: rgba(239, 68, 68, 0.1);
    border-color: rgba(239, 68, 68, 0.3);
    color: #dc2626;
}

.alert-success {
    background: rgba(34, 211, 238, 0.1);
    border-color: rgba(34, 211, 238, 0.3);
    color: #0891b2;
}

.alert-icon {
    flex-shrink: 0;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
}

.alert-content {
    flex: 1;
}

.alert-title {
    font-weight: 600;
    margin-bottom: 4px;
}

.alert-message {
    font-size: 14px;
    opacity: 0.9;
}

.alert-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    opacity: 0.6;
    transition: opacity 0.2s;
}

.alert-close:hover {
    opacity: 1;
}

@keyframes slideDown {
    from {
        transform: translateY(-10px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

/* 上传网格 */
.upload-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    margin-bottom: 32px;
}

/* 上传区容器 */
.upload-zone-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.upload-zone {
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: var(--radius-lg);
    padding: 48px 32px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
    backdrop-filter: blur(8px);
}

.upload-zone:hover {
    border-color: rgba(37, 99, 235, 0.4);
    background: linear-gradient(145deg, rgba(37, 99, 235, 0.08), rgba(37, 99, 235, 0.04));
}

.upload-zone.drag-over {
    border-color: var(--primary);
    background: linear-gradient(145deg, rgba(37, 99, 235, 0.12), rgba(37, 99, 235, 0.06));
}

.upload-content {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
}

.upload-icon {
    font-size: 56px;
    line-height: 1;
}

.upload-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

.upload-instruction {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0;
}

.upload-formats {
    font-size: 12px;
    color: var(--text-muted);
    margin: 0;
}

/* 文件已选择 */
.file-selected {
    background: linear-gradient(145deg, rgba(34, 211, 238, 0.1), rgba(34, 211, 238, 0.05));
    border: 1px solid rgba(34, 211, 238, 0.3);
    border-radius: var(--radius-lg);
    padding: 16px;
}

.file-item {
    display: flex;
    gap: 12px;
    align-items: center;
}

.file-icon {
    font-size: 32px;
    flex-shrink: 0;
}

.file-details {
    flex: 1;
    min-width: 0;
}

.file-name {
    font-weight: 600;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.file-size {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}

.file-remove {
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: var(--text-muted);
    transition: color 0.2s;
    padding: 0;
}

.file-remove:hover {
    color: #ef4444;
}

/* 进度条 */
.progress-section {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 16px;
}

.progress-label {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 500;
}

.progress-percent {
    color: var(--primary);
    font-weight: 700;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    transition: width 0.3s ease;
    box-shadow: 0 0 8px rgba(37, 99, 235, 0.6);
}

/* 表单容器 */
.form-container {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 32px;
    backdrop-filter: blur(8px);
    height: fit-content;
    position: sticky;
    top: 24px;
}

.form-container h2 {
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 24px 0;
    color: var(--text);
}

.patient-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.form-input,
.form-select {
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.05);
    color: var(--text);
    font-family: inherit;
    font-size: 14px;
    transition: all 0.2s;
}

.form-input:focus,
.form-select:focus {
    outline: none;
    border-color: var(--primary);
    background: rgba(37, 99, 235, 0.08);
    box-shadow: 0 0 12px rgba(37, 99, 235, 0.2);
}

.form-hint {
    font-size: 12px;
    color: var(--text-muted);
    margin-top: 4px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}

/* 按钮 */
.btn {
    padding: 12px 24px;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 14px;
    transition: all 0.3s;
    border: none;
    cursor: pointer;
    text-transform: none;
}

.btn-primary {
    background: linear-gradient(135deg, var(--primary), var(--primary-2));
    color: white;
    box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
    flex: 1;
}

.btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.4);
}

.btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.btn-outline {
    background: transparent;
    color: var(--text);
    border: 1px solid rgba(255, 255, 255, 0.2);
    flex: 1;
}

.btn-outline:hover:not(:disabled) {
    border-color: rgba(255, 255, 255, 0.4);
    background: rgba(255, 255, 255, 0.05);
}

/* 最近上传 */
.recent-uploads {
    margin-top: 40px;
}

.recent-uploads h2 {
    font-size: 20px;
    font-weight: 700;
    margin: 0 0 20px 0;
    color: var(--text);
}

.uploads-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.upload-card {
    background: linear-gradient(145deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.02));
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 16px;
    transition: all 0.3s;
    cursor: pointer;
}

.upload-card:hover {
    border-color: rgba(255, 255, 255, 0.15);
    transform: translateY(-2px);
}

.upload-card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
}

.upload-card-info {
    flex: 1;
    min-width: 0;
}

.upload-card-name {
    font-weight: 600;
    color: var(--text);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 4px;
}

.upload-card-date {
    font-size: 12px;
    color: var(--text-muted);
}

.status-badge {
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    white-space: nowrap;
    flex-shrink: 0;
}

.status-badge.completed {
    background: rgba(34, 211, 238, 0.15);
    color: #06b6d4;
}

.status-badge.pending {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
}

/* 响应式 */
@media (max-width: 1200px) {
    .upload-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 20px;
    }

    .header-stats {
        width: 100%;
    }

    .upload-grid {
        grid-template-columns: 1fr;
    }

    .form-container {
        position: static;
        height: auto;
    }
}

@media (max-width: 768px) {
    .upload-container {
        padding: 12px;
    }

    .upload-header {
        padding: 20px;
    }

    .header-content h1 {
        font-size: 24px;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
    }

    .upload-zone {
        padding: 32px 16px;
    }

    .uploads-grid {
        grid-template-columns: 1fr;
    }
}
</style>
