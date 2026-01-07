# 系统架构和数据流说明

## 🏗️ 完整系统架构

```
┌────────────────────────────────────────────────────────────────┐
│                       用户浏览器                               │
│                  http://localhost:5173                         │
└────────────────────────┬─────────────────────────────────────┘
                         │
                    HTTP/REST API
                         │
        ┌────────────────▼──────────────────┐
        │      前端应用 (Vue 3 + TypeScript)  │
        │  ├─ LoginView          (认证)      │
        │  ├─ DashboardView      (仪表盘)    │
        │  ├─ UploadView         (上传)      │
        │  ├─ WorkbenchView      (工作台)    │
        │  ├─ PreOpPlanningView  (术前规划)  │
        │  ├─ RadiomicsView      (影像组学)  │
        │  └─ ... (其他视图)                 │
        └────────────────┬──────────────────┘
                         │
                     fetch() API
                         │
        ┌────────────────▼──────────────────────┐
        │  API 服务层                            │
        │  ├─ api.ts        (主 API 服务)       │
        │  └─ auth.ts       (认证服务)          │
        └────────────────┬──────────────────────┘
                         │
              http://127.0.0.1:8000/api
                         │
        ┌────────────────▼──────────────────────┐
        │   后端应用 (Flask 3.0.0)              │
        │   ├─ routes/auth.py      (认证)      │
        │   ├─ routes/medical_images.py (影像) │
        │   ├─ routes/result_display.py (结果) │
        │   ├─ routes/extra_endpoints.py (其他)│
        │   └─ middleware.py       (中间件)     │
        └────────────────┬──────────────────────┘
                         │
                   SQLAlchemy ORM
                   (models/*.py)
                         │
                    PyMySQL 驱动
                         │
        ┌────────────────▼──────────────────────┐
        │   MySQL 数据库                         │
        │   Host: localhost:3306                │
        │   Database: jieke                     │
        │   User: root                          │
        │                                        │
        │   表结构:                              │
        │   ├─ users          (用户表)         │
        │   ├─ medical_images (医学影像)       │
        │   ├─ ... (其他表)                    │
        └────────────────────────────────────┘
```

---

## 🔄 用户登录流程

```
1. 用户在浏览器输入用户名密码
   ↓
2. 前端 LoginView.vue 调用 authService.login()
   ↓
3. authService.login() 发送 POST /api/login 请求
   ↓
4. 后端 routes/auth.py 处理请求：
   - 验证用户名和密码
   - 检查用户是否存在于 MySQL users 表
   - 使用 bcrypt 验证密码
   ↓
5. 验证成功：
   - 使用 JWT 创建 access_token
   - 返回 token 和用户信息
   ↓
6. 前端接收响应：
   - 将 access_token 存储到 localStorage
   - 重定向到仪表盘
   ↓
7. 后续请求：
   - 所有 API 请求都包含 Authorization: Bearer {token}
   - 后端验证 token 有效性
```

---

## 📤 医学影像上传流程

```
1. 用户在 UploadView 选择文件
   ↓
2. 前端调用 api.uploadImage(file)
   ↓
3. 创建 FormData，包含文件数据
   ↓
4. 发送 POST /api/medical/upload 请求
   ↓
5. 后端 routes/medical_images.py 处理：
   - 验证文件类型和大小
   - 生成唯一文件名（UUID + 原始名称）
   - 保存文件到 uploads/medical_images/
   - 生成图片预览
   ↓
6. 在 MySQL medical_images 表中插入记录：
   - filename (保存的文件名)
   - original_filename (原始文件名)
   - filepath (文件路径)
   - file_size (文件大小)
   - mime_type (MIME 类型)
   - uploaded_at (上传时间)
   - uploaded_by (上传用户)
   ↓
7. 返回文件 ID 和预览 URL
   ↓
8. 前端显示上传成功和预览
```

---

## 🔍 肿瘤检测流程

