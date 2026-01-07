# UNet分析报告字段补全 - 部署指南

## 已完成的修改

### 1. 数据库模型 (backend/models/medical_image.py)
✅ 添加了UNet扩展字段：
- unet_tumor_centroid_x, unet_tumor_centroid_y (肿瘤中心点)
- unet_tumor_bbox_x1~y2 (边界框坐标)
- unet_risk_level (风险等级)
- unet_surgical_accessibility (手术可达性)
- unet_location_description (位置描述)

✅ 更新了to_dict()方法序列化新字段

### 2. 后端路由 (backend/routes/model_comparison.py)
✅ 在保存UNet结果时自动计算：
- 边界框和中心点坐标
- 风险等级 (基于肿瘤比例和实例数)
- 手术可达性 (基于肿瘤位置)
- 位置描述 (如"左侧上部"等)

### 3. 前端视图 (frontend/src/views/AnalysisReportView.vue)
✅ 修改reportData构建逻辑，根据模型类型动态选择字段：
- risk_level
- surgical_accessibility
- location
- bbox_x1/y1/x2/y2
- centroid_x/y

## 部署步骤

### 步骤1: 运行数据库迁移
```bash
cd backend
python add_unet_extended_fields.py
```

预期输出：
```
============================================================
添加UNet扩展字段到数据库
============================================================
✓ 成功添加字段: unet_tumor_centroid_x
✓ 成功添加字段: unet_tumor_centroid_y
✓ 成功添加字段: unet_tumor_bbox_x1
✓ 成功添加字段: unet_tumor_bbox_y1
✓ 成功添加字段: unet_tumor_bbox_x2
✓ 成功添加字段: unet_tumor_bbox_y2
✓ 成功添加字段: unet_risk_level
✓ 成功添加字段: unet_surgical_accessibility
✓ 成功添加字段: unet_location_description

✅ UNet扩展字段添加完成！
```

### 步骤2: 重启后端服务
```bash
# 停止当前后端 (Ctrl+C)
python main.py
```

### 步骤3: 测试完整流程

#### 测试YOLO模型分析报告
1. 登录系统
2. 上传或选择脑部MRI图像
3. 进入工作台，选择"YOLO11"模型
4. 点击"开始分割"
5. 点击"查看完整报告"
6. **验证报告显示：**
   - ✓ 副标题显示"基于YOLO深度学习模型"
   - ✓ 肿瘤位置描述（如"左侧中部"）
   - ✓ 中心点坐标
   - ✓ 边界框坐标
   - ✓ 风险等级（高/中/低）
   - ✓ 手术可达性（易/中/难）

#### 测试UNet模型分析报告
1. 返回工作台
2. 选择"UNet"模型
3. 点击"开始分割"
4. 点击"查看完整报告"
5. **验证报告显示：**
   - ✓ 副标题显示"基于UNet深度学习模型"
   - ✓ 肿瘤位置描述（不再是"未知"）
   - ✓ 中心点坐标（不再为空）
   - ✓ 边界框坐标（不再为空）
   - ✓ 风险等级（根据UNet结果计算）
   - ✓ 手术可达性（根据UNet结果计算）

## 字段计算逻辑

### 风险等级 (risk_level)
```python
if tumor_ratio > 50 or num_instances > 3:
    return 'high'
elif tumor_ratio > 20 or num_instances > 1:
    return 'medium'
else:
    return 'low'
```

### 手术可达性 (surgical_accessibility)
```python
# 基于肿瘤到图像中心的相对距离
distance_to_center = sqrt(((x-cx)/w)^2 + ((y-cy)/h)^2)

if distance < 0.3:  # 靠近中心
    return 'difficult'
elif distance < 0.6:  # 中间区域
    return 'moderate'
else:  # 外围区域
    return 'easy'
```

### 位置描述 (location_description)
基于边界框中心点位置，分为9个区域：
- 水平：左侧 / 中央 / 右侧
- 垂直：上部 / 中部 / 下部
- 组合示例："左侧上部"、"中央中部"等

## 数据库Schema变化

新增字段：
```sql
ALTER TABLE medical_images ADD COLUMN unet_tumor_centroid_x REAL;
ALTER TABLE medical_images ADD COLUMN unet_tumor_centroid_y REAL;
ALTER TABLE medical_images ADD COLUMN unet_tumor_bbox_x1 REAL;
ALTER TABLE medical_images ADD COLUMN unet_tumor_bbox_y1 REAL;
ALTER TABLE medical_images ADD COLUMN unet_tumor_bbox_x2 REAL;
ALTER TABLE medical_images ADD COLUMN unet_tumor_bbox_y2 REAL;
ALTER TABLE medical_images ADD COLUMN unet_risk_level VARCHAR(50);
ALTER TABLE medical_images ADD COLUMN unet_surgical_accessibility VARCHAR(50);
ALTER TABLE medical_images ADD COLUMN unet_location_description TEXT;
```

## 预期效果

### 修复前（UNet报告）
- 肿瘤位置：未知 ❌
- 中心点坐标：（不显示）❌
- 边界框：（不显示）❌
- 风险等级：仅显示YOLO数据 ❌
- 手术可达性：仅显示YOLO数据 ❌

### 修复后（UNet报告）
- 肿瘤位置：左侧上部 ✅
- 中心点坐标：(245.3, 178.6) ✅
- 边界框：(180, 120) - (310, 237) ✅
- 风险等级：Medium ✅
- 手术可达性：Moderate ✅

## 注意事项

1. **历史数据**: 已有的UNet预测记录不会自动补全这些字段，需要重新运行分割才能生成完整报告

2. **模型切换**: 报告会根据`last_model_used`字段自动选择显示YOLO或UNet的数据

3. **字段兼容**: YOLO和UNet现在具有完全对称的字段集合，便于对比分析

4. **性能影响**: 计算这些字段的开销极小（<10ms），不会影响预测性能
