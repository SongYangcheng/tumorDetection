<template>
  <div class="preop-planning">
    <div class="planning-header">
      <h1>术前3D规划系统</h1>
      <p class="subtitle">基于AI的脑肿瘤三维重建与手术路径规划</p>
    </div>

    <!-- 图像选择 -->
    <div v-if="!currentImageId" class="image-selector card">
      <div class="selector-header">
        <h3>选择医学影像</h3>
        <div class="upload-section">
          <label class="btn btn-primary upload-btn">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
              <polyline points="17 8 12 3 7 8" />
              <line x1="12" y1="3" x2="12" y2="15" />
            </svg>
            上传NII文件直接重建
            <input type="file" accept=".nii,.nii.gz" @change="uploadNiiFile" style="display: none" />
          </label>
          <span class="hint">支持.nii和.nii.gz格式，无需预先分割</span>
        </div>
      </div>

      <div v-if="uploadingNii" class="upload-progress">
        <div class="spinner"></div>
        <p>{{ niiUploadStatus }}</p>
      </div>

      <h4 style="margin-top: 2rem; color: var(--text-muted);">或选择已上传的NII影像</h4>
      <div class="image-grid">
        <div v-for="img in availableImages" :key="img.id" class="image-card nii-card" @click="selectImage(img.id)">
          <div class="nii-icon">📁</div>
          <div class="image-info">
            <p class="filename">{{ img.original_filename || img.filename }}</p>
            <p class="upload-time">{{ formatDate(img.uploaded_at) }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 主工作区 -->
    <div v-else class="planning-workspace">
      <!-- 左侧：3D可视化区域 -->
      <div class="viewer-panel card">
        <div class="panel-header">
          <h3>3D肿瘤模型</h3>
          <div class="view-controls">
            <button class="btn-icon" @click="resetView" title="重置视角">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10" />
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
            </button>
            <button class="btn-icon" @click="toggleWireframe" title="线框模式">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              </svg>
            </button>
            <button class="btn-icon" @click="toggleBrainOutline" title="切换脑部轮廓"
              :style="{ opacity: brainOutlineMesh ? 1 : 0.3 }">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10" />
                <path d="M12 2a10 10 0 0 0 0 20" />
              </svg>
            </button>
            <button class="btn-icon" @click="captureScreenshot" title="截图">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                <circle cx="12" cy="13" r="4" />
              </svg>
            </button>
          </div>
        </div>

        <div id="three-container" class="viewer-container" ref="threeContainer">
          <div v-if="loading3D" class="loading-overlay">
            <div class="spinner"></div>
            <p>正在生成3D模型...</p>
          </div>
          <div v-else-if="!model3D" class="empty-viewer">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path
                d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
            </svg>
            <p style="margin-top: 1rem; font-weight: 500;">3D模型视图</p>
            <p style="font-size: 0.875rem; margin-top: 0.5rem;">
              方式一：点击上方"上传NII文件直接重建"（推荐）
            </p>
            <p style="font-size: 0.875rem; margin-top: 0.25rem;">
              方式二：点击下方"从分割结果生成3D"
            </p>
          </div>
        </div>

        <div class="viewer-footer">
          <!-- 暂时移除从分割结果生成3D的功能，专注于NII上传 -->
          <span v-if="!model3D && !loading3D" class="hint" style="margin-left: 1rem;">
            提示: 使用上方的NII文件上传功能进行3D重建
          </span>
        </div>
      </div>

      <!-- 右侧：分析与规划面板 -->
      <div class="analysis-panel">
        <!-- 肿瘤分析 -->
        <div class="card">
          <h3>肿瘤分析</h3>
          <div v-if="tumorAnalysis" class="analysis-grid">
            <div class="metric-card">
              <div class="metric-icon" style="background: #EEF2FF;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2">
                  <path
                    d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                </svg>
              </div>
              <div class="metric-content">
                <span class="metric-label">体积</span>
                <span class="metric-value">{{ (tumorAnalysis.volume / 1000).toFixed(2) }} cm³</span>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon" style="background: #FEF3C7;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2">
                  <circle cx="12" cy="12" r="10" />
                </svg>
              </div>
              <div class="metric-content">
                <span class="metric-label">表面积</span>
                <span class="metric-value">{{ (tumorAnalysis.surface_area / 100).toFixed(2) }} cm²</span>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon" style="background: #DBEAFE;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2">
                  <path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z" />
                </svg>
              </div>
              <div class="metric-content">
                <span class="metric-label">紧凑度</span>
                <span class="metric-value">{{ (tumorAnalysis.compactness * 100).toFixed(1) }}%</span>
              </div>
            </div>

            <div class="metric-card">
              <div class="metric-icon" style="background: #FEE2E2;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                  <line x1="12" y1="9" x2="12" y2="13" />
                  <line x1="12" y1="17" x2="12.01" y2="17" />
                </svg>
              </div>
              <div class="metric-content">
                <span class="metric-label">风险评分</span>
                <span class="metric-value">{{ tumorAnalysis.risk_score.toFixed(1) }}/10</span>
              </div>
            </div>
          </div>
          <button v-else class="btn btn-secondary btn-block" @click="analyzeTumor">开始分析</button>
        </div>

        <!-- 手术路径规划 -->
        <div class="card">
          <h3>手术路径规划</h3>
          <div class="path-planning">
            <div class="form-group">
              <label>入口点 (X, Y, Z)</label>
              <div class="coord-input">
                <input v-model.number="surgicalPath.entry[0]" type="number" placeholder="X" />
                <input v-model.number="surgicalPath.entry[1]" type="number" placeholder="Y" />
                <input v-model.number="surgicalPath.entry[2]" type="number" placeholder="Z" />
              </div>
            </div>

            <div class="form-group">
              <label>目标点 (X, Y, Z)</label>
              <div class="coord-input">
                <input v-model.number="surgicalPath.target[0]" type="number" placeholder="X" />
                <input v-model.number="surgicalPath.target[1]" type="number" placeholder="Y" />
                <input v-model.number="surgicalPath.target[2]" type="number" placeholder="Z" />
              </div>
            </div>

            <button class="btn btn-primary btn-block" @click="planPath">计算路径</button>

            <div v-if="pathResult" class="path-result">
              <div class="result-item">
                <span class="label">路径长度:</span>
                <span class="value">{{ pathResult.length.toFixed(2) }} mm</span>
              </div>
              <div class="result-item">
                <span class="label">安全评分:</span>
                <span class="value">{{ pathResult.safety_score.toFixed(1) }}/10</span>
              </div>
              <div v-if="pathResult.warnings.length" class="warnings">
                <p v-for="(warning, idx) in pathResult.warnings" :key="idx" class="warning-text">
                  警告: {{ warning }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-buttons">
          <button class="btn btn-secondary" @click="backToImageList">返回列表</button>
          <button class="btn btn-primary" @click="savePlan">保存规划</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls'
import { useThemeStore } from '@/stores/theme'
import { storeToRefs } from 'pinia'
import { api } from '@/services/api'
import { testAuthentication } from '@/utils/auth-test'

const route = useRoute()
const router = useRouter()

// 主题相关
const themeStore = useThemeStore()
const { currentTheme } = storeToRefs(themeStore)

// 状态
const currentImageId = ref<number | null>(null)
const availableImages = ref<any[]>([])
const loading3D = ref(false)
const model3D = ref<any>(null)
const tumorAnalysis = ref<any>(null)
const pathResult = ref<any>(null)
const uploadingNii = ref(false)
const niiUploadStatus = ref('准备上传...')

// Three.js相关
const threeContainer = ref<HTMLElement | null>(null)
let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let tumorMesh: THREE.Mesh | null = null
let brainOutlineMesh: THREE.Mesh | null = null  // 脑部轮廓网格

// 手术路径
const surgicalPath = ref({
  entry: [0, 0, 0],
  target: [0, 0, 0]
})

// 初始化
onMounted(async () => {
  // 1. 先运行认证测试
  console.log('[开始认证测试]')
  const authResult = await testAuthentication()

  if (!authResult.success) {
    console.error('[认证测试失败]', authResult)
    alert(`认证失败: ${authResult.error}\n建议: ${authResult.suggestion}`)
    router.push('/login')
    return
  }

  console.log('[认证测试通过] 用户:', authResult.user?.username)

  // 2. 继续正常流程
  if (route.params.imageId) {
    currentImageId.value = Number(route.params.imageId)
    await initThreeJS()
  } else {
    await loadAvailableImages()
  }
})

onUnmounted(() => {
  disposeThreeJS()
})

// 监听主题变化，更新3D场景颜色
watch(currentTheme, (newTheme) => {
  if (scene) {
    const bgColor = newTheme === 'dark' ? 0x0f172a : 0xf8fafc
    scene.background = new THREE.Color(bgColor)
  }
})

// NII文件上传
async function uploadNiiFile(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  if (!file.name.endsWith('.nii') && !file.name.endsWith('.nii.gz')) {
    alert('仅支持.nii或.nii.gz格式文件')
    return
  }

  uploadingNii.value = true
  niiUploadStatus.value = '正在上传NII文件...'

  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('spacing', JSON.stringify([1.0, 1.0, 1.0]))
    formData.append('use_unet', 'true')  // 启用UNet进行分割，并提取脑部轮廓

    niiUploadStatus.value = '正在进行3D重建...'

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await fetch(`${apiBaseUrl}/api/reconstruction/upload-nii`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: formData
    })

    const data = await response.json()

    if (data.success) {
      niiUploadStatus.value = '重建完成！正在初始化3D视图...'

      // 设置图像ID
      currentImageId.value = data.image_id

      // 等待DOM更新完成后再初始化3D场景
      await nextTick()

      // 初始化Three.js场景
      await initThreeJS()

      // 再次检查scene是否成功创建
      if (!scene) {
        console.error('[initThreeJS失败] scene未创建')
        alert('3D场景初始化失败，请刷新页面后重试')
        uploadingNii.value = false
        input.value = ''
        return
      }

      // 直接渲染模型
      if (data.model_data) {
        model3D.value = data.model_data

        console.log('[收到3D数据]', {
          hasTumor: !!(data.model_data.vertices && data.model_data.faces),
          tumorVertices: data.model_data.vertices?.length || 0,
          tumorFaces: data.model_data.faces?.length || 0,
          hasBrainOutline: !!data.model_data.brain_outline,
          brainVertices: data.model_data.brain_outline?.vertices?.length || 0,
          brainFaces: data.model_data.brain_outline?.faces?.length || 0
        })

        renderTumorMesh(data.model_data)

        // 渲染脑部轮廓（如果有）
        if (data.model_data.brain_outline) {
          console.log('[开始渲染脑部轮廓]')
          renderBrainOutline(data.model_data.brain_outline)
        } else {
          console.warn('[警告] 后端未返回brain_outline数据')
          // 如果只有肿瘤没有脑轮廓，也创建包围盒
          updateBoundingBox()
        }
      }

      // 设置分析数据
      if (data.analysis) {
        tumorAnalysis.value = data.analysis

        // 设置默认手术路径点
        if (data.analysis.centroid) {
          surgicalPath.value.target = [...data.analysis.centroid]
          surgicalPath.value.entry = [
            data.analysis.centroid[0],
            data.analysis.centroid[1],
            data.analysis.centroid[2] + 50
          ]
        }
      }

      alert(`3D重建成功！\n体积: ${(data.analysis.volume_cm3).toFixed(2)} cm³`)
    } else {
      const errorMsg = `重建失败: ${data.error}\n${data.hint || ''}\n详情: ${data.detail || ''}`
      console.error('NII上传错误:', data)
      alert(errorMsg)
      uploadingNii.value = false
      input.value = ''
    }
  } catch (error) {
    console.error('NII上传异常:', error)

    let errorMsg = '上传失败: '
    if (error.message) {
      errorMsg += error.message
    } else {
      errorMsg += '未知错误'
    }

    errorMsg += '\n\n请检查:'
    errorMsg += '\n1. 后端服务器是否运行在 ' + (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000')
    errorMsg += '\n2. 文件格式是否正确 (.nii 或 .nii.gz)'
    errorMsg += '\n3. 文件是否包含有效的肿瘤数据'
    errorMsg += '\n4. 后端日志查看具体错误'

    alert(errorMsg)
  } finally {
    uploadingNii.value = false
    if (input) input.value = ''
  }
}

// 加载可用NII文件列表（仅用于术前规划）
async function loadAvailableImages() {
  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await fetch(`${apiBaseUrl}/api/reconstruction/nii-files`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    if (!response.ok) {
      throw new Error('获取NII文件列表失败')
    }

    const data = await response.json()
    availableImages.value = data.files || []
  } catch (error: any) {
    console.error('加载NII文件列表失败:', error)

    if (error.message?.includes('认证失败') || error.message?.includes('重新登录')) {
      alert('登录已过期，请重新登录')
      router.push('/login')
    } else {
      availableImages.value = []
      console.warn('无法加载NII文件列表: ' + (error.message || '未知错误'))
    }
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 选择图像
async function selectImage(imageId: number) {
  currentImageId.value = imageId
  await initThreeJS()
}

// 返回列表
function backToImageList() {
  currentImageId.value = null
  disposeThreeJS()
}

// 初始化Three.js场景
async function initThreeJS() {
  if (!threeContainer.value) return

  const container = threeContainer.value
  const width = container.clientWidth
  const height = container.clientHeight

  // 场景
  scene = new THREE.Scene()
  // 根据主题设置背景色
  const bgColor = currentTheme.value === 'dark' ? 0x0f172a : 0xf8fafc
  scene.background = new THREE.Color(bgColor)

  // 相机
  camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000)
  camera.position.set(150, 150, 150)

  // 渲染器
  renderer = new THREE.WebGLRenderer({ antialias: true })
  renderer.setSize(width, height)
  renderer.shadowMap.enabled = true
  container.appendChild(renderer.domElement)

  // 控制器 - 允许360度旋转
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minPolarAngle = 0  // 允许垂直旋转到顶部
  controls.maxPolarAngle = Math.PI  // 允许垂直旋转到底部
  controls.enableRotate = true  // 启用旋转
  controls.autoRotate = false  // 禁用自动旋转

  // 光照 - 根据主题调整
  const ambientIntensity = currentTheme.value === 'dark' ? 0.5 : 0.7
  const directionalIntensity = currentTheme.value === 'dark' ? 0.7 : 0.9
  
  const ambientLight = new THREE.AmbientLight(0xffffff, ambientIntensity)
  scene.add(ambientLight)

  const directionalLight = new THREE.DirectionalLight(0xffffff, directionalIntensity)
  directionalLight.position.set(100, 100, 50)
  directionalLight.castShadow = true
  scene.add(directionalLight)

  // 移除网格和坐标轴，改用3D包围盒线框
  // 包围盒会在模型渲染后动态创建

  // 动画循环
  animate()
}

// 动画循环
function animate() {
  if (!renderer || !scene || !camera || !controls) return

  requestAnimationFrame(animate)
  controls.update()
  renderer.render(scene, camera)
}

// 清理Three.js资源
function disposeThreeJS() {
  // 清理肿瘤mesh
  if (tumorMesh && scene) {
    scene.remove(tumorMesh)
    tumorMesh.geometry.dispose()
    if (Array.isArray(tumorMesh.material)) {
      tumorMesh.material.forEach(m => m.dispose())
    } else {
      tumorMesh.material.dispose()
    }
  }

  // 清理脑部轮廓mesh
  if (brainOutlineMesh && scene) {
    scene.remove(brainOutlineMesh)
    brainOutlineMesh.geometry.dispose()
    if (Array.isArray(brainOutlineMesh.material)) {
      brainOutlineMesh.material.forEach(m => m.dispose())
    } else {
      brainOutlineMesh.material.dispose()
    }
  }

  // 清理包围盒
  if (scene && (scene as any).boundingBox) {
    scene.remove((scene as any).boundingBox)
      ; (scene as any).boundingBox.geometry.dispose()
      ; (scene as any).boundingBox.material.dispose()
  }
}

// 渲染肿瘤网格
function renderTumorMesh(modelData: any) {
  if (!scene || !modelData.vertices || !modelData.faces) {
    console.error('[renderTumorMesh] 缺少必要数据', {
      hasScene: !!scene,
      hasVertices: !!modelData?.vertices,
      hasFaces: !!modelData?.faces
    })
    return
  }

  // 检查数据是否为空
  if (modelData.vertices.length === 0 || modelData.faces.length === 0) {
    console.error('[renderTumorMesh] 顶点或面数据为空')
    return
  }

  console.log('[开始渲染3D模型]', {
    vertices: modelData.vertices.length,
    faces: modelData.faces.length,
    firstVertex: modelData.vertices[0],
    lastVertex: modelData.vertices[modelData.vertices.length - 1]
  })

  // 移除旧的模型
  if (tumorMesh) {
    scene.remove(tumorMesh)
    tumorMesh.geometry.dispose()
    if (Array.isArray(tumorMesh.material)) {
      tumorMesh.material.forEach(m => m.dispose())
    } else {
      tumorMesh.material.dispose()
    }
  }

  // 创建几何体
  const geometry = new THREE.BufferGeometry()

  // 转换顶点数据
  const vertices = new Float32Array(modelData.vertices.flat())
  geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))

  // 转换面数据
  const indices = new Uint32Array(modelData.faces.flat())
  geometry.setIndex(new THREE.BufferAttribute(indices, 1))

  // 计算法向量
  geometry.computeVertexNormals()

  // 创建材质
  const material = new THREE.MeshPhongMaterial({
    color: 0xff4444,
    shininess: 100,
    transparent: true,
    opacity: 0.8,
    side: THREE.DoubleSide,
    depthWrite: true  // 启用深度写入，防止旋转时消失
  })

  // 创建网格
  tumorMesh = new THREE.Mesh(geometry, material)
  tumorMesh.castShadow = true
  tumorMesh.receiveShadow = true
  tumorMesh.renderOrder = 2  // 设置更高的渲染顺序，确保肿瘤在脑轮廓之后渲染

  scene.add(tumorMesh)

  // 调整相机位置以适应模型
  if (camera && controls) {
    geometry.computeBoundingBox()
    const bbox = geometry.boundingBox!
    const center = new THREE.Vector3()
    bbox.getCenter(center)

    const size = new THREE.Vector3()
    bbox.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)

    console.log('[肿瘤包围盒信息]', {
      center: center.toArray(),
      size: size.toArray(),
      maxDim,
      min: bbox.min.toArray(),
      max: bbox.max.toArray()
    })

    // 暂时调整相机（稍后会根据整体模型重新调整）
    camera.position.set(
      center.x + maxDim * 1.5,
      center.y + maxDim * 1.5,
      center.z + maxDim * 1.5
    )

    controls.target.copy(center)
    controls.update()
  }
}

