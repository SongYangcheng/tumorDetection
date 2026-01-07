<template>
    <div class="video-detection">
        <header class="video-header">
            <div class="header-content">
                <h1>🎥 视频影像检测</h1>
                <p class="subtitle">支持视频上传检测和实时摄像头流检测</p>
            </div>
        </header>

        <div class="detection-tabs">
            <button class="tab-btn" :class="{ active: activeTab === 'upload' }" @click="activeTab = 'upload'">
                视频上传检测
            </button>
            <button class="tab-btn" :class="{ active: activeTab === 'stream' }" @click="activeTab = 'stream'">
                实时流检测
            </button>
        </div>

        <!-- 视频上传检测 -->
        <div v-if="activeTab === 'upload'" class="upload-section">
            <div class="upload-card">
                <h2>视频文件上传</h2>

                <input type="file" ref="videoInput" accept="video/*" style="display: none" @change="onVideoSelect" />

                <div v-if="!selectedVideo" class="upload-zone" @click="$refs.videoInput?.click()">
                    <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                        stroke-width="1.5">
                        <path d="M23 7l-7 5 7 5V7z" />
                        <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
                    </svg>
                    <h3>选择视频文件</h3>
                    <p>支持格式：MP4, AVI, MOV, MKV, FLV, WMV</p>
                    <p class="hint">点击此处选择视频文件</p>
                </div>

                <div v-else class="video-preview">
                    <video ref="videoPreview" controls :src="videoPreviewUrl" class="preview-player"></video>
                    <div class="video-info">
                        <p><strong>文件名：</strong>{{ selectedVideo.name }}</p>
                        <p><strong>大小：</strong>{{ formatFileSize(selectedVideo.size) }}</p>
                    </div>
                    <button class="btn btn-outline" @click="clearVideo">重新选择</button>
                </div>

                <div v-if="selectedVideo" class="upload-form">
                    <h3>患者信息</h3>
                    <div class="form-row">
                        <div class="form-group">
                            <label>患者ID <span class="required">*</span></label>
                            <input v-model="videoMeta.patientId" type="text" placeholder="例如：P001" class="form-input"
                                required />
                        </div>
                        <div class="form-group">
                            <label>患者姓名 <span class="required">*</span></label>
                            <input v-model="videoMeta.patientName" type="text" placeholder="输入患者姓名" class="form-input"
                                required />
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>置信度阈值</label>
                            <input v-model.number="videoMeta.confThreshold" type="range" min="0.1" max="0.9" step="0.05"
                                class="form-range" />
                            <span class="range-value">{{ videoMeta.confThreshold.toFixed(2) }}</span>
                        </div>
                        <div class="form-group">
                            <label>帧间隔（提取间隔）</label>
                            <input v-model.number="videoMeta.frameInterval" type="number" min="1" max="120"
                                class="form-input" />
                            <span class="hint-text">每隔N帧提取一帧分析</span>
                        </div>
                    </div>

                    <button class="btn btn-primary btn-large"
                        :disabled="uploading || !videoMeta.patientId || !videoMeta.patientName" @click="uploadVideo">
                        <span v-if="uploading" class="spinner"></span>
                        {{ uploading ? '分析中...' : '开始分析' }}
                    </button>

                    <div v-if="uploading" class="progress-section">
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
                        </div>
                        <p class="progress-text">{{ uploadProgress }}% - {{ uploadStatus }}</p>
                    </div>
                </div>

                <!-- 检测结果 -->
                <div v-if="detectionResult" class="detection-result">
                    <h3>检测结果</h3>
                    <div class="result-stats">
                        <div class="stat-card">
                            <div class="stat-icon"></div>
                            <div class="stat-value">{{ detectionResult.video_info?.frame_count || 0 }}</div>
                            <div class="stat-label">总帧数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"></div>
                            <div class="stat-value">{{ detectionResult.summary?.total_frames_analyzed || 0 }}</div>
                            <div class="stat-label">分析帧数</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"></div>
                            <div class="stat-value">{{ detectionResult.summary?.frames_with_tumor || 0 }}</div>
                            <div class="stat-label">检测到肿瘤帧</div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon"></div>
                            <div class="stat-value">{{ (detectionResult.summary?.tumor_detection_rate * 100).toFixed(1)
                                }}%</div>
                            <div class="stat-label">检出率</div>
                        </div>
                    </div>

                    <div v-if="detectionResult.sample_frames" class="sample-frames">
                        <h4>样本帧检测</h4>
                        <div class="frames-grid">
                            <div v-for="frame in detectionResult.sample_frames" :key="frame.frame" class="frame-card">
                                <div class="frame-number">帧 #{{ frame.frame }}</div>
                                <div class="frame-result" :class="{ detected: frame.has_tumor }">
                                    {{ frame.has_tumor ? '✓ 检测到' : '✗ 未检测到' }}
                                </div>
                                <div v-if="frame.has_tumor" class="frame-conf">
                                    置信度: {{ frame.avg_confidence.toFixed(3) }}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 实时流检测 -->
        <div v-if="activeTab === 'stream'" class="stream-section">
            <div class="stream-card">
                <h2>实时摄像头检测</h2>

                <div class="stream-container">
                    <div class="video-container">
                        <video ref="videoStream" autoplay playsinline class="stream-video"></video>
                        <canvas ref="detectionCanvas" class="detection-overlay"></canvas>
                    </div>

                    <div class="stream-controls">
                        <button v-if="!streaming" class="btn btn-primary" @click="startStream">
                            启动摄像头
                        </button>
                        <button v-else class="btn btn-danger" @click="stopStream">
                            停止检测
                        </button>

                        <div class="stream-settings">
                            <label>
                                置信度阈值:
                                <input v-model.number="streamConfThreshold" type="range" min="0.1" max="0.9"
                                    step="0.05" />
                                <span>{{ streamConfThreshold.toFixed(2) }}</span>
                            </label>
                        </div>
                    </div>

                    <div v-if="streaming" class="stream-stats">
                        <div class="stat-item">
                            <span class="stat-label">FPS:</span>
                            <span class="stat-value">{{ currentFps }}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">检测到肿瘤:</span>
                            <span class="stat-value" :class="{ detected: streamDetection?.has_tumor }">
                                {{ streamDetection?.has_tumor ? '是' : '否' }}
                            </span>
                        </div>
                        <div class="stat-item" v-if="streamDetection?.has_tumor">
                            <span class="stat-label">置信度:</span>
                            <span class="stat-value">{{ streamDetection?.avg_confidence?.toFixed(3) }}</span>
                        </div>
                    </div>
                </div>

                <div v-if="error" class="alert alert-error">
                    {{ error }}
                </div>
            </div>
        </div>

        <!-- 错误提示 -->
        <div v-if="error" class="toast-error">
            {{ error }}
        </div>

        <!-- 成功提示 -->
        <div v-if="toast" class="toast-success">
            ✓ {{ toast }}
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { api } from '@/services/api'

