<template>
    <div class="report-container">
        <!-- 报告标题 -->
        <div class="report-header">
            <div class="header-left">
                <h1 class="report-title">脑肿瘤检测分析报告</h1>
                <p class="report-subtitle">基于{{ reportData?.last_model_used === 'unet' ? 'UNet' : 'YOLO' }}深度学习模型的智能诊断
                </p>
            </div>
            <div class="header-right">
                <button class="btn-export" @click="exportPDF">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                        <polyline points="7 10 12 15 17 10" />
                        <line x1="12" y1="15" x2="12" y2="3" />
                    </svg>
                    导出PDF
                </button>
                <button class="btn-print" @click="printReport">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="6 9 6 2 18 2 18 9" />
                        <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2" />
                        <rect x="6" y="14" width="12" height="8" />
                    </svg>
                    打印报告
                </button>
            </div>
        </div>

        <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在加载报告数据...</p>
        </div>

        <div v-else-if="error" class="error-container">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <h3>{{ error.includes('未提供影像ID') ? '请选择医学影像' : '加载失败' }}</h3>
            <p>{{ error }}</p>
            <div class="error-actions">
                <button v-if="error.includes('未提供影像ID')" class="btn-primary" @click="goToDataManager">
                    前往数据管理
                </button>
                <button v-else class="btn-retry" @click="loadReport">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="23 4 23 10 17 10" />
                        <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                    </svg>
                    重新加载
                </button>
            </div>
        </div>

        <div v-else-if="reportData" class="report-content">
            <!-- 患者信息 -->
            <section class="report-section patient-info">
                <div class="section-header">
                    <h2 class="section-title">患者信息</h2>
                </div>
                <div class="info-grid-2col">
                    <div class="info-field">
                        <span class="field-label">患者ID</span>
                        <span class="field-value">{{ reportData.patient_id || 'N/A' }}</span>
                    </div>
                    <div class="info-field">
                        <span class="field-label">患者姓名</span>
                        <span class="field-value">{{ reportData.patient_name || 'N/A' }}</span>
                    </div>
                    <div class="info-field">
                        <span class="field-label">影像类型</span>
                        <span class="field-value">{{ reportData.image_type || 'N/A' }}</span>
                    </div>
                    <div class="info-field">
                        <span class="field-label">扫描日期</span>
                        <span class="field-value">{{ formatDate(reportData.scan_date) }}</span>
                    </div>
                    <div class="info-field">
                        <span class="field-label">上传时间</span>
                        <span class="field-value">{{ formatDate(reportData.uploaded_at) }}</span>
                    </div>
                    <div class="info-field">
                        <span class="field-label">检测时间</span>
                        <span class="field-value">{{ formatDate(reportData.detection_time) }}</span>
                    </div>
                </div>
            </section>

            <!-- 检测结果总览 -->
            <section class="report-section detection-overview">
                <div class="section-header">
                    <h2 class="section-title">检测结果总览</h2>
                </div>

                <div class="overview-cards">
                    <div class="overview-card" :class="{ 'has-tumor': reportData.has_tumor }">
                        <div class="card-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <circle cx="12" cy="12" r="10" />
                                <path d="M12 6v6l4 2" />
                            </svg>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">检测状态</h3>
                            <p class="card-value">{{ reportData.has_tumor ? '发现肿瘤' : '未发现肿瘤' }}</p>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <path
                                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                            </svg>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">肿瘤实例数</h3>
                            <p class="card-value">{{ reportData.num_instances }}</p>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                                <rect x="7" y="7" width="10" height="10" />
                            </svg>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">面积占比</h3>
                            <p class="card-value">{{ reportData.tumor_ratio?.toFixed(2) }}%</p>
                        </div>
                    </div>

                    <div class="overview-card">
                        <div class="card-icon">
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="2">
                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                            </svg>
                        </div>
                        <div class="card-content">
                            <h3 class="card-title">平均置信度</h3>
                            <p class="card-value">{{ (reportData.avg_confidence * 100).toFixed(1) }}%</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 影像展示 -->
            <section class="report-section image-display">
                <div class="section-header">
                    <h2 class="section-title">影像对比</h2>
                </div>

                <div class="image-comparison">
                    <div class="image-box">
                        <h4 class="image-label">原始影像</h4>
                        <img v-if="reportData.file_url || reportData.preview_url"
                            :src="getImageUrl(reportData.preview_url || reportData.file_url)" alt="原始影像"
                            @error="handleImageError" />
                        <div v-else class="image-placeholder">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="1.5">
                                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                                <circle cx="8.5" cy="8.5" r="1.5" />
                                <polyline points="21 15 16 10 5 21" />
                            </svg>
                            <p>原始影像不可用</p>
                        </div>
                    </div>
                    <div class="image-box">
                        <h4 class="image-label">分割结果</h4>
                        <img v-if="reportData.overlay_url" :src="getImageUrl(reportData.overlay_url)" alt="分割结果"
                            @error="handleImageError" />
                        <div v-else class="image-placeholder">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                                stroke-width="1.5">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                            </svg>
                            <p>{{ reportData.has_tumor ? '请先在处理与分割页面进行分割' : '未检测到肿瘤' }}</p>
                            <p style="font-size: 12px; margin-top: 8px; color: #999;">
                                调试: overlay_url = {{ reportData.overlay_url || 'null' }}
                            </p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- 肿瘤详细信息 -->
            <section v-if="reportData.has_tumor" class="report-section tumor-details">
                <div class="section-header">
                    <h2 class="section-title">肿瘤详细信息</h2>
                </div>

                <div class="detail-grid">
                    <div class="detail-item">
                        <span class="detail-label">肿瘤位置</span>
                        <span class="detail-value">{{ reportData.location || '未知' }}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">肿瘤像素数</span>
                        <span class="detail-value">{{ reportData.tumor_pixels?.toLocaleString() || '0' }} px</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">总像素数</span>
                        <span class="detail-value">{{ reportData.total_pixels?.toLocaleString() || 'N/A' }} px</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">肿瘤面积占比</span>
                        <span class="detail-value">{{ reportData.tumor_ratio?.toFixed(2) || '0.00' }}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">检测实例数</span>
                        <span class="detail-value">{{ reportData.num_instances || 0 }} 个</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">平均置信度</span>
                        <span class="detail-value">{{ (reportData.avg_confidence * 100)?.toFixed(1) || '0.0' }}%</span>
                    </div>
                    <div class="detail-item" v-if="reportData.centroid_x && reportData.centroid_y">
                        <span class="detail-label">中心坐标</span>
                        <span class="detail-value">({{ reportData.centroid_x?.toFixed(1) }}, {{
                            reportData.centroid_y?.toFixed(1) }})</span>
                    </div>
                    <div class="detail-item" v-if="reportData.bbox_x1">
                        <span class="detail-label">边界框</span>
                        <span class="detail-value">
                            ({{ reportData.bbox_x1?.toFixed(0) }}, {{ reportData.bbox_y1?.toFixed(0) }}) -
                            ({{ reportData.bbox_x2?.toFixed(0) }}, {{ reportData.bbox_y2?.toFixed(0) }})
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">模型版本</span>
                        <span class="detail-value">{{
                            reportData?.last_model_used === 'unet'
                                ? (reportData.unet_model_version || 'UNet (ResNeXt50)')
                                : (reportData.yolo_model_version || 'YOLO11')
                        }}</span>
                    </div>
                </div>

                <!-- 实例级别详细信息 -->
                <div v-if="reportData.instances && reportData.instances.length > 0" class="instances-section">
                    <h3 class="subsection-title">检测实例详情</h3>
                    <div class="instances-grid">
                        <div v-for="(instance, idx) in reportData.instances" :key="idx" class="instance-card">
                            <div class="instance-header">
                                <span class="instance-id">实例 {{ instance.id || (idx + 1) }}</span>
                                <span class="instance-confidence">{{ (instance.confidence * 100)?.toFixed(1) }}%</span>
                            </div>
                            <div class="instance-details">
                                <div class="instance-field">
                                    <span class="field-label">面积</span>
                                    <span class="field-value">{{ instance.area?.toLocaleString() || 'N/A' }} px</span>
                                </div>
                                <div class="instance-field" v-if="instance.bbox">
                                    <span class="field-label">位置</span>
                                    <span class="field-value">
                                        ({{ instance.bbox[0]?.toFixed(0) }}, {{ instance.bbox[1]?.toFixed(0) }})
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>


                <!-- 肿瘤实例列表 -->
                <div v-if="reportData.instances && reportData.instances.length > 0" class="instances-table">
                    <h3 class="table-title">肿瘤实例详情</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>实例ID</th>
                                <th>置信度</th>
                                <th>面积 (px²)</th>
                                <th>边界框坐标</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(instance, idx) in reportData.instances" :key="instance.id || idx">
                                <td>{{ instance.id || (idx + 1) }}</td>
                                <td>
                                    <span class="confidence-badge">{{ ((instance.confidence || 0) * 100).toFixed(1)
                                        }}%</span>
                                </td>
                                <td>{{ (instance.area || 0).toLocaleString() }}</td>
                                <td class="bbox-coord">
                                    ({{ reportData.bbox_x1?.toFixed(0) }}, {{ reportData.bbox_y1?.toFixed(0) }}) -
                                    ({{ reportData.bbox_x2?.toFixed(0) }}, {{ reportData.bbox_y2?.toFixed(0) }})
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <!-- 风险评估 -->
            <section class="report-section risk-assessment">
                <div class="section-header">
                    <h2 class="section-title">风险评估</h2>
                </div>

                <div class="risk-cards">
                    <div class="risk-card" :class="`risk-${reportData.risk_level}`">
                        <h3 class="risk-title">风险等级</h3>
                        <p class="risk-value">{{ getRiskLabel(reportData.risk_level) }}</p>
                        <div class="risk-bar">
                            <div class="risk-fill" :style="{ width: getRiskWidth(reportData.risk_level) }"></div>
                        </div>
                        <p class="risk-desc">{{ getRiskDescription(reportData.risk_level) }}</p>
                    </div>

                    <div class="risk-card accessibility">
                        <h3 class="risk-title">手术可达性</h3>
                        <p class="risk-value">{{ getAccessibilityLabel(reportData.surgical_accessibility) }}</p>
                        <div class="accessibility-indicator" :class="reportData.surgical_accessibility">
                            <div class="indicator-dot"></div>
                        </div>
                        <p class="risk-desc">{{ getAccessibilityDescription(reportData.surgical_accessibility) }}</p>
                    </div>
                </div>
            </section>

            <!-- 诊断报告 -->
            <section v-if="reportData.diagnostic_report" class="report-section diagnostic-report">
                <div class="section-header">
                    <div class="section-icon" style="background: #F3E8FF;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#A855F7" stroke-width="2">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                            <polyline points="14 2 14 8 20 8" />
                            <line x1="16" y1="13" x2="8" y2="13" />
                            <line x1="16" y1="17" x2="8" y2="17" />
                            <polyline points="10 9 9 9 8 9" />
                        </svg>
                    </div>
                    <h2 class="section-title">诊断建议</h2>
                </div>

                <div class="diagnostic-content">
                    <div class="diagnostic-item">
                        <h4>检测结果</h4>
                        <p>{{ reportData.diagnostic_report.has_tumor ? '检测到肿瘤组织' : '未检测到明显肿瘤组织' }}</p>
                    </div>
                    <div class="diagnostic-item" v-if="reportData.has_tumor">
                        <h4>肿瘤特征</h4>
                        <p>
                            检测到 <strong>{{ reportData.diagnostic_report.num_instances }}</strong> 个肿瘤实例，
                            占据影像面积的 <strong>{{ reportData.diagnostic_report.tumor_ratio?.toFixed(2) }}%</strong>，
                            平均置信度为 <strong>{{ (reportData.diagnostic_report.avg_confidence * 100).toFixed(1)
                                }}%</strong>。
                        </p>
                    </div>
                    <div class="diagnostic-item">
                        <h4>风险评估</h4>
                        <p>
                            根据肿瘤面积和位置分析，风险等级评定为 <strong>{{ getRiskLabel(reportData.diagnostic_report.risk_level)
                                }}</strong>，
                            手术可达性评估为 <strong>{{
                                getAccessibilityLabel(reportData.diagnostic_report.surgical_accessibility) }}</strong>。
                        </p>
                    </div>
                    <div class="diagnostic-item recommendation">
                        <h4>医疗建议</h4>
                        <p>{{ reportData.diagnostic_report.recommendation }}</p>
                        <p class="disclaimer">
                            <strong>免责声明：</strong>本报告由AI辅助诊断系统生成，仅供医学参考，不能替代专业医师的临床判断。
                            请结合患者临床症状和其他检查结果进行综合诊断。
                        </p>
                    </div>
                </div>
            </section>

            <!-- 报告签名 -->
            <section class="report-footer">
                <div class="footer-line"></div>
                <div class="footer-content">
                    <div class="footer-item">
                        <span class="footer-label">生成时间：</span>
                        <span class="footer-value">{{ formatFullDate(new Date()) }}</span>
                    </div>
                    <div class="footer-item">
                        <span class="footer-label">系统版本：</span>
                        <span class="footer-value">脑肿瘤检测系统 v1.0</span>
                    </div>
                    <div class="footer-item">
                        <span class="footer-label">模型：</span>
                        <span class="footer-value">{{ reportData.last_model_used === 'yolo' ? 'YOLOv11 分割' : 'UNet 分割'
                        }}</span>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '@/services/api'