// 渲染脑部轮廓
function renderBrainOutline(brainData: any) {
  if (!scene) {
    console.error('[renderBrainOutline] scene未初始化')
    return
  }

  if (!brainData?.vertices || !brainData?.faces) {
    console.warn('[警告] 无脑部轮廓数据')
    return
  }

  console.log('[开始渲染脑部轮廓]', {
    vertices: brainData.vertices.length,
    faces: brainData.faces.length,
    firstVertex: brainData.vertices[0],
    lastVertex: brainData.vertices[brainData.vertices.length - 1]
  })

  // 移除旧的脑部轮廓
  if (brainOutlineMesh) {
    scene.remove(brainOutlineMesh)
    brainOutlineMesh.geometry.dispose()
    if (Array.isArray(brainOutlineMesh.material)) {
      brainOutlineMesh.material.forEach(m => m.dispose())
    } else {
      brainOutlineMesh.material.dispose()
    }
  }

  // 创建几何体
  const geometry = new THREE.BufferGeometry()

  // 转换顶点数据
  const vertices = new Float32Array(brainData.vertices.flat())
  geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3))

  // 转换面数据
  const indices = new Uint32Array(brainData.faces.flat())
  geometry.setIndex(new THREE.BufferAttribute(indices, 1))

  // 计算法向量
  geometry.computeVertexNormals()

  // 创建材质（增强可见度：25%透明度 + 边缘发光）
  const material = new THREE.MeshPhongMaterial({
    color: 0xcccccc,  // 浅灰色
    transparent: true,
    opacity: 0.25,  // 提升到25%透明度，更容易看见
    wireframe: false,
    side: THREE.DoubleSide,
    shininess: 50,
    // 添加边缘发光效果
    emissive: 0x444444,
    emissiveIntensity: 0.2,
    // 禁用深度写入，让肿瘤可以透过脑轮廓显示
    depthWrite: false,
    // 启用深度测试
    depthTest: true
  })

  // 创建网格
  brainOutlineMesh = new THREE.Mesh(geometry, material)
  brainOutlineMesh.renderOrder = 1  // 设置较低的渲染顺序，先渲染脑轮廓
  scene.add(brainOutlineMesh)

  // 计算并显示边界框信息
  geometry.computeBoundingBox()
  const bbox = geometry.boundingBox!
  const center = new THREE.Vector3()
  bbox.getCenter(center)
  const size = new THREE.Vector3()
  bbox.getSize(size)

  console.log('[脑部轮廓渲染完成]', {
    vertices: brainData.vertices.length,
    faces: brainData.faces.length,
    center: center.toArray(),
    size: size.toArray(),
    min: bbox.min.toArray(),
    max: bbox.max.toArray()
  })

  // 创建包围盒框住整个场景（脑子+肿瘤）
  updateBoundingBox()
}

