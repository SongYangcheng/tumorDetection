# API 完整参考文档

**版本**: 1.0  
**更新日期**: 2026-01-04  
**基础 URL**: `http://127.0.0.1:8000`（开发环境）

---

## 目录

1. [认证机制](#认证机制)
2. [认证端点](#认证端点)
3. [医学影像管理](#医学影像管理)
4. [分析与结果](#分析与结果)
5. [仪表板](#仪表板)
6. [工作台](#工作台)
7. [术前规划](#术前规划)
8. [影像组学](#影像组学)
9. [分析与报告](#分析与报告)
10. [用户管理与系统](#用户管理与系统)
11. [核心端点](#核心端点)
12. [错误处理](#错误处理)
13. [使用示例](#使用示例)

---

## 认证机制

所有受保护的端点需要在请求头中包含有效的 JWT token：

```
Authorization: Bearer <ACCESS_TOKEN>
```

Token 有效期为 **3600 秒**（1 小时）。

---

## 认证端点

### 注册用户

```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**响应** (201):
```json
{
  "message": "用户注册成功",
  "user_id": 2
}
```

---

### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**响应** (200):
```json
{
  "message": "登录成功",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true,
    "created_at": "2025-12-28T10:00:00"
  }
}
```

---

### 获取用户信息

```http
GET /api/auth/profile
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "created_at": "2025-12-28T10:00:00",
    "is_admin": true
  }
}
```

**错误** (401):
```json
{
  "error": "Token has expired"
}
```

---

### 修改密码

```http
POST /api/auth/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "admin123",
  "new_password": "NewSecurePass456"
}
```

**响应** (200):
```json
{
  "message": "密码修改成功"
}
```

**错误** (400):
```json
{
  "error": "旧密码不正确"
}
```

---

## 医学影像管理

### 上传影像

```http
POST /api/medical/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: <二进制文件>
patient_id: "P001" (可选)
patient_name: "张三" (可选)
age: 45 (可选)
gender: "M" (可选)
scan_date: "2025-12-28" (可选)
modality: "MRI" (可选)
body_part: "Brain" (可选)
```

**支持格式**: PNG, JPG, JPEG, TIFF, DCM, NII, NII.GZ  
**最大文件**: 500MB  

**响应** (201):
```json
{
  "message": "医学影像上传成功",
  "image_id": 1,
  "filename": "uuid_patient_scan.png",
  "file_url": "/uploads/medical_images/uuid_patient_scan.png",
  "preview_url": "/uploads/medical_images/uuid_patient_scan_preview.png"
}
```

**错误** (400):
```json
{
  "error": "不支持的文件格式"
}
```

**错误** (401):
```json
{
  "error": "未认证"
}
```

---

### 列出影像

```http
GET /api/medical/list?page=1&per_page=12
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码（默认 1）
- `per_page`: 每页数量（默认 12）
- `patient_id`: 按患者 ID 过滤
- `modality`: 按模态过滤（MRI, CT, X-ray 等）

**响应** (200):
```json
{
  "images": [
    {
      "id": 1,
      "filename": "uuid_scan_001.png",
      "original_filename": "patient_scan.png",
      "filepath": "uploads/medical_images/uuid_scan_001.png",
      "file_url": "/uploads/medical_images/uuid_scan_001.png",
      "preview_url": "/uploads/medical_images/uuid_scan_001_preview.png",
      "file_size": 1753293,
      "mime_type": "image/png",
      "patient_id": "P001",
      "patient_name": "张三",
      "scan_date": "2025-12-28",
      "study_date": "2025-12-28",
      "modality": "MRI",
      "body_part": "Brain",
      "institution": "协和医院",
      "age": 45,
      "gender": "M",
      "tumor_detected": false,
      "confidence_score": null,
      "uploaded_by": 1,
      "uploaded_at": "2026-01-04T09:00:00",
      "updated_at": "2026-01-04T09:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 12,
    "total": 5,
    "pages": 1
  }
}
```

---

### 获取单个影像

```http
GET /api/medical/{image_id}
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "id": 1,
  "filename": "uuid_scan_001.png",
  "original_filename": "patient_scan.png",
  "filepath": "uploads/medical_images/uuid_scan_001.png",
  "file_url": "/uploads/medical_images/uuid_scan_001.png",
  "preview_url": "/uploads/medical_images/uuid_scan_001_preview.png",
  "file_size": 1753293,
  "mime_type": "image/png",
  "patient_id": "P001",
  "patient_name": "张三",
  "scan_date": "2025-12-28",
  "study_date": "2025-12-28",
  "modality": "MRI",
  "body_part": "Brain",
  "institution": "协和医院",
  "age": 45,
  "gender": "M",
  "diagnosis": "脑肿瘤",
  "tumor_detected": false,
  "confidence_score": null,
  "segmentation_mask_path": null,
  "detection_result": "{}",
  "tumor_volume": null,
  "tumor_area": null,
  "max_diameter": null,
  "radiomics_features": "{}",
  "surgical_plan": null,
  "is_annotated": false,
  "is_validated": false,
  "annotation_data": "{}",
  "uploaded_by": 1,
  "uploaded_at": "2026-01-04T09:00:00",
  "updated_at": "2026-01-04T09:00:00"
}
```

**错误** (404):
```json
{
  "error": "影像不存在"
}
```

---

### 更新影像信息

```http
PUT /api/medical/{image_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "patient_name": "张三",
  "age": 45,
  "gender": "M",
  "diagnosis": "脑肿瘤",
  "is_validated": true,
  "annotation_data": "{\"notes\": \"良性\"}"
}
```

**响应** (200):
```json
{
  "message": "医学影像信息更新成功",
  "image": { ... }
}
```

---

### 删除影像

```http
DELETE /api/medical/{image_id}
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "医学影像删除成功"
}
```

**错误** (403):
```json
{
  "error": "权限不足"
}
```

---

### 批量删除

```http
POST /api/medical/delete-batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "ids": [1, 2, 3]
}
```

**响应** (200):
```json
{
  "message": "批量删除成功",
  "deleted_ids": [1, 2, 3]
}
```

---

## 分析与结果

### 分析影像

```http
POST /api/results/analyze/{image_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "conf": 0.25,
  "weightPath": "Yolov11_best.pt"
}
```

**请求参数说明**:
- `conf`: 检测置信度阈值（0.0-1.0）
- `weightPath`: 模型权重文件路径（相对路径或绝对路径）

**响应** (200):
```json
{
  "message": "分析完成",
  "tumor_detected": true,
  "confidence_score": 0.92,
  "bounding_box": [100, 150, 300, 350],
  "segmentation_mask": "data:image/png;base64,...",
  "tumor_volume": 15342.5,
  "tumor_area": 245.6,
  "max_diameter": 32.5,
  "radiomics_features": {
    "GLCM_Contrast": 0.42,
    "GLRLM_SRE": 0.78,
    "FirstOrder_Mean": 128.3
  }
}
```

**错误** (404):
```json
{
  "error": "影像不存在"
}
```

**错误** (500):
```json
{
  "error": "模型加载失败"
}
```

---

## 仪表板

### 获取统计数据

```http
GET /api/dashboard/stats
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "todayCases": 12,
  "modelAccuracy": 0.89,
  "systemStatus": "healthy",
  "totalImages": 425,
  "detectedTumors": 198
}
```

---

### 案例趋势

```http
GET /api/dashboard/cases-trend?start=2025-12-01&end=2026-01-04
Authorization: Bearer <token>
```

**查询参数**:
- `start`: 开始日期（YYYY-MM-DD）
- `end`: 结束日期（YYYY-MM-DD）

**响应** (200):
```json
[
  {"date": "2025-12-28", "value": 15},
  {"date": "2025-12-29", "value": 18},
  {"date": "2025-12-30", "value": 12},
  {"date": "2025-12-31", "value": 22},
  {"date": "2026-01-01", "value": 8},
  {"date": "2026-01-02", "value": 19},
  {"date": "2026-01-03", "value": 21},
  {"date": "2026-01-04", "value": 11}
]
```

---

### 准确度趋势

```http
GET /api/dashboard/accuracy-trend
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {"date": "2025-12-28", "value": 0.85},
  {"date": "2025-12-29", "value": 0.87},
  {"date": "2025-12-30", "value": 0.88},
  {"date": "2025-12-31", "value": 0.89},
  {"date": "2026-01-01", "value": 0.89},
  {"date": "2026-01-02", "value": 0.90},
  {"date": "2026-01-03", "value": 0.89},
  {"date": "2026-01-04", "value": 0.89}
]
```

---

### 部门分布 (新增)

```http
GET /api/dashboard/dept-dist
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {"name": "神经外科", "value": 32},
  {"name": "肿瘤科", "value": 18},
  {"name": "放射科", "value": 12},
  {"name": "神经内科", "value": 8},
  {"name": "综合科", "value": 5}
]
```

---

### 医生分布 (新增)

```http
GET /api/dashboard/doctor-dist
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {"name": "李医生", "value": 45},
  {"name": "王医生", "value": 38},
  {"name": "张医生", "value": 32},
  {"name": "刘医生", "value": 28}
]
```

---

### 最近案例

```http
GET /api/dashboard/recent-cases
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {
    "id": 1,
    "patient_id": "P001",
    "patient_name": "张三",
    "scan_date": "2026-01-03",
    "modality": "MRI",
    "tumor_detected": true,
    "confidence_score": 0.92,
    "status": "已分析"
  },
  {
    "id": 2,
    "patient_id": "P002",
    "patient_name": "李四",
    "scan_date": "2026-01-02",
    "modality": "CT",
    "tumor_detected": false,
    "confidence_score": 0.15,
    "status": "已分析"
  }
]
```

---

### 待办事项

```http
GET /api/dashboard/todos
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {"id": 1, "title": "审核图像数据集", "status": "pending", "priority": "high"},
  {"id": 2, "title": "更新模型权重", "status": "in_progress", "priority": "high"},
  {"id": 3, "title": "生成月度报告", "status": "pending", "priority": "medium"}
]
```

---

## 工作台

### 预处理

```http
POST /api/workbench/preprocess
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_id": 1,
  "normalize": "minmax",
  "denoise": "bilateral",
  "clahe": true
}
```

**参数说明**:
- `normalize`: 归一化方法（minmax, zscore, none）
- `denoise`: 降噪方法（bilateral, gaussian, median, none）
- `clahe`: 是否应用 CLAHE（对比度限制自适应直方图均衡）

**响应** (200):
```json
{
  "message": "预处理完成",
  "preprocessed_image": "data:image/png;base64,...",
  "processing_time_ms": 450
}
```

---

### 数据增强

```http
POST /api/workbench/augment
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_id": 1,
  "degrees": 15,
  "translate": 0.1,
  "scale": 0.1,
  "flipud": true,
  "fliplr": true,
  "num_samples": 5
}
```

**参数说明**:
- `degrees`: 旋转角度范围（度数）
- `translate`: 平移比例（0.0-1.0）
- `scale`: 缩放比例（0.0-1.0）
- `flipud`: 是否上下翻转
- `fliplr`: 是否左右翻转
- `num_samples`: 生成样本数量

**响应** (200):
```json
{
  "message": "数据增强完成",
  "augmented_images": [
    {"id": 1, "url": "/uploads/augmented/aug_1.png"},
    {"id": 2, "url": "/uploads/augmented/aug_2.png"}
  ],
  "total": 5
}
```

---

## 术前规划

### 手术模拟

```http
POST /api/preop/simulate
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_id": 1,
  "path": "surgical_path_001",
  "resection": 75
}
```

**参数说明**:
- `path`: 手术路径标识
- `resection`: 切除比例（%）

**响应** (200):
```json
{
  "message": "手术模拟完成",
  "prognosisRisk": "高",
  "difficulty": "高",
  "estimatedTime": 180,
  "recommendations": "建议采用显微神经外科技术，强化术中神经监测"
}
```

---

### 加载3D模型

```http
GET /api/preop/load3d?image_id=1
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "3D模型加载成功",
  "model_url": "/data/models/3d_model_1.obj",
  "texture_url": "/data/textures/texture_1.png"
}
```

---

## 影像组学

### 提取特征

```http
GET /api/radiomics/extract?image_id=1
Authorization: Bearer <token>
```

**响应** (200):
```json
[
  {"name": "GLCM_Contrast", "value": 0.42},
  {"name": "GLCM_Energy", "value": 0.56},
  {"name": "GLRLM_SRE", "value": 0.78},
  {"name": "GLRLM_LRE", "value": 0.34},
  {"name": "FirstOrder_Mean", "value": 128.3},
  {"name": "FirstOrder_Std", "value": 45.2},
  {"name": "FirstOrder_Median", "value": 130.0},
  {"name": "FirstOrder_Range", "value": 189.0}
]
```

---

### 训练模型

```http
POST /api/radiomics/train
Authorization: Bearer <token>
Content-Type: application/json

{
  "alg": "LogisticRegression",
  "label": "tumor_prognosis",
  "test_size": 0.2
}
```

**参数说明**:
- `alg`: 算法（LogisticRegression, RandomForest, SVM, GradientBoosting）
- `label`: 目标变量标签
- `test_size`: 测试集比例（0.0-1.0）

**响应** (200):
```json
{
  "message": "模型训练完成",
  "auc": 0.86,
  "acc": 0.81,
  "precision": 0.84,
  "recall": 0.78,
  "f1_score": 0.81,
  "training_time_s": 145.3,
  "model_path": "/models/radiomics_model_001.pkl"
}
```

---

## 分析与报告

### 获取分析指标

```http
GET /api/analysis/metrics?image_id=1
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "volume": 15342,
  "volume_unit": "mm³",
  "maxDiameter": 32.5,
  "maxDiameter_unit": "mm",
  "heterogeneity": 0.63,
  "texture_complexity": 0.58,
  "vascularization": 0.72
}
```

---

### 保存报告

```http
POST /api/analysis/report
Authorization: Bearer <token>
Content-Type: application/json

{
  "image_id": 1,
  "notes": "分割效果良好，建议手术治疗。肿瘤位置在运动皮层附近，需要术中神经导航。",
  "metrics": {
    "volume": 15342,
    "maxDiameter": 32.5,
    "heterogeneity": 0.63
  },
  "doctor_name": "李医生"
}
```

**响应** (201):
```json
{
  "message": "报告保存成功",
  "report_id": 1,
  "saved_at": "2026-01-04T09:30:00"
}
```

---

### 导出报告

```http
GET /api/analysis/export?image_id=1&fmt=pdf
Authorization: Bearer <token>
```

**查询参数**:
- `image_id`: 影像 ID
- `fmt`: 导出格式（pdf, docx, xlsx）

**响应** (200):
二进制 PDF 文件

**响应头**:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="report_1.pdf"
```

---

## 用户管理与系统

### 列出用户

```http
GET /api/admin/users?page=1&per_page=10&role=doctor
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码
- `per_page`: 每页数量
- `role`: 按角色过滤（admin, doctor, technician）
- `search`: 按用户名或邮箱搜索

**响应** (200):
```json
{
  "users": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin",
      "created_at": "2025-12-28T10:00:00",
      "last_login": "2026-01-04T08:30:00"
    },
    {
      "id": 2,
      "username": "doctor1",
      "email": "doctor1@hospital.com",
      "role": "doctor",
      "created_at": "2025-12-29T10:00:00",
      "last_login": "2026-01-04T07:45:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 5,
    "pages": 1
  }
}
```

---

### 创建用户

```http
POST /api/admin/users
Authorization: Bearer <token>
Content-Type: application/json

{
  "username": "doctor2",
  "email": "doctor2@hospital.com",
  "password": "TempPassword123",
  "role": "doctor"
}
```

**参数说明**:
- `role`: 用户角色（admin, doctor, technician, patient）

**响应** (201):
```json
{
  "message": "用户创建成功",
  "user": {
    "id": 3,
    "username": "doctor2",
    "email": "doctor2@hospital.com",
    "role": "doctor"
  }
}
```

**错误** (400):
```json
{
  "error": "用户名已存在"
}
```

---

### 获取单个用户

```http
GET /api/admin/users/{user_id}
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "user": {
    "id": 2,
    "username": "doctor1",
    "email": "doctor1@hospital.com",
    "role": "doctor",
    "created_at": "2025-12-29T10:00:00",
    "last_login": "2026-01-04T07:45:00",
    "department": "神经外科",
    "phone": "1234567890"
  }
}
```

---

### 更新用户

```http
PUT /api/admin/users/{user_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@hospital.com",
  "role": "admin",
  "department": "神经外科"
}
```

**响应** (200):
```json
{
  "message": "用户更新成功",
  "user": { ... }
}
```

---

### 删除用户

```http
DELETE /api/admin/users/{user_id}
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "用户删除成功"
}
```

---

### 获取模型信息 (新增)

```http
GET /api/admin/model
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "version": "YOLO11n",
  "framework": "ultralytics",
  "performance": {
    "accuracy": 0.89,
    "latency_ms": 245,
    "mAP50": 0.78,
    "mAP50_95": 0.65
  },
  "last_updated": "2025-12-28T10:30:00",
  "weights_path": "backend/yolov8n.pt",
  "total_parameters": 2601513,
  "device": "cuda"
}
```

---

### 更新模型 (新增)

```http
POST /api/admin/model/update
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "Model reloaded successfully",
  "version": "YOLO11n",
  "performance": { ... },
  "reload_time_s": 2.35
}
```

**错误** (500):
```json
{
  "error": "模型加载失败"
}
```

---

### 数据备份 (新增)

```http
POST /api/admin/backup
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "message": "Backup started",
  "backup_id": "backup_2026-01-04T09:00:00",
  "status": "in_progress",
  "estimated_duration_s": 180
}
```

---

### 系统监控 (新增)

```http
GET /api/admin/monitor
Authorization: Bearer <token>
```

**响应** (200):
```json
{
  "serverStatus": "healthy",
  "uptime_hours": 168.5,
  "storageUsage": 45.2,
  "storageTotal": "1TB",
  "apiCalls": 1234,
  "cpu_percent": 22.5,
  "memory_percent": 58.3,
  "memory_available_gb": 8.2,
  "database_status": "connected",
  "model_loaded": true
}
```

---

## 核心端点

### 健康检查

```http
GET /health
```

**响应** (200):
```json
{
  "status": "healthy"
}
```

---

### 肿瘤检测（快速接口）

```http
POST /detect
Authorization: Bearer <token>
Content-Type: application/json

{
  "image": "data:image/png;base64,iVBORw0KGgo..."
}
```

**响应** (200):
```json
{
  "detections": [
    {
      "class": "tumor",
      "confidence": 0.95,
      "bbox": [100, 150, 200, 250]
    }
  ],
  "count": 1
}
```

---

### 分割任务启动

```http
POST /segmentation/start
Content-Type: application/json

{
  "weightPath": "Yolov11_best.pt",
  "conf": 0.25
}
```

**响应** (200):
```json
{
  "job_id": "seg_job_001",
  "status": "pending",
  "created_at": "2026-01-04T09:00:00"
}
```

---

### 分割进度查询

```http
GET /segmentation/{job_id}/progress
```

**响应** (200):
```json
{
  "job_id": "seg_job_001",
  "status": "processing",
  "progress": 45,
  "current_step": "模型推理",
  "eta_seconds": 120
}
```

当任务完成时：

```json
{
  "job_id": "seg_job_001",
  "status": "completed",
  "progress": 100,
  "result": {
    "segmentation_mask": "data:image/png;base64,...",
    "tumor_volume": 15342.5
  }
}
```

---

## 错误处理

所有 API 错误遵循统一格式：

```json
{
  "error": "错误描述",
  "message": "人性化错误消息（可选）",
  "code": "ERROR_CODE"
}
```

### HTTP 状态码

| 状态码 | 含义         | 示例               |
| ------ | ------------ | ------------------ |
| 200    | 成功         | 正常请求           |
| 201    | 创建成功     | 上传影像、创建用户 |
| 400    | 请求参数错误 | 缺少必需参数       |
| 401    | 未授权       | Token 过期或无效   |
| 403    | 禁止访问     | 权限不足           |
| 404    | 资源不存在   | 影像不存在         |
| 500    | 服务器错误   | 模型加载失败       |

### 常见错误

**401 - 缺少或无效的 Token**:
```json
{
  "error": "Missing Authorization Header",
  "code": "MISSING_TOKEN"
}
```

**401 - Token 过期**:
```json
{
  "error": "Token has expired",
  "code": "TOKEN_EXPIRED"
}
```

**404 - 资源不存在**:
```json
{
  "error": "影像不存在",
  "code": "NOT_FOUND"
}
```

**500 - 模型错误**:
```json
{
  "error": "模型加载失败",
  "message": "无法找到权重文件",
  "code": "MODEL_ERROR"
}
```

---

## 使用示例

### JavaScript/TypeScript (Fetch API)

```javascript
// 登录
const loginResponse = await fetch('http://127.0.0.1:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'admin',
    password: 'admin123'
  })
});
const { access_token } = await loginResponse.json();

// 上传影像
const formData = new FormData();
formData.append('file', imageFile);
formData.append('patient_id', 'P001');

const uploadResponse = await fetch('http://127.0.0.1:8000/api/medical/upload', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`
  },
  body: formData
});
const uploadData = await uploadResponse.json();

// 分析影像
const analyzeResponse = await fetch(`http://127.0.0.1:8000/api/results/analyze/${uploadData.image_id}`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    conf: 0.25,
    weightPath: 'Yolov11_best.pt'
  })
});
const analysisResult = await analyzeResponse.json();
console.log('分析结果:', analysisResult);
```

### Python

```python
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

# 登录
login_response = requests.post(f'{BASE_URL}/api/auth/login', json={
    'username': 'admin',
    'password': 'admin123'
})
access_token = login_response.json()['access_token']
headers = {'Authorization': f'Bearer {access_token}'}

# 上传影像
with open('patient_scan.png', 'rb') as f:
    files = {'file': f}
    data = {'patient_id': 'P001', 'modality': 'MRI'}
    upload_response = requests.post(
        f'{BASE_URL}/api/medical/upload',
        headers=headers,
        files=files,
        data=data
    )
    image_id = upload_response.json()['image_id']

# 分析影像
analyze_response = requests.post(
    f'{BASE_URL}/api/results/analyze/{image_id}',
    headers=headers,
    json={'conf': 0.25, 'weightPath': 'Yolov11_best.pt'}
)
print('分析结果:', analyze_response.json())

# 获取仪表板数据
stats_response = requests.get(
    f'{BASE_URL}/api/dashboard/stats',
    headers=headers
)
print('统计数据:', stats_response.json())
```

### cURL

```bash
# 登录
TOKEN=$(curl -s -X POST 'http://127.0.0.1:8000/api/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"admin123"}' | jq -r '.access_token')

# 上传影像
curl -X POST 'http://127.0.0.1:8000/api/medical/upload' \
  -H "Authorization: Bearer $TOKEN" \
  -F 'file=@patient_scan.png' \
  -F 'patient_id=P001'

# 列出影像
curl -X GET 'http://127.0.0.1:8000/api/medical/list' \
  -H "Authorization: Bearer $TOKEN"

# 获取仪表板数据
curl -X GET 'http://127.0.0.1:8000/api/dashboard/stats' \
  -H "Authorization: Bearer $TOKEN"

# 获取模型信息
curl -X GET 'http://127.0.0.1:8000/api/admin/model' \
  -H "Authorization: Bearer $TOKEN"

# 系统监控
curl -X GET 'http://127.0.0.1:8000/api/admin/monitor' \
  -H "Authorization: Bearer $TOKEN"
```

---

## 版本历史

| 版本 | 日期       | 变更                            |
| ---- | ---------- | ------------------------------- |
| 1.0  | 2026-01-04 | 初版发布，包含 47 个 API 端点   |
|      |            | 补充 5 个缺失的管理员端点       |
|      |            | 固定前端上传端点 URL 不一致问题 |

---

## 开发注意事项

1. **Token 有效期**: JWT Token 有效期为 3600 秒，过期后需要重新登录
2. **文件上传**: 支持多种医学影像格式，建议压缩后上传以加快速度
3. **并发请求**: 建议使用连接池，避免频繁建立新连接
4. **错误处理**: 始终检查 HTTP 状态码，不要仅依赖响应体中的消息
5. **安全**: 生产环境应使用 HTTPS，妥善保管 JWT Token

---

## 联系与支持

- **文档维护**: 如发现 API 文档与实际不符，请提交问题
- **功能建议**: 欢迎提交新功能需求
- **Bug 报告**: 遇到 API 问题，请提供详细日志和重现步骤