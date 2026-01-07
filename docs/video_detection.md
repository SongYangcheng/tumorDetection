# 🎥 视频影像检测功能文档

## 功能概览

视频影像检测模块支持两种检测方式：
1. **视频文件上传检测** - 上传医学影像视频进行批量帧分析
2. **实时摄像头流检测** - 使用摄像头进行实时肿瘤检测

## 功能特性

### 📤 视频上传检测

- ✅ 支持多种视频格式：MP4, AVI, MOV, MKV, FLV, WMV
- ✅ 自动提取关键帧进行分析
- ✅ 可配置帧间隔和置信度阈值
- ✅ 实时显示上传和分析进度
- ✅ 生成详细的检测统计报告
- ✅ 保存检测结果到数据库

### 📹 实时流检测

- ✅ 支持浏览器摄像头访问
- ✅ 实时帧检测（约5 FPS）
- ✅ 动态检测框绘制
- ✅ 实时FPS和置信度显示
- ✅ 可调整置信度阈值

## 使用方法

### 1. 访问视频检测页面

在系统中导航到"视频检测"页面，或访问路由 `/video-detection`

### 2. 视频上传检测

#### 步骤：

1. **选择标签页**：点击"📤 视频上传检测"
2. **上传视频**：
   - 点击上传区域选择视频文件
   - 或直接拖拽视频文件到上传区
3. **填写信息**：
   - 患者ID（必填）
   - 患者姓名（必填）
   - 置信度阈值（默认0.25，范围0.1-0.9）
   - 帧间隔（默认30，表示每30帧提取一帧）
4. **开始分析**：点击"🚀 开始分析"按钮
5. **查看结果**：
   - 总帧数
   - 分析帧数
   - 检测到肿瘤的帧数
   - 检出率
   - 样本帧详情

#### 参数说明：

| 参数       | 说明                                  | 默认值 | 范围    |
| ---------- | ------------------------------------- | ------ | ------- |
| 置信度阈值 | 检测置信度的最小值，越高越严格        | 0.25   | 0.1-0.9 |
| 帧间隔     | 每隔N帧提取一帧分析，减小以提高准确度 | 30     | 1-120   |

### 3. 实时流检测

#### 步骤：

1. **选择标签页**：点击"📹 实时流检测"
2. **启动摄像头**：
   - 点击"🎥 启动摄像头"按钮
   - 浏览器会请求摄像头权限，点击"允许"
3. **调整参数**：
   - 使用滑块调整置信度阈值
4. **实时检测**：
   - 红色框：检测到的肿瘤区域
   - 数值：检测置信度
   - FPS：当前检测帧率
5. **停止检测**：点击"⏹️ 停止检测"按钮

## API端点

### 后端API

```python
# 视频上传检测
POST /api/video/upload
Form-data:
  - file: 视频文件
  - patient_id: 患者ID
  - patient_name: 患者姓名
  - conf_threshold: 置信度阈值（可选，默认0.25）
  - frame_interval: 帧间隔（可选，默认30）

# 实时流帧检测
POST /api/video/stream/detect
JSON Body:
  - frame: base64编码的图像帧
  - conf_threshold: 置信度阈值（可选）

# 获取流配置信息
GET /api/video/stream/info

# 处理已上传视频
POST /api/video/process/<video_id>
JSON Body:
  - conf_threshold: 置信度阈值（可选）
  - frame_interval: 帧间隔（可选）
```

### 前端API调用

```typescript
// 上传视频
await api.uploadVideo(file, {
  patientId: 'P001',
  patientName: '张三',
  confThreshold: 0.25,
  frameInterval: 30
}, (progress) => {
  console.log(`上传进度: ${progress}%`)
})

// 实时流帧检测
const result = await api.detectStreamFrame(frameBase64, 0.25)
console.log(result.detection)

// 获取流信息
const info = await api.getVideoStreamInfo()
```

## 技术实现

### 后端

1. **视频处理器** (`utils/video_processing.py`):
   - `VideoProcessor` 类：视频帧提取、检测、处理
   - 使用OpenCV进行视频读取和帧处理
   - 集成YOLO模型进行实时检测

2. **路由** (`routes/video_detection.py`):
   - `/upload`: 视频上传和批量帧分析
   - `/stream/detect`: 单帧实时检测
   - `/process/<id>`: 处理已上传视频生成标注视频

### 前端

1. **视频检测页面** (`VideoDetectionView.vue`):
   - 双标签页设计（上传/实时流）
   - 视频预览和进度显示
   - Canvas叠加层绘制检测框
   - WebRTC摄像头访问

2. **API服务** (`services/api.ts`):
   - XMLHttpRequest实现文件上传进度监控
   - Fetch API用于实时帧检测

## 配置要求

### 服务器

- Python 3.8+
- OpenCV (`opencv-python`)
- PyTorch
- Ultralytics YOLO

### 客户端

- 现代浏览器（支持WebRTC）
- 摄像头权限（仅实时流检测）

## 性能优化建议

### 视频上传检测

1. **帧间隔**：
   - 快速筛查：60-120帧
   - 标准检测：30帧（默认）
   - 精细检测：10-15帧

2. **置信度阈值**：
   - 高敏感度：0.10-0.15（可能有误报）
   - 平衡模式：0.20-0.30（推荐）
   - 高精度：0.40-0.50（可能漏检）

### 实时流检测

- 检测间隔：200ms（约5 FPS）
- 分辨率：640x480（默认）
- 可根据性能调整检测频率

## 数据存储

检测结果存储在 `medical_images` 表中：

- `modality`: 'Video'
- `detection_result`: JSON格式的完整检测信息
  - `video_info`: 视频元信息
  - `summary`: 统计摘要
  - `frame_results`: 每帧检测结果

## 故障排除

### 视频上传失败

- ✅ 检查视频格式是否支持
- ✅ 确认文件大小限制
- ✅ 验证后端服务运行状态

### 摄像头无法访问

- ✅ 检查浏览器权限设置
- ✅ 确认使用HTTPS或localhost
- ✅ 测试摄像头硬件是否正常

### 检测效果不佳

- ✅ 调整置信度阈值
- ✅ 确认YOLO模型已正确加载
- ✅ 检查输入图像质量

## 未来扩展

- [ ] 支持实时视频流（RTSP/RTMP）
- [ ] 生成带标注的视频导出
- [ ] 多摄像头同时检测
- [ ] GPU加速优化
- [ ] 检测结果时间轴可视化

## 示例代码

### 使用VideoProcessor类

```python
from utils.video_processing import VideoProcessor

# 初始化
processor = VideoProcessor(model_path='path/to/yolo.pt')

# 获取视频信息
info = processor.get_video_info('video.mp4')

# 提取并检测关键帧
for frame_num, frame in processor.extract_frames('video.mp4', frame_interval=30):
    detection = processor.detect_frame(frame, conf_threshold=0.25)
    print(f"帧 {frame_num}: {detection}")

# 处理整个视频
results = processor.process_video(
    'input.mp4',
    'output.mp4',
    conf_threshold=0.25
)
```

---

**更新日期**：2026年1月4日  
**版本**：1.0.0