const activeTab = ref<'upload' | 'stream'>('upload')

// 视频上传相关
const videoInput = ref<HTMLInputElement>()
const selectedVideo = ref<File | null>(null)
const videoPreviewUrl = ref('')
const videoPreview = ref<HTMLVideoElement>()
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const detectionResult = ref<any>(null)

const videoMeta = ref({
    patientId: '',
    patientName: '',
    confThreshold: 0.25,
    frameInterval: 30
})

// 实时流相关
const videoStream = ref<HTMLVideoElement>()
const detectionCanvas = ref<HTMLCanvasElement>()
const streaming = ref(false)
const streamConfThreshold = ref(0.25)
const streamDetection = ref<any>(null)
const currentFps = ref(0)
const mediaStream = ref<MediaStream | null>(null)
const detectionInterval = ref<number | null>(null)

// 通用
const error = ref('')
const toast = ref('')

// 文件大小格式化
const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}

// 选择视频
const onVideoSelect = (e: Event) => {
    const files = (e.target as HTMLInputElement).files
    if (files && files.length > 0) {
        selectedVideo.value = files[0]
        videoPreviewUrl.value = URL.createObjectURL(files[0])
    }
}

// 清除视频
const clearVideo = () => {
    selectedVideo.value = null
    videoPreviewUrl.value = ''
    detectionResult.value = null
    if (videoInput.value) {
        videoInput.value.value = ''
    }
}