```
1. 用户选择已上传的医学影像
   ↓
2. 前端调用 api.detectTumor(imageId)
   ↓
3. 后端 routes/extra_endpoints.py 处理：
   - 从数据库获取图像路径
   - 加载 YOLO11 模型
   - 对图像进行推理
   ↓
4. 模型返回检测结果：
   - 肿瘤位置 (bounding boxes)
   - 置信度分数
   - 分割掩码
   ↓
5. 后端将结果存储到 MySQL：
   - UPDATE medical_images SET:
     - tumor_detected (是否检测到肿瘤)
     - confidence_score (置信度)
     - detection_results (检测结果 JSON)
     - segmentation_mask_path (分割掩码路径)
   ↓
6. 返回检测结果到前端
   ↓
7. 前端在 WorkbenchView 显示结果和可视化
```

---

## 📊 仪表盘数据流

```
1. 用户打开 DashboardView
   ↓
2. 前端调用多个 API 方法：
   - api.getDashboardStats()        → /api/dashboard/stats
   - api.getCasesTrend()            → /api/dashboard/cases-trend
   - api.getAccuracyTrend()         → /api/dashboard/accuracy-trend
   - api.getDepartmentDistribution() → /api/dashboard/dept-dist
   - api.getDoctorDistribution()    → /api/dashboard/doctor-dist
   - api.getRecentCases()           → /api/dashboard/recent-cases
   - api.getSystemMonitor()         → /api/admin/monitor
   - api.getModelInfo()             → /api/admin/model
   - api.getTodos()                 → /api/dashboard/todos
   ↓
3. 后端处理各个请求：
   - SQL 查询 medical_images 表
   - 统计肿瘤检测数量
   - 计算检测准确率
   - 按科室分组统计
   - 按医生分组统计
   - 获取最近的 10 个病例
   - 获取系统监控信息
   - 获取模型信息
   ↓
4. MySQL 返回查询结果
   ↓
5. 后端返回 JSON 格式数据
   ↓
6. 前端使用 Chart.vue 组件可视化：
   - 统计卡片显示数据
   - 折线图显示趋势
   - 柱状图显示分布
   - 表格显示列表
```

---

## 🔐 认证和授权机制

### Token 生命周期

```
1. 用户登录
   ↓
2. 后端生成 JWT Token（有效期 3600 秒）
   ```python
   access_token = create_access_token(identity=str(user.id))
   ```
   ↓
3. 前端存储 Token
   ```javascript
   localStorage.setItem('access_token', access_token)
   ```
   ↓
4. 每个请求都发送 Token
   ```
   Authorization: Bearer eyJhbGci...
   ```
   ↓
5. 后端验证 Token
   ```python
   @jwt_required()
   def protected_route():
       current_user_id = get_jwt_identity()
   ```
   ↓
6. Token 过期
   - 后端返回 401 Unauthorized
   - 前端重定向到登录页
   - 用户需要重新登录
```

### 权限检查

```
后端中间件检查：
1. Token 是否有效
2. Token 是否过期
3. 用户是否存在
4. 用户是否被激活
5. 用户是否有权限访问资源
```

---

## 🗄️ MySQL 数据库表关系

```
users 表
├─ id (主键)
├─ username (唯一)
├─ email (唯一)
├─ password_hash (加密)
├─ is_admin (权限)
├─ is_active (状态)
└─ created_at (时间戳)
    ↓
    ├→ medical_images.uploaded_by (外键)
    └→ ... (其他关联)

medical_images 表
├─ id (主键)
├─ filename (文件名)
├─ original_filename (原始名称)
├─ filepath (存储路径)
├─ file_size (文件大小)
├─ mime_type (文件类型)
├─ patient_id (患者 ID)
├─ scan_date (扫描日期)
├─ modality (影像模态)
├─ patient_name (患者名)
├─ age (年龄)
├─ gender (性别)
├─ diagnosis (诊断)
├─ detection_results (检测结果 JSON)
├─ tumor_detected (是否检测到肿瘤)
├─ confidence_score (置信度)
├─ segmentation_mask_path (分割掩码)
├─ tumor_volume (肿瘤体积)
├─ tumor_area (肿瘤面积)
├─ max_diameter (最大直径)
├─ radiomics_features (影像组学特征 JSON)
├─ surgical_plan (手术规划 JSON)
├─ uploaded_by (上传者 ID，外键)
├─ uploaded_at (上传时间)
└─ updated_at (更新时间)
```