// 更新相机视角和旋转中心（不显示包围盒）
function updateBoundingBox() {
  if (!scene || !camera || !controls) return

  // 清理旧的包围盒（如果存在）
  if ((scene as any).boundingBox) {
    scene.remove((scene as any).boundingBox)
      ; ((scene as any).boundingBox as any).geometry.dispose()
      ; ((scene as any).boundingBox as any).material.dispose()
    delete (scene as any).boundingBox
  }

  // 优先使用脑子模型的中心作为旋转中心
  let center: THREE.Vector3
  let maxDim: number

  if (brainOutlineMesh) {
    // 如果有脑轮廓，使用脑轮廓的中心
    brainOutlineMesh.geometry.computeBoundingBox()
    const brainBox = brainOutlineMesh.geometry.boundingBox!
    center = new THREE.Vector3()
    brainBox.getCenter(center)

    const brainSize = new THREE.Vector3()
    brainBox.getSize(brainSize)
    maxDim = Math.max(brainSize.x, brainSize.y, brainSize.z)

    console.log('[使用脑轮廓中心作为旋转中心]', center.toArray())
  } else if (tumorMesh) {
    // 没有脑轮廓时，使用肿瘤中心
    tumorMesh.geometry.computeBoundingBox()
    const tumorBox = tumorMesh.geometry.boundingBox!
    center = new THREE.Vector3()
    tumorBox.getCenter(center)

    const tumorSize = new THREE.Vector3()
    tumorBox.getSize(tumorSize)
    maxDim = Math.max(tumorSize.x, tumorSize.y, tumorSize.z)

    console.log('[使用肿瘤中心作为旋转中心]', center.toArray())
  } else {
    console.warn('[警告] 无模型数据，无法调整视角')
    return
  }

  // 计算整体场景大小（用于相机距离）
  const box = new THREE.Box3()
  if (tumorMesh) {
    tumorMesh.geometry.computeBoundingBox()
    box.union(tumorMesh.geometry.boundingBox!)
  }
  if (brainOutlineMesh) {
    brainOutlineMesh.geometry.computeBoundingBox()
    box.union(brainOutlineMesh.geometry.boundingBox!)
  }

  const size = new THREE.Vector3()
  box.getSize(size)
  const sceneDim = Math.max(size.x, size.y, size.z)

  console.log('[场景信息]', {
    rotationCenter: center.toArray(),
    sceneSize: size.toArray(),
    sceneDim
  })

  // 调整相机位置（使用场景尺寸计算距离）
  camera.position.set(
    center.x + sceneDim * 1.5,
    center.y + sceneDim * 1.5,
    center.z + sceneDim * 1.5
  )

  // 设置旋转中心为计算出的中心点（脑子或肿瘤的中心）
  controls.target.copy(center)
  controls.update()
}

