# 双模型系统集成文档

## 概述

本系统现在支持两种肿瘤分割模型：
1. **YOLO11** - 快速实时检测，适合快速筛查
2. **UNet (ResNeXt50)** - 精确深度学习分割，适合精细分析

用户可以：
- 在两个模型之间切换进行单独预测
- 对比两个模型的预测结果
- 查看详细的指标差异分析

## 技术架构

### 后端组件

#### 1. UNet预测器 (`backend/utils/unet_predictor.py`)

**ResNeXtUNet模型架构**：
- 编码器：4层ResNeXt50特征提取
- 解码器：4层上采样 + 跳跃连接
- 输出：单通道二值分割掩码

**UNetPredictor类**：
```python
def __init__(self, weight_path, device='cpu', threshold=0.3)
def predict(self, image_path) -> (pred_mask, pred_prob, result_dict)
def visualize(self, image, mask, alpha=0.5) -> overlay_image
```

**返回结果格式** (与YOLO兼容):
```python
{
    'has_tumor': bool,
    'num_instances': int,
    'tumor_pixels': int,
    'total_pixels': int,
    'tumor_ratio': float,
    'avg_confidence': float,
    'instances': [
        {
            'id': int,
            'bbox': [x, y, w, h],
            'area': int,
            'confidence': float
        }
    ]
}
```

#### 2. 模型管理器 (`backend/utils/model_manager.py`)

**ModelManager类** - 统一的模型接口：

```python
def detect_model_type(weight_path: str) -> str
    # 自动检测模型类型（yolo或unet）
    # 基于文件名和checkpoint结构

def load_model(weight_path, model_type=None, conf_threshold=0.25, device='cpu')
    # 统一的模型加载接口
    # 返回：(model, actual_model_type)

def predict(model, model_type, image_path, **kwargs)
    # 统一的预测接口
    # 返回标准化结果格式

def compare_models(yolo_model, unet_model, image_path, output_dir)
    # 生成模型对比结果
    # 返回：comparison_path, yolo_path, unet_path, metrics_diff
```

**支持的模型类型**：
```python
SUPPORTED_MODELS = {
    'yolo': ['yolo', 'yolov8', 'yolov11', 'yolo11'],
    'unet': ['unet', 'resnext', 'resnext50']
}
```

#### 3. API路由 (`backend/routes/model_comparison.py`)

##### 端点1: 单模型预测
```
POST /api/model/predict/<image_id>
```

**请求体**:
```json
{
    "model_type": "yolo" | "unet",
    "weight_path": "weights/Yolov11_best.pt",
    "conf_threshold": 0.25
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "overlay_url": "/uploads/masks/overlay_123_20240115_143022.png",
        "mask_url": "/uploads/masks/mask_123_20240115_143022.png",
        "has_tumor": true,
        "num_instances": 2,
        "tumor_ratio": 15.3,
        "avg_confidence": 0.85,
        "instances": [...]
    }
}
```

##### 端点2: 模型对比
```
POST /api/model/compare/<image_id>
```

**请求体**:
```json
{
    "yolo_weight": "weights/Yolov11_best.pt",
    "unet_weight": "weights/ResNeXt50_best.pt",
    "conf_threshold": 0.25
}
```

**响应**:
```json
{
    "success": true,
    "data": {
        "comparison_url": "/uploads/comparisons/comparison_123_20240115.png",
        "yolo_overlay_url": "/uploads/comparisons/yolo_123_20240115.png",
        "unet_overlay_url": "/uploads/comparisons/unet_123_20240115.png",
        "yolo_metrics": {
            "tumor_ratio": 15.3,
            "num_instances": 2,
            "avg_confidence": 0.85
        },
        "unet_metrics": {
            "tumor_ratio": 16.8,
            "num_instances": 3,
            "avg_confidence": 0.78
        },
        "metrics_diff": {
            "tumor_ratio_diff": 1.5,
            "confidence_diff": -0.07,
            "instances_diff": 1
        }
    }
}
```

##### 端点3: 权重列表
```
GET /api/model/list-weights
```

**响应**:
```json
{
    "yolo_weights": [
        {
            "name": "Yolov11_best.pt",
            "path": "weights/Yolov11_best.pt",
            "size": "12.5 MB"
        }
    ],
    "unet_weights": [
        {
            "name": "ResNeXt50_best.pt",
            "path": "weights/ResNeXt50_best.pt",
            "size": "95.3 MB"
        }
    ]
}
```

#### 4. 主应用更新 (`backend/main.py`)

**新增导入**:
```python
from routes.model_comparison import model_comparison_bp
```

**注册蓝图**:
```python
app.register_blueprint(model_comparison_bp, url_prefix="/api/model")
```

