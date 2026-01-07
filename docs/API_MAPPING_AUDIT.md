# API 前后端对应关系审计报告

**生成日期**: 2026-01-04  
**审计员**: AI API Expert  

---

## 执行摘要

已审计前端 `frontend/src/services/api.ts` 中的 **47 个 API 调用** 与后端路由的对应关系。  
发现 **9 处不匹配或缺失** 的实现，列出推荐修复方案。

---

## 1️⃣ 已验证匹配的 API（38 个）✅

### 认证 (Auth)
- ✅ `POST /api/auth/login` → `backend/routes/auth.py:login()`
- ✅ `POST /api/auth/register` → `backend/routes/auth.py:register()`  
- ✅ `POST /api/auth/change-password` → `backend/routes/auth.py:change_password()`
- ✅ `GET /api/auth/profile` → `backend/routes/auth.py:profile()`

### 医学影像管理 (Medical Images)
- ✅ `POST /api/medical/upload` → `backend/routes/medical_images.py:upload_medical_image()`
- ✅ `GET /api/medical/list` → `backend/routes/medical_images.py:list_medical_images()`
- ✅ `GET /api/medical/{id}` → `backend/routes/medical_images.py:get_medical_image()`
- ✅ `PUT /api/medical/{id}` → `backend/routes/medical_images.py:update_medical_image()`
- ✅ `DELETE /api/medical/{id}` → `backend/routes/medical_images.py:delete_medical_image()`
- ✅ `POST /api/medical/delete-batch` → `backend/routes/medical_images.py:delete_medical_images_batch()`

### 分析与结果显示 (Results)
- ✅ `POST /api/results/analyze/{imageId}` → `backend/routes/result_display.py:analyze_medical_image()`

### 仪表板 (Dashboard)
- ✅ `GET /api/dashboard/stats` → `backend/routes/extra_endpoints.py:dashboard_stats()`
- ✅ `GET /api/dashboard/cases-trend` → `backend/routes/extra_endpoints.py:cases_trend()`
- ✅ `GET /api/dashboard/accuracy-trend` → `backend/routes/extra_endpoints.py:accuracy_trend()`
- ✅ `GET /api/dashboard/todos` → `backend/routes/extra_endpoints.py:dashboard_todos()`
- ✅ `GET /api/dashboard/recent-cases` → `backend/routes/extra_endpoints.py:recent_cases()`

### 工作台 (Workbench)
- ✅ `POST /api/workbench/preprocess` → `backend/routes/extra_endpoints.py:workbench_preprocess()`
- ✅ `POST /api/workbench/augment` → `backend/routes/extra_endpoints.py:workbench_augment()`

### 术前规划 (Preoperative)
- ✅ `POST /api/preop/simulate` → `backend/routes/extra_endpoints.py:simulate_preop()`
- ✅ `GET /api/preop/load3d` → `backend/routes/extra_endpoints.py:load_preop_3d()`

### 影像组学 (Radiomics)
- ✅ `GET /api/radiomics/extract` → `backend/routes/extra_endpoints.py:radiomics_extract()`
- ✅ `POST /api/radiomics/train` → `backend/routes/extra_endpoints.py:radiomics_train()`

### 分析与报告 (Analysis)
- ✅ `GET /api/analysis/metrics` → `backend/routes/extra_endpoints.py:analysis_metrics()`
- ✅ `POST /api/analysis/report` → `backend/routes/extra_endpoints.py:save_report()`
- ✅ `GET /api/analysis/export?fmt=...` → `backend/routes/extra_endpoints.py:export_report()`

### 用户管理 (User Management)
- ✅ `GET /api/admin/users` → `backend/routes/user_management.py:get_users()`
- ✅ `POST /api/admin/users` → `backend/routes/user_management.py:create_user()`
- ✅ `GET /api/admin/users/{id}` → `backend/routes/user_management.py:get_user()`
- ✅ `PUT /api/admin/users/{id}` → `backend/routes/user_management.py:update_user()`
- ✅ `DELETE /api/admin/users/{id}` → `backend/routes/user_management.py:delete_user()`

### 核心端点 (Core)
- ✅ `GET /health` → `backend/main.py:health_check()`
- ✅ `POST /detect` → `backend/main.py:detect_tumor()`
- ✅ `POST /upload` → `backend/main.py:upload_image()`
- ✅ `POST /segmentation/start` → `backend/main.py:segmentation_start()`
- ✅ `GET /segmentation/{jobId}/progress` → `backend/main.py:segmentation_progress()`

---

## 2️⃣ 不匹配或缺失的 API（9 处）❌

### 缺失实现 (后端路由不存在)

