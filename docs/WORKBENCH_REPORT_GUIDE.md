# 处理与分割 + 分析报告功能使用指南

## 功能概览

本次更新完善了**处理与分割页面（WorkbenchView）**和新增了**分析报告页面（AnalysisReportView）**，提供完整的肿瘤检测、分析和报告生成流程。

---

## 一、处理与分割页面增强

### 新增功能

#### 1. 肿瘤详细信息展示
分割完成后，页面会自动显示：

- **检测状态**：是否发现肿瘤
- **肿瘤实例数**：检测到的肿瘤数量
- **肿瘤面积占比**：肿瘤占影像总面积的百分比
- **平均置信度**：模型预测的平均置信度
- **风险等级**：low（低风险）、medium（中风险）、high（高风险）
- **手术可达性**：easy（易接近）、moderate（中等）、difficult（困难）
- **肿瘤位置**：描述肿瘤在脑组织中的位置

#### 2. 肿瘤实例详情
如果检测到多个肿瘤实例，会显示每个实例的：
- 实例ID
- 置信度
- 面积（像素²）
- 边界框坐标

#### 3. 查看完整报告按钮
点击"查看完整报告"按钮，跳转到专业的分析报告页面。

### 使用流程

```
1. 从数据管理页面选择影像 → 跳转到处理与分割页面
2. 配置分割参数（置信度阈值、模型权重路径）
3. 点击"开始分割"
4. 等待分割完成，查看分割结果图像
5. 查看下方的肿瘤详细信息面板
6. 点击"查看完整报告"生成专业报告
```

---

## 二、分析报告页面（全新）

### 报告结构

#### 1. 报告头部
- 报告标题和副标题
- 导出PDF按钮
- 打印报告按钮

#### 2. 患者信息
- 患者ID
- 患者姓名
- 影像类型
- 扫描日期
- 上传时间
- 检测时间

#### 3. 检测结果总览
以卡片形式展示：
- 检测状态
- 肿瘤实例数
- 面积占比
- 平均置信度

#### 4. 影像对比
并排显示：
- 原始影像
- 分割结果（带肿瘤标记）

#### 5. 肿瘤详细信息
- 肿瘤位置
- 肿瘤像素数
- 总像素数
- 中心坐标
- 边界框坐标
- 推理时间
- 模型版本
- 分割质量
- 肿瘤实例详情表格

#### 6. 风险评估
两个评估卡片：
- **风险等级**：显示风险进度条和描述
- **手术可达性**：显示可达性指示灯和描述

#### 7. 诊断建议
- 检测结果描述
- 肿瘤特征分析
- 风险评估说明
- 医疗建议
- 免责声明

#### 8. 报告签名
- 生成时间
- 系统版本
- 使用模型

### 使用流程

```
1. 在处理与分割页面完成分割后，点击"查看完整报告"
2. 自动跳转到分析报告页面，带上影像ID参数
3. 系统自动加载影像信息和YOLO检测结果
4. 查看完整的分析报告
5. 可以导出PDF或打印报告
```

### 路由访问

直接访问：`/analysis-report?imageId=<影像ID>`

---

## 三、API接口说明

### 1. 获取YOLO检测结果

```typescript
// 方法1
const result = await api.getYoloResults(imageId)

// 方法2（别名，用于分析报告）
const result = await api.getYoloDetectionResults(imageId)
```

**返回数据结构**：
```typescript
{
  success: boolean
  data: {
    image_id: number
    has_tumor: boolean
    num_instances: number
    avg_confidence: number
    tumor_ratio: number
    tumor_pixels: number
    total_pixels: number
    risk_level: 'low' | 'medium' | 'high'
    surgical_accessibility: 'easy' | 'moderate' | 'difficult'
    location: string
    centroid: { x: number, y: number }
    bbox: { x1: number, y1: number, x2: number, y2: number }
    mask_url: string
    overlay_url: string
    instances: YoloInstance[]
    segmentation_quality: number
    model_version: string
    inference_time: number
    diagnostic_report: YoloDiagnosticReport
    detection_time: string
  }
}
```

### 2. 获取医学影像信息

```typescript
const imageInfo = await api.getMedicalImage(imageId)
```

---

## 四、风险等级说明

