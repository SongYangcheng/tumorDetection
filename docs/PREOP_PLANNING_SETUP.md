# 术前规划3D模块 - 独立部署指南

## ✅ 已完成的功能

### 后端 (Backend)
1. **独立NII文件上传端点** - `POST /api/reconstruction/upload-nii`
   - 支持`.nii`和`.nii.gz`格式
   - 可选UNet分割或直接使用预分割掩码
   - 自动3D重建和肿瘤分析
   
2. **3D重建工具** - `utils/mesh_reconstruction.py`
   - Marching Cubes算法
   - 网格平滑和细化
   - STL导出支持

3. **分析API** - `GET /api/reconstruction/tumor-analysis/<id>`
   - 体积、表面积、紧凑度
   - 风险评分计算
   - 边界框和质心

4. **路径规划API** - `POST /api/reconstruction/surgical-path/<id>`
   - 入口点到目标点的路径计算
   - 安全评分
   - 风险警告

### 前端 (Frontend)
1. **NII文件直接上传** - 无需预先分割
2. **Three.js 3D可视化** - 完整的3D场景渲染
3. **交互控制** - 旋转、缩放、重置视角、截图
4. **肿瘤分析面板** - 实时显示几何指标
5. **手术路径规划** - 可视化路径和评分

## 🚀 启动步骤

### 1. 安装依赖

#### 后端Python依赖
```bash
cd backend
pip install flask flask-cors flask-jwt-extended sqlalchemy opencv-python numpy scipy scikit-image nibabel
```

#### 前端Node.js依赖
```bash
cd frontend
npm install three @types/three
```

### 2. 启动后端服务器

```bash
cd backend
python main.py
```

**预期输出**:
```
 * Running on http://127.0.0.1:8000
 * Registered blueprint: reconstruction at /api/reconstruction
```

**验证API可用**:
```bash
curl http://localhost:8000/api/reconstruction/upload-nii
# 应返回405 Method Not Allowed (因为需要POST)
```

### 3. 启动前端服务器

```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v7.3.0  ready in 844 ms
➜  Local:   http://localhost:5173/
```

### 4. 访问术前规划页面

浏览器打开: `http://localhost:5173/preop-planning`

## 📋 使用流程

### 方式一：上传NII文件（推荐，完全独立）

1. 点击"上传NII文件直接重建"按钮
2. 选择`.nii`或`.nii.gz`文件
3. 系统自动：
   - 上传文件到服务器
   - 执行3D重建（Marching Cubes）
   - 计算肿瘤几何指标
   - 渲染3D模型

**支持的NII文件类型**:
- ✅ 已分割的二值掩码 (推荐) - `use_unet=false`
- ✅ 原始MRI数据 + UNet分割 - `use_unet=true` (需要模型权重)

### 方式二：使用已上传的影像

1. 从列表中选择已分析的影像
2. 点击"生成3D模型"
3. 与现有YOLO/UNet结果集成

## 🔧 配置选项

### 后端配置 (backend/.env)
```env
# 数据库
DATABASE_URL=sqlite:///tumor_detection.db

# 上传目录
UPLOADS_DIR=backend/uploads

# UNet模型路径（可选，如果使用use_unet=true）
UNET_MODEL_PATH=backend/ai/brain_tumor/weights/ResNeXt50_best.pt
```

### 前端配置 (frontend/.env)
```env
# 后端API地址
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 📊 API端点详情

### 1. 上传NII并重建
```http
POST /api/reconstruction/upload-nii
Content-Type: multipart/form-data
Authorization: Bearer <token>

Body:
- file: NII文件
- spacing: [1.0, 1.0, 1.0] (可选)
- use_unet: false (可选)

Response:
{
  "success": true,
  "image_id": 123,
  "model_data": {
    "vertices": [[x,y,z], ...],
    "faces": [[i,j,k], ...],
    "volume": 1234.56
  },
  "analysis": {
    "volume_cm3": 1.23,
    "surface_area": 789.0,
    "centroid": [128, 128, 78],
    "risk_score": 6.5
  }
}
```

### 2. 肿瘤分析
```http
GET /api/reconstruction/tumor-analysis/<image_id>
Authorization: Bearer <token>

Response:
{
  "success": true,
  "analysis": {
    "volume": 1234.56,
    "surface_area": 789.01,
    "centroid": [x, y, z],
    "compactness": 0.68,
    "risk_score": 7.5
  }
}
```

### 3. 路径规划
```http
POST /api/reconstruction/surgical-path/<image_id>
Content-Type: application/json
Authorization: Bearer <token>

Body:
{
  "entry_point": [x, y, z],
  "target_point": [x, y, z]
}

Response:
{
  "success": true,
  "path": [[x,y,z], ...],
  "length": 45.6,
  "safety_score": 8.5,
  "warnings": ["路径较长，建议选择更近的入口点"]
}
```

## ⚠️ 常见问题

### 1. 404 Not Found on `/api/reconstruction/upload-nii`
**原因**: 后端服务器未运行或未注册blueprint

**解决**:
```bash
# 检查服务器是否运行
curl http://localhost:8000/health

# 重启后端
cd backend
python main.py
```

### 2. Three.js模块找不到
**原因**: 未安装Three.js依赖

**解决**:
```bash
cd frontend
npm install three @types/three
```

### 3. NII文件上传后重建失败
**原因**: NII文件不是有效的掩码或缺少UNet模型

**解决**:
- 确保NII文件是二值掩码（0和255）
- 或设置`use_unet=true`并提供UNet模型权重

### 4. `Cannot read properties of undefined (reading 'images')`
**原因**: API返回数据结构不匹配

**已修复**: 更新为`response.images`而不是`response.data.images`

## 🎯 下一步优化建议

1. **多切片存储** - 当前只保存单个overlay，改为存储完整切片序列
2. **实时路径优化** - 使用A*或Dijkstra算法计算最优路径
3. **风险区域可视化** - 在3D场景中高亮显示高风险区域
4. **STL导出功能** - 完成STL文件导出用于3D打印
5. **VR/AR支持** - 集成WebXR实现沉浸式手术规划

## 📝 测试清单

- [ ] 后端服务器启动成功
- [ ] 前端开发服务器运行
- [ ] 可访问术前规划页面
- [ ] 上传NII文件成功
- [ ] 3D模型渲染显示
- [ ] 肿瘤指标计算正确
- [ ] 可旋转/缩放3D模型
- [ ] 路径规划功能可用
- [ ] 截图功能工作

## 📚 技术栈

- **后端**: Flask, SQLAlchemy, scikit-image (Marching Cubes), OpenCV, nibabel
- **前端**: Vue 3, TypeScript, Three.js, OrbitControls
- **3D算法**: Marching Cubes, 网格细化, Gaussian平滑
- **路径规划**: 直线距离计算（可扩展为A*）

---

**部署完成后即可独立使用，无需依赖YOLO或UNet的预先分割结果！**