// 分析肿瘤
async function analyzeTumor() {
  if (!currentImageId.value) return

  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await fetch(`${apiBaseUrl}/api/reconstruction/tumor-analysis/${currentImageId.value}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      }
    })

    const data = await response.json()
    if (data.success) {
      tumorAnalysis.value = data.analysis

      // 设置默认的手术路径点
      if (data.analysis.centroid) {
        surgicalPath.value.target = [...data.analysis.centroid]
        surgicalPath.value.entry = [
          data.analysis.centroid[0],
          data.analysis.centroid[1],
          data.analysis.centroid[2] + 50
        ]
      }
    }
  } catch (error) {
    console.error('分析失败:', error)
  }
}

// 规划手术路径
async function planPath() {
  if (!currentImageId.value) return

  try {
    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
    const response = await fetch(`${apiBaseUrl}/api/reconstruction/surgical-path/${currentImageId.value}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        entry_point: surgicalPath.value.entry,
        target_point: surgicalPath.value.target
      })
    })

    const data = await response.json()
    if (data.success) {
      pathResult.value = data

      // 在3D场景中绘制路径
      drawSurgicalPath(data.path)
    }
  } catch (error) {
    console.error('路径规划失败:', error)
  }
}

// 绘制手术路径
function drawSurgicalPath(path: number[][]) {
  if (!scene) return

  // 移除旧的路径线
  const oldPath = scene.getObjectByName('surgical-path')
  if (oldPath) {
    scene.remove(oldPath)
  }

  // 创建路径线
  const points = path.map(p => new THREE.Vector3(p[0], p[1], p[2]))
  const geometry = new THREE.BufferGeometry().setFromPoints(points)
  const material = new THREE.LineBasicMaterial({ color: 0x00ff00, linewidth: 3 })
  const line = new THREE.Line(geometry, material)
  line.name = 'surgical-path'
  scene.add(line)

  // 添加端点标记
  const sphereGeometry = new THREE.SphereGeometry(2, 16, 16)
  const entryMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 })
  const targetMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })

  const entrySphere = new THREE.Mesh(sphereGeometry, entryMaterial)
  entrySphere.position.set(points[0].x, points[0].y, points[0].z)
  scene.add(entrySphere)

  const targetSphere = new THREE.Mesh(sphereGeometry, targetMaterial)
  targetSphere.position.set(points[points.length - 1].x, points[points.length - 1].y, points[points.length - 1].z)
  scene.add(targetSphere)
}