**静态文件服务**:
```python
@app.route("/uploads/comparisons/<path:filename>")
def serve_comparisons(filename: str):
    uploads_root = os.path.dirname(app.config["UPLOADS_DIR"])
    comparisons_dir = os.path.join(uploads_root, 'comparisons')
    return send_from_directory(comparisons_dir, filename)
```

### 前端组件

#### 1. API服务更新 (`frontend/src/services/api.ts`)

**新增方法**:

```typescript
// 单模型预测
async predictWithModel(imageId: number, data: {
    model_type: 'yolo' | 'unet',
    weight_path: string,
    conf_threshold: number
}): Promise<any>

// 模型对比
async compareModels(imageId: number, data: {
    yolo_weight: string,
    unet_weight: string,
    conf_threshold: number
}): Promise<any>

// 获取权重列表
async listWeights(): Promise<{
    yolo_weights: any[],
    unet_weights: any[]
}>
```

**URL自动补全** - 确保所有图片URL包含完整HTTP前缀

#### 2. 工作台视图更新 (`frontend/src/views/WorkbenchView.vue`)

**新增UI组件**:

1. **模型类型选择器**
```vue
<div class="radio-group">
  <label class="radio-label">
    <input type="radio" v-model="modelType" value="yolo" />
    <span>YOLO11 (快速，实时)</span>
  </label>
  <label class="radio-label">
    <input type="radio" v-model="modelType" value="unet" />
    <span>UNet (精确，深度学习)</span>
  </label>
</div>
```

2. **动态权重选择**
```vue
<select v-model="weightPath" class="form-select">
  <option value="" v-if="modelType === 'yolo'">默认YOLO模型</option>
  <option value="" v-if="modelType === 'unet'">默认UNet模型</option>
  <option v-for="weight in availableWeights" :value="weight.path">
    {{ weight.name }}
  </option>
</select>
```

3. **模型对比按钮**
```vue
<button class="btn btn-secondary" @click="compareModels">
  模型对比
</button>
```

4. **对比结果展示**
```vue
<div v-if="comparisonResult" class="comparison-panel">
  <!-- 两列对比图像 -->
  <div class="comparison-images">
    <div class="comparison-col"><!-- YOLO --></div>
    <div class="comparison-col"><!-- UNet --></div>
  </div>
  <!-- 差异分析 -->
  <div class="diff-summary">...</div>
</div>
```

**新增响应式状态**:
```typescript
const modelType = ref<'yolo' | 'unet'>('yolo')
const availableWeights = ref<any[]>([])
const comparisonResult = ref<any>(null)
```

**新增方法**:
```typescript
// 模型类型切换
const onModelTypeChange = async () => {
    const weights = await api.listWeights()
    availableWeights.value = modelType.value === 'yolo' 
        ? weights.yolo_weights 
        : weights.unet_weights
}

// 单模型预测（更新）
const runSeg = async () => {
    const res = await api.predictWithModel(imageId.value, {
        model_type: modelType.value,
        weight_path: weightPath.value,
        conf_threshold: conf.value
    })
    // ... 处理结果
}

// 模型对比
const compareModels = async () => {
    const res = await api.compareModels(imageId.value, {
        yolo_weight: 'weights/Yolov11_best.pt',
        unet_weight: 'weights/ResNeXt50_best.pt',
        conf_threshold: conf.value
    })
    comparisonResult.value = res.data
}

// 差异颜色类
const getDiffClass = (diff: number) => {
    if (diff > 0) return 'diff-positive'  // 红色
    if (diff < 0) return 'diff-negative'  // 绿色
    return 'diff-neutral'  // 灰色
}
```

**新增CSS样式**:
- `.radio-group` - 单选按钮组
- `.comparison-panel` - 对比面板
- `.comparison-images` - 两列网格布局
- `.metrics-card` - 指标卡片
- `.diff-summary` - 差异摘要
- `.diff-positive/negative/neutral` - 差异值颜色

## 文件结构

```
backend/
├── utils/
│   ├── unet_predictor.py          # UNet推理模块 (NEW)
│   ├── model_manager.py           # 模型管理器 (NEW)
│   └── segmentation.py            # YOLO推理 (EXISTING)
├── routes/
│   ├── model_comparison.py        # 模型对比API (NEW)
│   └── yolo_detection.py          # YOLO检测API (EXISTING)
├── main.py                        # 注册新路由 (UPDATED)
└── weights/
    ├── Yolov11_best.pt
    ├── ResNeXt50_best.pt
    └── ResNeXt50_last.pt

frontend/
├── src/
│   ├── services/
│   │   └── api.ts                 # 新增API方法 (UPDATED)
│   └── views/
│       └── WorkbenchView.vue      # 模型选择+对比UI (UPDATED)
└── uploads/
    ├── masks/                     # 单模型结果
    └── comparisons/               # 对比结果 (NEW)
```