---

## 🔗 API 端点映射

### 认证相关

```
POST   /api/login                    → 用户登录
POST   /api/register                 → 用户注册
GET    /api/profile                  → 获取个人信息
POST   /api/change-password          → 修改密码
```

### 医学影像管理

```
POST   /api/medical/upload           → 上传医学影像
GET    /api/medical/{id}             → 获取单个影像信息
GET    /api/medical/list             → 获取影像列表
```

### 肿瘤检测和分割

```
POST   /detect                        → 进行肿瘤检测
POST   /api/results/analyze/{id}     → 分析影像
```

### 术前规划

```
POST   /api/preop/simulate           → 术前规划模拟
GET    /api/preop/load3d             → 加载 3D 模型
```

### 影像组学

```
POST   /api/radiomics/extract        → 提取影像组学特征
POST   /api/radiomics/train          → 训练分类模型
```

### 工作台

```
POST   /api/workbench/preprocess     → 数据预处理
POST   /api/workbench/augment        → 数据增强
```

### 仪表盘和管理

```
GET    /api/dashboard/stats          → 获取统计数据
GET    /api/dashboard/cases-trend    → 获取病例趋势
GET    /api/dashboard/accuracy-trend → 获取准确率趋势
GET    /api/dashboard/dept-dist      → 获取科室分布
GET    /api/dashboard/doctor-dist    → 获取医生分布
GET    /api/dashboard/recent-cases   → 获取最近病例
GET    /api/dashboard/todos          → 获取 TODO 列表
GET    /api/admin/monitor            → 系统监控信息
GET    /api/admin/model              → 获取模型信息
POST   /api/admin/model/update       → 更新模型
```

---

## 📡 HTTP 请求示例

### 登录请求

```
POST /api/login HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

// 响应
HTTP/1.1 200 OK
{
  "message": "登录成功",
  "access_token": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "is_admin": true
  }
}
```

### 获取仪表盘统计

```
GET /api/dashboard/stats HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGci...

// 响应
HTTP/1.1 200 OK
{
  "totalCases": 100,
  "detectedTumors": 45,
  "totalImages": 250,
  "averageAccuracy": 0.92
}
```

### 上传医学影像

```
POST /api/medical/upload HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer eyJhbGci...
Content-Type: multipart/form-data

[文件二进制数据]

// 响应
HTTP/1.1 201 Created
{
  "message": "文件上传成功",
  "image_id": "uuid-123-456",
  "file_url": "http://127.0.0.1:8000/uploads/...",
  "preview_url": "http://127.0.0.1:8000/uploads/..._preview.png"
}
```

---

## ⚡ 性能考虑

### 前端优化

- ✅ 使用 Vite 快速热更新
- ✅ Vue 3 响应式系统高效更新
- ✅ localStorage 缓存 Token，减少登录请求

### 后端优化

- ✅ Flask 应用使用 blueprints 组织代码
- ✅ SQLAlchemy ORM 管理数据库连接
- ✅ YOLO11 模型使用 GPU 加速推理（可选）

### 数据库优化

- ✅ MySQL 索引优化查询性能
- ✅ 连接池管理数据库连接
- ✅ 存储 JSON 数据在 TEXT 字段中

---

## 🔒 安全措施

- ✅ JWT Token 认证所有 API
- ✅ 密码使用 bcrypt 加密
- ✅ CORS 跨域请求保护
- ✅ SQL 注入防护（使用 ORM）
- ✅ 输入验证和清理

---

## 📝 总结

系统架构完整，前端正确与 MySQL 后端通信：

1. **前端**: Vue 3 应用通过 fetch API 调用 RESTful 接口
2. **后端**: Flask 应用使用 SQLAlchemy 与 MySQL 通信
3. **数据库**: MySQL 存储所有业务数据
4. **认证**: JWT Token 保护所有 API
5. **数据流**: 清晰的单向数据流确保系统的可维护性

**系统已准备好使用！** 🎉