// 重置视角
function resetView() {
  if (camera && controls && tumorMesh) {
    const bbox = new THREE.Box3().setFromObject(tumorMesh)
    const center = new THREE.Vector3()
    bbox.getCenter(center)

    const size = new THREE.Vector3()
    bbox.getSize(size)
    const maxDim = Math.max(size.x, size.y, size.z)

    camera.position.set(
      center.x + maxDim * 1.5,
      center.y + maxDim * 1.5,
      center.z + maxDim * 1.5
    )

    controls.target.copy(center)
    controls.update()
  }
}

// 切换线框模式
function toggleWireframe() {
  if (tumorMesh && tumorMesh.material) {
    const material = tumorMesh.material as THREE.MeshPhongMaterial
    material.wireframe = !material.wireframe
  }
}

// 切换脑部轮廓可见性
function toggleBrainOutline() {
  if (brainOutlineMesh) {
    brainOutlineMesh.visible = !brainOutlineMesh.visible
    console.log(`[脑部轮廓${brainOutlineMesh.visible ? '显示' : '隐藏'}]`)
  } else {
    console.warn('[警告] 脑部轮廓mesh不存在')
  }
}

// 截图
function captureScreenshot() {
  if (renderer) {
    renderer.render(scene!, camera!)
    const dataURL = renderer.domElement.toDataURL('image/png')
    const link = document.createElement('a')
    link.download = `3d_tumor_${Date.now()}.png`
    link.href = dataURL
    link.click()
  }
}

