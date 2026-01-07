# 分析报告功能 - 快速参考

## ✅ 已修复的问题

### 问题：点击侧边栏"分析报告"无法访问正确页面
- **原因**：侧边栏链接指向 `/analysis`，但该路径被重定向到了 `/dashboard`
- **解决**：移除了侧边栏的"分析报告"菜单项，因为分析报告需要imageId参数，应通过工作流访问

---

## 🎯 正确的使用流程

### 完整步骤
```
1. 数据管理 (/data)
   ↓ 上传影像 → 选择影像 → 点击"开始分析"
   
2. 处理与分割 (/workbench?imageId=xxx)
   ↓ 配置参数 → 开始分割 → 查看详细信息
   
3. 分析报告 (/analysis-report?imageId=xxx)
   ↓ 点击"查看完整报告" → 查看/导出/打印报告
```

### 快速开始
```bash
# 1️⃣ 在数据管理页面
1. 点击"数据管理"菜单
2. 上传脑部MRI影像
3. 选择影像，点击"开始分析"

# 2️⃣ 在处理与分割页面
1. 自动加载影像
2. 调整置信度阈值（可选）
3. 点击"开始分割"
4. 等待完成，查看肿瘤详细信息

# 3️⃣ 查看完整报告
1. 点击"查看完整报告"按钮
2. 在分析报告页面查看所有信息
3. 可以导出PDF或打印
```

---

## 🔗 路由说明

### 可访问的路由
| 路径                           | 说明                 | 访问方式                     |
| ------------------------------ | -------------------- | ---------------------------- |
| `/data`                        | 数据管理             | 侧边栏菜单                   |
| `/workbench`                   | 处理与分割           | 侧边栏菜单 或 从数据管理跳转 |
| `/workbench?imageId=123`       | 处理与分割（带参数） | 从数据管理跳转               |
| `/analysis-report?imageId=123` | 分析报告             | 从处理与分割跳转             |

### 重定向路由
| 路径         | 重定向到           | 说明                   |
| ------------ | ------------------ | ---------------------- |
| `/analysis`  | `/data`            | 引导用户从数据管理开始 |
| `/radiomics` | `/video-detection` | 影像组学指向视频检测   |

---

## 🎨 关键组件说明

### WorkbenchView（处理与分割）
**功能**：
- 加载影像并执行分割
- 显示分割结果
- 展示肿瘤详细信息
- 提供跳转到分析报告的按钮

**关键代码**：
```vue
<button @click="viewAnalysisReport">查看完整报告</button>

const viewAnalysisReport = () => {
  router.push({ path: '/analysis-report', query: { imageId: imageId.value } })
}
```

### AnalysisReportView（分析报告）
**功能**：
- 从URL参数获取imageId
- 加载影像信息和YOLO检测结果
- 展示完整的医疗报告
- 支持导出PDF和打印

**关键代码**：
```vue
const imageId = route.query.imageId as string
const imageInfo = await api.getMedicalImage(imageId)
const yoloResults = await api.getYoloDetectionResults(parseInt(imageId))
```

### DataManagerView（数据管理）
**功能**：
- 上传和管理影像
- 选择影像后跳转到处理页面

**关键代码**：
```vue
const goAnalyze = (d: Dataset) => {
  router.push({ path: '/workbench', query: { imageId: String(d.id) } })
}
```

---

## 📊 数据流

### 参数传递
```
DataManagerView
  └─> imageId (通过 router.push query)
        └─> WorkbenchView
              └─> imageId (通过 router.push query)
                    └─> AnalysisReportView
```

### API调用
```
WorkbenchView:
  api.analyzeImage(imageId, conf, weightPath)
    └─> 返回分割结果和肿瘤信息

AnalysisReportView:
  api.getMedicalImage(imageId)
    └─> 返回影像基础信息
  
  api.getYoloDetectionResults(imageId)
    └─> 返回完整检测结果
```

---

## ⚠️ 注意事项

### 1. 必须按流程操作
- ❌ 不能直接访问 `/analysis-report`（没有imageId会加载失败）
- ❌ 不能跳过"开始分割"步骤（没有检测结果）
- ✅ 必须完整走流程：上传 → 分割 → 报告

### 2. imageId参数必需
```typescript
// ✅ 正确
router.push({ path: '/analysis-report', query: { imageId: '123' } })

// ❌ 错误
router.push({ path: '/analysis-report' })  // 缺少imageId
```

### 3. 后端依赖
- 必须先运行YOLO检测才能查看报告
- 后端接口 `/api/yolo/results/{imageId}` 必须返回有效数据

---

## 🔧 调试技巧

### 检查imageId是否传递
```javascript
// 在 WorkbenchView 中
console.log('imageId:', imageId.value)

// 在 AnalysisReportView 中
console.log('imageId from route:', route.query.imageId)
```

### 检查API响应
```javascript
// 在浏览器控制台查看
const response = await api.getYoloDetectionResults(123)
console.log('YOLO结果:', response)
```

### 检查路由跳转
```javascript
// 查看当前路由
console.log('当前路径:', route.path)
console.log('查询参数:', route.query)
```

---

## 📝 更新记录

### 2026-01-04
- ✅ 修复侧边栏"分析报告"链接问题
- ✅ 移除独立的"分析报告"菜单项
- ✅ 更新 `/analysis` 路由重定向到 `/data`
- ✅ 完善整个数据流程
- ✅ 创建测试文档和快速参考

---

## 🚀 快速测试

### 5分钟完整测试
```bash
1. 登录系统 (admin/admin123)
2. 点击"数据管理" [预计 10秒]
3. 上传一张MRI影像 [预计 30秒]
4. 选择影像，点击"开始分析" [预计 5秒]
5. 在处理页面点击"开始分割" [预计 2分钟]
6. 查看肿瘤详细信息 [预计 30秒]
7. 点击"查看完整报告" [预计 5秒]
8. 浏览完整报告内容 [预计 1分钟]
```

**预期结果**：所有步骤顺利完成，能够看到完整的分析报告 ✅

---

**文档版本**: v1.0  
**更新日期**: 2026年1月4日