const ROOT_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const error = ref('')
const reportData = ref<any>(null)

onMounted(() => {
    loadReport()
})

const loadReport = async () => {
    loading.value = true
    error.value = ''

    try {
        const imageId = route.query.imageId as string
        console.log('AnalysisReportView 加载报告，imageId:', imageId)

        if (!imageId) {
            throw new Error('未提供影像ID。请从处理与分割页面跳转。')
        }

        // 获取医学影像信息
        console.log('正在获取医学影像信息...')
        const imageInfo = await api.getMedicalImage(imageId)
        console.log('医学影像信息加载成功:', imageInfo)

        // 解析检测结果（如果已保存在数据库中）
        let detectionData: any = {}
        if (imageInfo.detection_result) {
            try {
                const parsed = JSON.parse(imageInfo.detection_result)
                detectionData = parsed.segmentation || {}
                console.log('解析数据库中的检测结果:', detectionData)
            } catch (e) {
                console.warn('解析detection_result失败:', e)
            }
        }

        // 合并数据：优先使用最后使用的模型结果
        const lastModel = imageInfo.last_model_used || 'yolo'
        const useYolo = lastModel === 'yolo'

        const mask_url = useYolo ? imageInfo.yolo_mask_path : imageInfo.unet_mask_path
        const overlay_url = useYolo ? imageInfo.yolo_mask_overlay_path : imageInfo.unet_mask_overlay_path

        console.log('调试信息 - 模型结果:')
        console.log('  last_model_used:', lastModel)
        console.log('  使用YOLO结果:', useYolo)
        console.log('  overlay_url:', overlay_url)

        reportData.value = {
            ...imageInfo,
            // 根据最后使用的模型选择数据
            has_tumor: useYolo ? imageInfo.yolo_has_tumor : imageInfo.unet_has_tumor,
            num_instances: useYolo ? imageInfo.yolo_num_instances : imageInfo.unet_num_instances,
            tumor_ratio: useYolo ? imageInfo.yolo_tumor_ratio : imageInfo.unet_tumor_ratio,
            avg_confidence: useYolo ? imageInfo.yolo_avg_confidence : imageInfo.unet_avg_confidence,
            tumor_pixels: useYolo ? imageInfo.yolo_tumor_pixels : imageInfo.unet_tumor_pixels,
            total_pixels: useYolo ? imageInfo.yolo_total_pixels : imageInfo.unet_total_pixels,
            risk_level: useYolo
                ? (imageInfo.yolo_risk_level || detectionData.metrics?.risk_level || 'low')
                : (imageInfo.unet_risk_level || detectionData.metrics?.risk_level || 'low'),
            surgical_accessibility: useYolo
                ? (imageInfo.yolo_surgical_accessibility || detectionData.metrics?.surgical_accessibility || 'moderate')
                : (imageInfo.unet_surgical_accessibility || detectionData.metrics?.surgical_accessibility || 'moderate'),
            location: useYolo
                ? (imageInfo.yolo_location_description || detectionData.metrics?.location || '未知')
                : (imageInfo.unet_location_description || detectionData.metrics?.location || '未知'),
            instances: (() => {
                try {
                    if (useYolo) {
                        return imageInfo.yolo_instances ? JSON.parse(imageInfo.yolo_instances) : []
                    } else {
                        return imageInfo.unet_instances ? JSON.parse(imageInfo.unet_instances) : []
                    }
                } catch (e) {
                    console.warn('解析instances失败:', e)
                    return []
                }
            })(),
            // 图像URL
            mask_url: mask_url,
            overlay_url: overlay_url,
            // 边界框信息 - 根据模型选择
            bbox_x1: useYolo ? imageInfo.yolo_tumor_bbox_x1 : imageInfo.unet_tumor_bbox_x1,
            bbox_y1: useYolo ? imageInfo.yolo_tumor_bbox_y1 : imageInfo.unet_tumor_bbox_y1,
            bbox_x2: useYolo ? imageInfo.yolo_tumor_bbox_x2 : imageInfo.unet_tumor_bbox_x2,
            bbox_y2: useYolo ? imageInfo.yolo_tumor_bbox_y2 : imageInfo.unet_tumor_bbox_y2,
            // 中心点 - 根据模型选择
            centroid_x: useYolo ? imageInfo.yolo_tumor_centroid_x : imageInfo.unet_tumor_centroid_x,
            centroid_y: useYolo ? imageInfo.yolo_tumor_centroid_y : imageInfo.unet_tumor_centroid_y
        }
        console.log('报告数据合并完成:', reportData.value)
        console.log('最终overlay_url:', reportData.value.overlay_url)

    } catch (e: any) {
        error.value = e?.message || '加载报告失败'
        console.error('加载报告错误:', e)
    } finally {
        loading.value = false
    }
}