// 导出STL
function exportSTL() {
  alert('STL导出功能开发中')
}

// 保存规划
async function savePlan() {
  alert('规划保存功能开发中')
}
</script>

<style scoped>
.preop-planning {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
  background: var(--background);
  min-height: 100vh;
  transition: var(--transition-theme);
}

.planning-header {
  text-align: center;
  margin-bottom: 2rem;
}

.planning-header h1 {
  font-size: 2rem;
  color: var(--text);
  margin-bottom: 0.5rem;
  font-weight: 700;
  transition: var(--transition-theme);
}

.subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  transition: var(--transition-theme);
}

/* 图像选择器 */
.image-selector {
  padding: 2rem;
}

.image-selector h3 {
  margin-bottom: 1.5rem;
  color: var(--text);
  font-weight: 600;
  transition: var(--transition-theme);
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.upload-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.upload-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.upload-btn svg {
  flex-shrink: 0;
}

.hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  transition: var(--transition-theme);
}

.upload-progress {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: var(--panel);
  border: 2px dashed var(--primary);
  border-radius: 8px;
  margin-bottom: 1.5rem;
  transition: var(--transition-theme);
}

.upload-progress p {
  color: var(--primary);
  font-weight: 500;
  transition: var(--transition-theme);
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1.5rem;
}