### 低风险（Low）
- **特征**：肿瘤面积 ≤ 20% 且实例数 ≤ 1
- **颜色**：绿色
- **建议**：定期复查监测

### 中风险（Medium）
- **特征**：20% < 肿瘤面积 ≤ 50% 或实例数 = 2-3
- **颜色**：橙色
- **建议**：尽快就医评估

### 高风险（High）
- **特征**：肿瘤面积 > 50% 或实例数 > 3
- **颜色**：红色
- **建议**：立即就医进行专业评估

---

## 五、手术可达性说明

### 易接近（Easy）
- **位置**：外围区域
- **距离中心**：> 60%
- **手术难度**：较低

### 中等（Moderate）
- **位置**：中间区域
- **距离中心**：30%-60%
- **手术难度**：中等

### 困难（Difficult）
- **位置**：深部或功能区
- **距离中心**：< 30%
- **手术难度**：较高，需专业团队

---

## 六、注意事项

### 1. 数据流程
```
数据管理 → 处理与分割 → 分析报告
```

必须先在**处理与分割页面**运行分割，才能在**分析报告页面**查看完整数据。

### 2. 权限要求
所有页面都需要登录认证（`requiresAuth: true`）

### 3. 后端依赖
分析报告依赖后端YOLO检测结果：
- 后端接口：`/api/yolo/results/{image_id}`
- 确保后端已运行YOLO检测

### 4. 打印和导出
- **打印**：调用浏览器原生打印功能 `window.print()`
- **导出PDF**：同样使用浏览器打印，选择"保存为PDF"

### 5. 免责声明
报告自动包含免责声明：
> 本报告由AI辅助诊断系统生成，仅供医学参考，不能替代专业医师的临床判断。

---

## 七、样式特性

### 响应式设计
- 桌面端：双列布局
- 平板/移动端：单列堆叠布局

### 颜色主题
- 主色调：`var(--primary)`（蓝色）
- 成功/低风险：绿色 `#10B981`
- 警告/中风险：橙色 `#F59E0B`
- 危险/高风险：红色 `#EF4444`

### 动画效果
- 卡片悬停效果
- 按钮提升效果
- 加载旋转动画
- 指示灯脉冲动画

---

## 八、开发扩展

### 添加新的报告章节

在 `AnalysisReportView.vue` 中添加新的 `<section>` 块：

```vue
<section class="report-section custom-section">
  <div class="section-header">
    <div class="section-icon" style="background: #E0F2FE;">
      <svg><!-- 图标 --></svg>
    </div>
    <h2 class="section-title">自定义章节</h2>
  </div>
  <!-- 内容 -->
</section>
```

### 自定义风险评级算法

修改 `backend/routes/yolo_detection.py` 中的 `calculate_risk_level` 函数。

### 添加新的肿瘤指标

1. 在后端添加字段到 `MedicalImage` 模型
2. 在 `api.ts` 的类型定义中添加字段
3. 在 `AnalysisReportView.vue` 中展示新字段

---

## 九、故障排查

### 问题1：分析报告显示"加载失败"

**原因**：
- 影像ID无效
- 后端未运行YOLO检测

**解决**：
1. 确保从处理与分割页面跳转
2. 先在处理与分割页面运行分割
3. 检查后端API是否正常

### 问题2：肿瘤详细信息未显示

**原因**：
- 分割结果数据不完整
- API响应格式不匹配

**解决**：
1. 检查 `api.analyzeImage` 返回的数据结构
2. 确保包含 `has_tumor`, `num_instances` 等字段
3. 查看浏览器控制台错误信息

### 问题3：导出PDF失败

**原因**：
- 浏览器打印功能被阻止
- 页面样式未加载完成

**解决**：
1. 允许浏览器弹出窗口
2. 等待页面完全加载后再导出
3. 使用Chrome/Edge浏览器以获得最佳支持

---

## 十、总结

本次更新实现了：
✅ 处理与分割页面增强：实时显示肿瘤详细信息  
✅ 分析报告页面创建：专业的医疗报告展示  
✅ API服务完善：支持获取完整检测结果  
✅ 路由配置更新：正确导航到分析报告  

使用流程简洁明了，从数据管理 → 处理与分割 → 分析报告，一气呵成！