const getImageUrl = (url: string) => {
    if (!url) return ''
    return url.startsWith('http') ? url : `${ROOT_BASE_URL}${url}`
}

const handleImageError = (event: Event) => {
    const target = event.target as HTMLImageElement
    console.error('图片加载失败:', target.src)
    // 不设置默认图，让占位符显示
}

const formatDate = (dateStr: string | undefined) => {
    if (!dateStr) return 'N/A'
    const date = new Date(dateStr)
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    })
}

const formatFullDate = (date: Date) => {
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    })
}

const getRiskLabel = (level: string) => {
    const labels: Record<string, string> = {
        low: '低风险',
        medium: '中风险',
        high: '高风险'
    }
    return labels[level] || level
}

const getRiskWidth = (level: string) => {
    const widths: Record<string, string> = {
        low: '33%',
        medium: '66%',
        high: '100%'
    }
    return widths[level] || '0%'
}

const getRiskDescription = (level: string) => {
    const descriptions: Record<string, string> = {
        low: '肿瘤面积较小，位置相对安全，建议定期复查监测',
        medium: '肿瘤面积中等或位于敏感区域，建议尽快就医评估',
        high: '肿瘤面积较大或位于高风险区域，建议立即就医进行专业评估'
    }
    return descriptions[level] || ''
}