.image-card {
  cursor: pointer;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  border: 1px solid var(--border);
  background: var(--surface);
}

.image-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
  border-color: var(--primary);
  transition: var(--transition-theme);
}

.image-card img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.image-info {
  padding: 0.75rem;
  background: rgba(255, 255, 255, 0.03);
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.filename {
  font-size: 0.875rem;
  color: var(--text);
  margin-bottom: 0.5rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: var(--transition-theme);
}

.model-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: rgba(124, 58, 237, 0.12);
  color: var(--accent);
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
  transition: var(--transition-theme);
}

/* NII文件卡片样式 */
.nii-card {
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  padding: 1.5rem;
  min-height: 120px;
}

.nii-card img {
  display: none;
  /* 隐藏图片 */
}

.nii-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.nii-card .image-info {
  width: 100%;
}

.nii-card .filename {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text);
  margin-bottom: 0.25rem;
  word-break: break-word;
  transition: var(--transition-theme);
}

.nii-card .upload-time {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin: 0;
  transition: var(--transition-theme);
}

.nii-card:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: var(--primary);
  transition: var(--transition-theme);
}

.nii-card:hover .nii-icon {
  transform: scale(1.1);
  transition: transform 0.2s;
}

/* 工作区布局 */
.planning-workspace {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1.5rem;
}