// 上传视频
const uploadVideo = async () => {
    if (!selectedVideo.value || !videoMeta.value.patientId || !videoMeta.value.patientName) {
        error.value = '请填写所有必填信息'
        return
    }

    uploading.value = true
    uploadProgress.value = 0
    uploadStatus.value = '正在上传视频...'
    error.value = ''

    try {
        const result = await api.uploadVideo(selectedVideo.value, videoMeta.value, (progress) => {
            uploadProgress.value = Math.round(progress)
            if (progress < 100) {
                uploadStatus.value = '正在上传视频...'
            } else {
                uploadStatus.value = '正在分析视频帧...'
            }
        })

        detectionResult.value = result
        toast.value = '视频分析完成'
        setTimeout(() => { toast.value = '' }, 3000)
    } catch (e: any) {
        error.value = e?.message || '上传失败'
    } finally {
        uploading.value = false
    }
}

// 启动实时流
const startStream = async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: 640, height: 480 }
        })

        if (videoStream.value) {
            videoStream.value.srcObject = stream
            mediaStream.value = stream

            // 等待视频加载
            await new Promise((resolve) => {
                videoStream.value!.onloadedmetadata = resolve
            })

            // 设置canvas尺寸
            if (detectionCanvas.value) {
                detectionCanvas.value.width = videoStream.value.videoWidth
                detectionCanvas.value.height = videoStream.value.videoHeight
            }

            streaming.value = true
            startDetectionLoop()
        }
    } catch (e: any) {
        error.value = '无法访问摄像头: ' + e.message
    }
}

// 停止实时流
const stopStream = () => {
    if (mediaStream.value) {
        mediaStream.value.getTracks().forEach(track => track.stop())
        mediaStream.value = null
    }

    if (detectionInterval.value) {
        clearInterval(detectionInterval.value)
        detectionInterval.value = null
    }

    streaming.value = false
    streamDetection.value = null
}

// 检测循环
const startDetectionLoop = () => {
    let lastTime = Date.now()
    let frameCount = 0

    detectionInterval.value = window.setInterval(async () => {
        if (!videoStream.value || !detectionCanvas.value) return

        // 获取当前帧
        const canvas = document.createElement('canvas')
        canvas.width = videoStream.value.videoWidth
        canvas.height = videoStream.value.videoHeight
        const ctx = canvas.getContext('2d')

        if (ctx) {
            ctx.drawImage(videoStream.value, 0, 0)
            const frameDataUrl = canvas.toDataURL('image/jpeg', 0.8)

            try {
                const result = await api.detectStreamFrame(frameDataUrl, streamConfThreshold.value)
                streamDetection.value = result.detection

                // 绘制检测框
                const overlayCtx = detectionCanvas.value!.getContext('2d')
                if (overlayCtx) {
                    overlayCtx.clearRect(0, 0, detectionCanvas.value!.width, detectionCanvas.value!.height)

                    if (result.detection.has_tumor) {
                        overlayCtx.strokeStyle = '#ff0000'
                        overlayCtx.lineWidth = 2
                        overlayCtx.font = '14px Arial'
                        overlayCtx.fillStyle = '#ff0000'

                        result.detection.boxes.forEach((box: number[], idx: number) => {
                            const [x1, y1, x2, y2] = box
                            overlayCtx.strokeRect(x1, y1, x2 - x1, y2 - y1)
                            const conf = result.detection.confidences[idx]
                            overlayCtx.fillText(`${conf.toFixed(2)}`, x1, y1 - 5)
                        })
                    }
                }

                // 计算FPS
                frameCount++
                const now = Date.now()
                if (now - lastTime >= 1000) {
                    currentFps.value = frameCount
                    frameCount = 0
                    lastTime = now
                }
            } catch (e: any) {
                console.error('检测失败:', e)
            }
        }
    }, 200) // 每200ms检测一次 (~5 FPS)
}

onUnmounted(() => {
    stopStream()
    if (videoPreviewUrl.value) {
        URL.revokeObjectURL(videoPreviewUrl.value)
    }
})
</script>

<style scoped>
.video-detection {
    min-height: 100vh;
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: var(--text);
    padding: 20px;
}

.video-header {
    text-align: center;
    margin-bottom: 30px;
}

.video-header h1 {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 10px 0;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    color: var(--text-muted);
    font-size: 14px;
}

.detection-tabs {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-bottom: 30px;
}

.tab-btn {
    padding: 12px 24px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    color: var(--text);
    cursor: pointer;
    transition: all 0.3s;
}

.tab-btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.tab-btn.active {
    background: var(--primary);
    border-color: var(--primary);
    color: white;
}

.upload-section,
.stream-section {
    max-width: 1200px;
    margin: 0 auto;
}

.upload-card,
.stream-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 30px;
}