const getAccessibilityLabel = (accessibility: string) => {
    const labels: Record<string, string> = {
        easy: '易接近',
        moderate: '中等难度',
        difficult: '困难'
    }
    return labels[accessibility] || accessibility
}

const getAccessibilityDescription = (accessibility: string) => {
    const descriptions: Record<string, string> = {
        easy: '肿瘤位于易于接近的外围区域，手术风险相对较低',
        moderate: '肿瘤位置中等，需要谨慎评估手术方案',
        difficult: '肿瘤位于深部或功能区，手术难度较高，需专业团队评估'
    }
    return descriptions[accessibility] || ''
}

const exportPDF = () => {
    window.print()
}

const printReport = () => {
    window.print()
}

const goToDataManager = () => {
    console.log('跳转到数据管理页面')
    router.push('/data')
}
</script>

<style scoped>
.report-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
    background: var(--background);
    min-height: 100vh;
}

/* 报告头部 */
.report-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 32px;
    padding-bottom: 24px;
    border-bottom: 2px solid var(--border-color);
}

.header-left {
    flex: 1;
}

.report-title {
    font-size: 32px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 8px 0;
}

.report-subtitle {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0;
}

.header-right {
    display: flex;
    gap: 12px;
}

.btn-export,
.btn-print {
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-export {
    background: linear-gradient(135deg, var(--primary), var(--primary-2));
    color: white;
}

.btn-export:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.3);
}