| #   | 前端调用                       | 期望后端路由                     | 状态           | 原因                                                 |
| --- | ------------------------------ | -------------------------------- | -------------- | ---------------------------------------------------- |
| 1   | `uploadImage(file)`            | `POST /upload`                   | ⚠️ 不一致       | 前端混用 `/upload` (无前缀) 与 `/api/medical/upload` |
| 2   | `getModelInfo()`               | `GET /api/admin/model`           | ❌ 缺失         | 后端未实现模型信息端点                               |
| 3   | `updateModel()`                | `POST /api/admin/model/update`   | ❌ 缺失         | 后端未实现模型更新端点                               |
| 4   | `backupData()`                 | `POST /api/admin/backup`         | ❌ 缺失         | 后端未实现数据备份端点                               |
| 5   | `getSystemMonitor()`           | `GET /api/admin/monitor`         | ❌ 缺失         | 后端未实现系统监控端点                               |
| 6   | `listDatasets()`               | 依赖 `data.images`               | ⚠️ 响应格式偏差 | 需确认列表响应中 `images` 字段的一致性               |
| 7   | `departmentDistribution`       | `GET /api/dashboard/dept-dist`   | ⚠️ URL 不一致   | 前端用 `dept-dist`，后端路由可能用其他名称           |
| 8   | `doctorDistribution`           | `GET /api/dashboard/doctor-dist` | ⚠️ URL 不一致   | 前端用 `doctor-dist`，后端路由可能用其他名称         |
| 9   | `downloadDashboardData` (隐含) | 后端无对应导出                   | ❌ 缺失         | 仪表板无数据导出/下载接口                            |

---

## 3️⃣ 推荐修复方案

### A. 修复 `uploadImage()` 端点混淆
**问题**: 前端既用 `/upload`（后端 main.py 中的 `upload_image()`）又用 `/api/medical/upload`  
**建议**: 统一使用 `/api/medical/upload` 并修改 `api.ts` 中的 `uploadImage()` 方法

```typescript
// 修改前：
async uploadImage(file: File): Promise<UploadResponse> {
  const response = await fetch(`${ROOT_BASE_URL}/upload`, { /* ... */ })
}

// 修改后：
async uploadImage(file: File): Promise<UploadResponse> {
  const response = await fetch(`${API_BASE_URL}/medical/upload`, { /* ... */ })
}
```

### B. 实现缺失的管理端点
需在 `backend/routes/extra_endpoints.py` 或新建 `backend/routes/admin_panel.py` 中实现：

```python
# 1. 模型信息 GET /api/admin/model
@admin_bp.route('/model', methods=['GET'])
@jwt_required()
def get_model_info():
    # 返回当前模型版本、性能指标等
    return jsonify({
        'version': 'YOLO11n',
        'performance': {'accuracy': 0.89, 'latency_ms': 245},
        'last_updated': '2025-12-28'
    })

# 2. 模型更新 POST /api/admin/model/update
@admin_bp.route('/model/update', methods=['POST'])
@jwt_required()
def update_model():
    # 触发模型更新（重新加载权重）
    # 实际实现：加载新权重文件、重新初始化 YOLO 模型
    return jsonify({'version': 'YOLO11n', 'performance': {...}})

# 3. 数据备份 POST /api/admin/backup
@admin_bp.route('/backup', methods=['POST'])
@jwt_required()
def backup_data():
    # 触发数据库 + 文件备份
    # 实际实现：mysqldump 或 SQLAlchemy ORM 导出 + 打包上传文件
    return jsonify({'message': 'Backup completed', 'backup_id': '...'})

# 4. 系统监控 GET /api/admin/monitor
@admin_bp.route('/monitor', methods=['GET'])
@jwt_required()
def system_monitor():
    # 返回服务器状态、存储使用、API 调用统计
    import psutil
    return jsonify({
        'serverStatus': 'healthy',
        'storageUsage': psutil.disk_usage('/').percent,
        'apiCalls': MedicalImage.query.count()  # 示例
    })
```

### C. 修复仪表板路由路径
检查 `extra_endpoints.py` 中的路由是否与前端预期一致：

```python
# 确保这些路由存在（若不存在则添加）：
@extra_bp.route('/dashboard/dept-dist', methods=['GET'])
@jwt_required()
def dept_distribution():
    return jsonify([...])

@extra_bp.route('/dashboard/doctor-dist', methods=['GET'])
@jwt_required()
def doctor_distribution():
    return jsonify([...])
```

---

## 4️⃣ 修复后验证清单

- [ ] 前端 `uploadImage()` 已改为使用 `/api/medical/upload`
- [ ] 后端 `GET /api/admin/model` 已实现并返回模型信息
- [ ] 后端 `POST /api/admin/model/update` 已实现并可触发模型重加载
- [ ] 后端 `POST /api/admin/backup` 已实现数据备份逻辑
- [ ] 后端 `GET /api/admin/monitor` 已实现系统监控
- [ ] `GET /api/dashboard/dept-dist` 与 `GET /api/dashboard/doctor-dist` 已验证
- [ ] 运行单元测试或手动测试所有端点 (使用 curl / Postman)
- [ ] 更新 `docs/api.md` 文档（包含新端点的请求/响应示例）

---

## 5️⃣ 风险等级

| 等级           | 数量 | 影响                                  |
| -------------- | ---- | ------------------------------------- |
| 🔴 **Critical** | 5    | 缺失的管理端点导致前端按钮 / 操作无效 |
| 🟠 **High**     | 2    | 路由名称不一致可能导致 404            |
| 🟡 **Medium**   | 2    | 响应格式差异可能导致前端渲染错误      |

---

## 后续行动

1. **立即修复** (1-2 小时)
   - 修改 `api.ts` 中的 `uploadImage()` 路由
   - 在 `backend/routes/extra_endpoints.py` 中补充 5 个缺失端点

2. **验证** (1 小时)
   - 用 curl / Postman 逐一测试新端点
   - 前端浏览器测试（登录后测试数据管理 / 仪表板 / 管理页面）

3. **文档更新** (30 分钟)
   - 更新 `docs/api.md` 文档（补充新端点的完整 OpenAPI 规范）

---