.upload-card h2,
.stream-card h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
}

.upload-zone {
    border: 2px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 60px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
}

.upload-zone:hover {
    border-color: var(--primary);
    background: rgba(37, 99, 235, 0.05);
}

.upload-zone svg {
    color: var(--primary);
    margin-bottom: 20px;
}

.upload-zone h3 {
    margin: 0 0 10px 0;
    font-size: 18px;
}

.upload-zone p {
    color: var(--text-muted);
    margin: 5px 0;
}

.hint {
    font-size: 12px;
    color: var(--primary);
}

.video-preview {
    margin: 20px 0;
}

.preview-player {
    width: 100%;
    max-height: 400px;
    border-radius: var(--radius-md);
    background: #000;
}

.video-info {
    margin: 15px 0;
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
}

.video-info p {
    margin: 5px 0;
}

.upload-form {
    margin-top: 30px;
}

.upload-form h3 {
    margin: 0 0 15px 0;
    font-size: 16px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
    margin-bottom: 15px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-group label {
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
}

.required {
    color: #ef4444;
}

.form-input,
.form-range {
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    background: rgba(255, 255, 255, 0.05);
    color: var(--text);
    font-size: 14px;
}

.form-input:focus {
    outline: none;
    border-color: var(--primary);
}

.range-value {
    font-size: 14px;
    color: var(--primary);
    font-weight: 600;
}

.hint-text {
    font-size: 12px;
    color: var(--text-muted);
}

.btn-large {
    width: 100%;
    padding: 15px;
    font-size: 16px;
    margin-top: 20px;
}

.progress-section {
    margin-top: 20px;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 10px;
}

.progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--primary), var(--accent));
    transition: width 0.3s;
}

.progress-text {
    text-align: center;
    font-size: 14px;
    color: var(--primary);
}

.detection-result {
    margin-top: 30px;
    padding-top: 30px;
    border-top: 1px solid var(--border);
}

.result-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    margin: 20px 0;
}

.stat-card {
    text-align: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
}

.stat-icon {
    font-size: 32px;
    margin-bottom: 10px;
}

.stat-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 5px;
}

.stat-label {
    font-size: 12px;
    color: var(--text-muted);
}

.sample-frames {
    margin-top: 30px;
}

.frames-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 10px;
    margin-top: 15px;
}

.frame-card {
    padding: 15px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
    text-align: center;
}

.frame-number {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 5px;
}

.frame-result {
    font-size: 14px;
    font-weight: 600;
    padding: 5px;
    border-radius: 4px;
    margin-bottom: 5px;
}

.frame-result.detected {
    color: #10b981;
    background: rgba(16, 185, 129, 0.1);
}

.frame-conf {
    font-size: 12px;
    color: var(--text-muted);
}

/* 实时流样式 */
.stream-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.video-container {
    position: relative;
    width: 100%;
    max-width: 640px;
    margin: 0 auto;
    border-radius: var(--radius-lg);
    overflow: hidden;
    background: #000;
}

.stream-video {
    width: 100%;
    display: block;
}

.detection-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
}

.stream-controls {
    display: flex;
    flex-direction: column;
    gap: 15px;
    align-items: center;
}

.stream-settings {
    display: flex;
    gap: 15px;
    align-items: center;
}

.stream-settings label {
    display: flex;
    gap: 10px;
    align-items: center;
}

.stream-stats {
    display: flex;
    gap: 20px;
    justify-content: center;
    padding: 20px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: var(--radius-md);
}

.stat-item {
    display: flex;
    gap: 8px;
    align-items: center;
}

.stat-label {
    font-size: 14px;
    color: var(--text-muted);
}

.stat-value {
    font-size: 16px;
    font-weight: 600;
    color: var(--primary);
}

.stat-value.detected {
    color: #ef4444;
}

.btn-danger {
    background: #ef4444;
    border-color: #ef4444;
}

.btn-danger:hover {
    background: #dc2626;
}

.toast-error {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    background: #ef4444;
    color: white;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 1000;
}

.toast-success {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px 20px;
    background: #10b981;
    color: white;
    border-radius: var(--radius-md);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    z-index: 1000;
}

@media (max-width: 768px) {
    .result-stats {
        grid-template-columns: repeat(2, 1fr);
    }

    .frames-grid {
        grid-template-columns: repeat(3, 1fr);
    }

    .form-row {
        grid-template-columns: 1fr;
    }
}
</style>