.btn-print {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border-color);
}

.btn-print:hover {
    background: var(--border-color);
}

/* 加载和错误状态 */
.loading-container,
.error-container {
    text-align: center;
    padding: 80px 20px;
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

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error-container svg {
    margin-bottom: 16px;
    color: #EF4444;
}

.error-container h3 {
    font-size: 20px;
    color: var(--text);
    margin: 0 0 8px 0;
}

.error-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 16px;
}

.btn-retry,
.btn-primary {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 24px;
    border: none;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-retry {
    background: var(--primary);
    color: white;
}

.btn-retry:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}

.btn-primary {
    background: linear-gradient(135deg, #10B981 0%, #059669 100%);
    color: white;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* 报告内容 */
.report-content {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

/* 报告区块 */
.report-section {
    background: var(--card-background);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    border: 1px solid var(--border-color);
}

.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}

.section-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.section-title {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

/* 患者信息 */
.info-grid-2col {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
}

.info-field {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding: 12px;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.field-label {
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
}

.field-value {
    font-size: 15px;
    color: var(--text);
    font-weight: 600;
}

/* 检测总览卡片 */
.overview-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
}

.overview-card {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 20px;
    background: var(--surface);
    border-radius: 12px;
    border: 2px solid var(--border-color);
    transition: all 0.2s;
}

.overview-card:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.1);
}

.overview-card.has-tumor {
    border-color: #EF4444;
    background: rgba(239, 68, 68, 0.05);
}

.card-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    background: var(--background);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--primary);
    flex-shrink: 0;
}