## 使用流程

### 1. 单模型预测

**用户操作**:
1. 在数据管理页面选择影像
2. 点击"开始分析"进入工作台
3. 选择模型类型（YOLO或UNet）
4. 选择权重文件（可选）
5. 调整置信度阈值
6. 点击"开始分割"

**系统流程**:
```
前端 WorkbenchView → predictWithModel()
                   ↓
后端 /api/model/predict/<id>
                   ↓
ModelManager.load_model()
                   ↓
ModelManager.predict()
                   ↓
保存 overlay → uploads/masks/
                   ↓
返回结果（包含完整URL）
                   ↓
前端显示分割结果
```

### 2. 模型对比

**用户操作**:
1. 在工作台加载影像
2. 点击"模型对比"按钮

**系统流程**:
```
前端 WorkbenchView → compareModels()
                   ↓
后端 /api/model/compare/<id>
                   ↓
加载YOLO模型 → 预测 → 生成overlay
                   ↓
加载UNet模型 → 预测 → 生成overlay
                   ↓
生成三张对比图：
  - YOLO overlay
  - UNet overlay  
  - 并排对比图
                   ↓
计算指标差异：
  - tumor_ratio_diff
  - confidence_diff
  - instances_diff
                   ↓
保存到 uploads/comparisons/
                   ↓
返回所有URL和指标
                   ↓
前端显示对比面板
```

## 部署步骤

### 1. 安装依赖

```bash
# 确保PyTorch已正确安装
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip install -r requirements.txt

# 可选：安装额外库
pip install opencv-python pydicom nibabel albumentations
```

### 2. 准备模型权重

```bash
# 将权重文件放到正确位置
backend/weights/
├── Yolov11_best.pt
├── ResNeXt50_best.pt
└── ResNeXt50_last.pt
```

### 3. 创建必要目录

```bash
mkdir -p backend/uploads/masks
mkdir -p backend/uploads/comparisons
```

### 4. 启动后端

```bash
cd backend
python main.py
# 后端运行在 http://127.0.0.1:8000
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
# 前端运行在 http://localhost:5173
```

## 测试清单

### 单元测试

- [ ] UNetPredictor 可以加载权重
- [ ] UNetPredictor.predict() 返回正确格式
- [ ] ModelManager 正确检测模型类型
- [ ] ModelManager 统一加载YOLO和UNet
- [ ] API端点返回正确状态码和数据

### 集成测试

- [ ] 前端可以切换模型类型
- [ ] 权重列表正确加载
- [ ] YOLO预测正常工作
- [ ] UNet预测正常工作
- [ ] 模型对比生成三张图片
- [ ] 指标差异计算正确
- [ ] 图片URL可访问

### 端到端测试

1. **YOLO工作流**:
   - 上传影像 → 选择YOLO → 分割 → 查看结果 ✓

2. **UNet工作流**:
   - 上传影像 → 选择UNet → 分割 → 查看结果 ✓

3. **对比工作流**:
   - 上传影像 → 点击对比 → 查看两模型结果 ✓
   - 验证指标差异显示正确 ✓

4. **切换模型**:
   - YOLO → UNet → 权重列表更新 ✓
   - UNet → YOLO → 权重列表更新 ✓

## 故障排除

### 问题1: UNet模型加载失败

**症状**: `RuntimeError: Error(s) in loading state_dict`

**解决**:
```python
# 检查权重文件结构
checkpoint = torch.load('weights/ResNeXt50_best.pt', map_location='cpu')
print(checkpoint.keys())  # 应包含 'model' 或 'state_dict'
```

### 问题2: 对比图片无法显示

**症状**: 前端显示404

**解决**:
1. 检查 `backend/uploads/comparisons/` 目录存在
2. 检查文件权限
3. 验证静态路由已注册
```python
# 在浏览器访问
http://127.0.0.1:8000/uploads/comparisons/comparison_xxx.png
```

### 问题3: 前端API调用失败

**症状**: `CORS error` 或 `Network error`

**解决**:
1. 确认后端运行在8000端口
2. 检查 `frontend/.env` 中 `VITE_API_BASE_URL=http://127.0.0.1:8000`
3. 验证CORS配置：
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 问题4: 模型预测结果不一致

**原因**: YOLO和UNet使用不同的预处理

**理解**:
- YOLO: 640x640 resize, 自动归一化
- UNet: 224x224 resize, ImageNet归一化 (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])

这是正常的，两个模型设计不同，结果会有差异。

## API使用示例

### Python客户端