/* 查看器面板 */
.viewer-panel {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  min-height: 600px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  color: var(--text);
  font-size: 1.125rem;
  font-weight: 600;
  transition: var(--transition-theme);
}

.view-controls {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: var(--primary);
  transition: var(--transition-theme);
}

.viewer-container {
  flex: 1;
  position: relative;
  background: #1f2937;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(31, 41, 55, 0.95);
  z-index: 10;
}

.loading-overlay p {
  color: var(--text-muted);
  margin-top: 1rem;
  transition: var(--transition-theme);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--border);
  border-top-color: var(--primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.empty-viewer {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-muted);
  transition: var(--transition-theme);
}

.empty-viewer svg {
  margin-bottom: 1rem;
  stroke: #6b7280;
}

.viewer-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  gap: 1rem;
}

/* 分析面板 */
.analysis-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.analysis-panel .card {
  padding: 1.5rem;
}

.analysis-panel h3 {
  color: #e5e7eb;
  font-size: 1.125rem;
  margin-bottom: 1rem;
  font-weight: 600;
}

.analysis-grid {
  display: grid;
  gap: 1rem;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.metric-icon {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.metric-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
  transition: var(--transition-theme);
}

.metric-value {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text);
  transition: var(--transition-theme);
}

/* 手术路径规划 */
.path-planning .form-group {
  margin-bottom: 1rem;
}

.path-planning label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 0.5rem;
  transition: var(--transition-theme);
}

.coord-input {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.coord-input input {
  padding: 0.5rem;
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.05);
  color: var(--text);
  transition: var(--transition-theme);
}

.path-result {
  margin-top: 1rem;
  padding: 1rem;
  background: rgba(16, 185, 129, 0.1);
  border-radius: 8px;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.result-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.result-item .label {
  color: var(--text-muted);
  font-size: 0.875rem;
  transition: var(--transition-theme);
}

.result-item .value {
  font-weight: 600;
  color: var(--success);
  transition: var(--transition-theme);
}

.warnings {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(16, 185, 129, 0.3);
}

.warning-text {
  color: var(--error);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  transition: var(--transition-theme);
}

/* 按钮样式 */
.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary);
  color: white;
  transition: var(--transition-theme);
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark);
  transition: var(--transition-theme);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text);
  border: 1px solid var(--border);
  transition: var(--transition-theme);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
}

.btn-block {
  width: 100%;
}

.action-buttons {
  display: flex;
  gap: 1rem;
}

.action-buttons .btn {
  flex: 1;
}

.card {
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.02));
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(8px);
}

/* 3D查看器深色主题额外样式 */
#three-container canvas {
  border-radius: 4px;
}

.viewer-container .empty-viewer p {
  color: #9ca3af;
  font-size: 0.95rem;
}
</style>