.overview-card.has-tumor .card-icon {
    color: #EF4444;
}

.card-content {
    flex: 1;
}

.card-title {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0 0 6px 0;
}

.card-value {
    font-size: 20px;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

/* 影像对比 */
.image-comparison {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.image-box {
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.image-label {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin: 0;
    text-align: center;
}

.image-box img {
    width: 100%;
    height: auto;
    border-radius: 12px;
    border: 2px solid var(--border-color);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-placeholder {
    width: 100%;
    min-height: 300px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 12px;
    background: var(--surface);
    border: 2px dashed var(--border-color);
    border-radius: 12px;
    color: var(--text-muted);
}

.image-placeholder svg {
    opacity: 0.4;
}

.image-placeholder p {
    margin: 0;
    font-size: 14px;
}

/* 肿瘤详情 */
.detail-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin-bottom: 24px;
}

.detail-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 16px;
    background: var(--surface);
    border-radius: 8px;
    border: 1px solid var(--border-color);
}

.detail-label {
    font-size: 13px;
    color: var(--text-muted);
    font-weight: 500;
}

.detail-value {
    font-size: 14px;
    color: var(--text);
    font-weight: 600;
}

/* 实例表格 */
.instances-table {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
}

.table-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 16px 0;
}

.instances-table table {
    width: 100%;
    border-collapse: collapse;
}

.instances-table th {
    background: var(--surface);
    padding: 12px;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
    color: var(--text);
    border-bottom: 2px solid var(--border-color);
}

.instances-table td {
    padding: 12px;
    font-size: 13px;
    color: var(--text);
    border-bottom: 1px solid var(--border-color);
}

.bbox-coord {
    font-family: monospace;
    font-size: 12px;
}

.confidence-badge {
    display: inline-block;
    padding: 4px 12px;
    background: rgba(16, 185, 129, 0.1);
    color: #10B981;
    font-weight: 600;
    border-radius: 12px;
    font-size: 12px;
}

/* 风险评估 */
.risk-cards {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
}

.risk-card {
    padding: 24px;
    background: var(--surface);
    border-radius: 12px;
    border: 2px solid var(--border-color);
}

.risk-title {
    font-size: 14px;
    color: var(--text-muted);
    margin: 0 0 12px 0;
}

.risk-value {
    font-size: 24px;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 16px 0;
}

.risk-card.risk-low {
    border-color: #10B981;
    background: rgba(16, 185, 129, 0.05);
}

.risk-card.risk-low .risk-value {
    color: #10B981;
}

.risk-card.risk-medium {
    border-color: #F59E0B;
    background: rgba(245, 158, 11, 0.05);
}

.risk-card.risk-medium .risk-value {
    color: #F59E0B;
}

.risk-card.risk-high {
    border-color: #EF4444;
    background: rgba(239, 68, 68, 0.05);
}

.risk-card.risk-high .risk-value {
    color: #EF4444;
}

.risk-bar {
    height: 8px;
    background: var(--border-color);
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 12px;
}

.risk-fill {
    height: 100%;
    background: linear-gradient(90deg, #10B981, #F59E0B, #EF4444);
    border-radius: 4px;
    transition: width 0.3s ease;
}

.risk-desc {
    font-size: 13px;
    color: var(--text-muted);
    margin: 0;
    line-height: 1.5;
}

.accessibility-indicator {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.indicator-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
}

.accessibility-indicator.easy .indicator-dot {
    background: #10B981;
}

.accessibility-indicator.moderate .indicator-dot {
    background: #F59E0B;
}

.accessibility-indicator.difficult .indicator-dot {
    background: #EF4444;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
        transform: scale(1);
    }

    50% {
        opacity: 0.6;
        transform: scale(1.2);
    }
}

/* 诊断报告 */
.diagnostic-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.diagnostic-item {
    padding: 16px;
    background: var(--surface);
    border-radius: 10px;
    border-left: 4px solid var(--primary);
}

.diagnostic-item h4 {
    font-size: 15px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 8px 0;
}

.diagnostic-item p {
    font-size: 14px;
    color: var(--text);
    line-height: 1.6;
    margin: 0;
}

.diagnostic-item.recommendation {
    border-left-color: #10B981;
    background: rgba(16, 185, 129, 0.05);
}

.disclaimer {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--border-color);
    font-size: 12px;
    color: var(--text-muted) !important;
}