```python
import requests

# 1. 登录获取token
response = requests.post('http://127.0.0.1:8000/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access_token']

headers = {'Authorization': f'Bearer {token}'}

# 2. 单模型预测
response = requests.post(
    'http://127.0.0.1:8000/api/model/predict/123',
    json={
        'model_type': 'unet',
        'weight_path': 'weights/ResNeXt50_best.pt',
        'conf_threshold': 0.25
    },
    headers=headers
)
result = response.json()
print(f"Tumor ratio: {result['data']['tumor_ratio']}%")

# 3. 模型对比
response = requests.post(
    'http://127.0.0.1:8000/api/model/compare/123',
    json={
        'yolo_weight': 'weights/Yolov11_best.pt',
        'unet_weight': 'weights/ResNeXt50_best.pt',
        'conf_threshold': 0.25
    },
    headers=headers
)
comparison = response.json()
print(f"Diff: {comparison['data']['metrics_diff']}")
```

### JavaScript客户端

```javascript
// 1. 登录
const login = await fetch('http://127.0.0.1:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' })
})
const { access_token } = await login.json()

// 2. 预测
const predict = await fetch('http://127.0.0.1:8000/api/model/predict/123', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${access_token}`
  },
  body: JSON.stringify({
    model_type: 'unet',
    weight_path: 'weights/ResNeXt50_best.pt',
    conf_threshold: 0.25
  })
})
const result = await predict.json()
console.log('Overlay URL:', result.data.overlay_url)
```

## 性能优化建议

### 1. 模型缓存

**问题**: 每次预测都重新加载模型，很慢

**解决**: 在ModelManager中添加模型缓存
```python
class ModelManager:
    def __init__(self):
        self._model_cache = {}  # {weight_path: (model, model_type)}
    
    def load_model(self, weight_path, ...):
        if weight_path in self._model_cache:
            return self._model_cache[weight_path]
        # ... 加载模型
        self._model_cache[weight_path] = (model, model_type)
        return model, model_type
```

### 2. 异步预测

**问题**: 对比两个模型时串行执行，耗时翻倍

**解决**: 使用异步并行预测
```python
import asyncio

async def compare_models_async(yolo_model, unet_model, image_path):
    yolo_task = asyncio.to_thread(predict, yolo_model, 'yolo', image_path)
    unet_task = asyncio.to_thread(predict, unet_model, 'unet', image_path)
    yolo_result, unet_result = await asyncio.gather(yolo_task, unet_task)
    return yolo_result, unet_result
```

### 3. GPU加速

**配置**:
```python
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model_manager = ModelManager()
model, _ = model_manager.load_model(weight_path, device=device)
```

## 下一步开发

### 短期任务

- [ ] 添加模型预测进度条
- [ ] 支持批量对比多张影像
- [ ] 导出对比报告（PDF）
- [ ] 添加模型性能指标（推理时间、内存占用）

### 中期任务

- [ ] 集成更多模型（Mask R-CNN、SAM）
- [ ] 支持3D医学影像分割
- [ ] 添加模型集成（ensemble）功能
- [ ] 实现在线模型训练

### 长期规划

- [ ] 开发模型市场，用户可上传自定义模型
- [ ] 联邦学习支持
- [ ] 自动化模型选择（根据影像特征推荐最佳模型）
- [ ] 模型解释性分析（GradCAM、LIME）

## 贡献指南

添加新模型时，请遵循以下步骤：

1. **创建预测器** (`backend/utils/your_model_predictor.py`):
```python
class YourModelPredictor:
    def __init__(self, weight_path, device='cpu', **kwargs):
        # 加载模型
        
    def predict(self, image_path):
        # 返回标准格式：(mask, prob, result_dict)
        return pred_mask, pred_prob, {
            'has_tumor': bool,
            'num_instances': int,
            'tumor_ratio': float,
            'avg_confidence': float,
            'instances': [...]
        }
```

2. **更新ModelManager** (`backend/utils/model_manager.py`):
```python
SUPPORTED_MODELS = {
    'yolo': [...],
    'unet': [...],
    'your_model': ['your_model_name', ...]  # 添加这行
}

def load_model(self, weight_path, model_type=None, ...):
    # 添加新模型加载逻辑
    elif model_type == 'your_model':
        from utils.your_model_predictor import YourModelPredictor
        model = YourModelPredictor(weight_path, device=device, ...)
```

3. **更新前端** (`frontend/src/views/WorkbenchView.vue`):
```vue
<label class="radio-label">
  <input type="radio" v-model="modelType" value="your_model" />
  <span>Your Model (描述)</span>
</label>
```

4. **测试**: 确保新模型通过所有测试用例

## 许可证

本项目遵循项目根目录的LICENSE文件。

## 联系方式

如有问题或建议，请提交Issue或Pull Request。

---

**文档版本**: 1.0  
**最后更新**: 2024-01-15  
**维护者**: Development Team