/* 实例级别详情 */
.instances-section {
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid var(--border-color);
}

.subsection-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text);
    margin: 0 0 16px 0;
}

.instances-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 16px;
}

.instance-card {
    background: var(--surface);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 16px;
    transition: all 0.2s ease;
}

.instance-card:hover {
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
    transform: translateY(-2px);
}

.instance-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
}

.instance-id {
    font-weight: 600;
    color: var(--text);
    font-size: 14px;
}

.instance-confidence {
    background: linear-gradient(135deg, var(--primary), #8B5CF6);
    color: white;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}

.instance-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.instance-field {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 13px;
}

.instance-field .field-label {
    color: var(--text-muted);
}

.instance-field .field-value {
    color: var(--text);
    font-weight: 500;
}

/* 报告尾部 */
.report-footer {
    margin-top: 32px;
    padding-top: 24px;
}

.footer-line {
    height: 2px;
    background: linear-gradient(90deg, var(--primary), transparent);
    margin-bottom: 16px;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.footer-item {
    display: flex;
    gap: 8px;
    font-size: 13px;
}

.footer-label {
    color: var(--text-muted);
}

.footer-value {
    color: var(--text);
    font-weight: 600;
}

/* 打印样式 */
@media print {
    .report-header .header-right {
        display: none;
    }

    .report-section {
        page-break-inside: avoid;
    }
}

/* 响应式 */
@media (max-width: 768px) {
    .report-header {
        flex-direction: column;
        gap: 16px;
    }

    .info-grid-2col,
    .detail-grid,
    .image-comparison,
    .risk-cards {
        grid-template-columns: 1fr;
    }

    .overview-cards {
        grid-template-columns: repeat(2, 1fr);
    }
}
</style>
