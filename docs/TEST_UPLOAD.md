# 数据上传与显示测试指南

## 已完成的更新

### 后端更新
1. 数据库添加了 `status` 字段（new/processing/completed）
2. 模型的 `to_dict()` 方法包含所有必要字段
3. ✅ 上传API接收 `patient_name` 和 `scan_date` 参数

### 前端更新
1. ✅ 上传表单添加了必填字段：
   - 患者ID *
   - 患者姓名 *
   - 影像类型 *
   - 扫描日期 *
   - 备注（可选）

2. ✅ API调用正确传递所有字段
3. ✅ 数据列表正确映射和显示所有字段

## 📋 测试步骤

### 1. 启动后端服务
```bash
cd backend
python main.py
```

### 2. 启动前端服务
```bash
cd frontend
npm run dev
```

### 3. 测试上传功能
1. 登录系统
2. 进入"数据管理"页面
3. 点击"上传新病例"按钮
4. 填写完整信息：
   - 患者ID: 例如 `P001`
   - 患者姓名: 例如 `张三`
   - 影像类型: 选择 `MRI`
   - 扫描日期: 选择日期
   - 备注: 可选填写
5. 选择或拖拽医学影像文件
6. 点击"开始上传"

### 4. 验证显示
上传成功后，在数据列表中应该看到：
- 病例ID（自动生成）
- ✅ 患者信息（显示姓名和ID）
- ✅ 影像类型（MRI/CT/PET等）
- ✅ 扫描日期（您输入的日期）
- ✅ 状态（显示"新建"）
- ✅ 操作按钮（分析、删除）

## 🔍 字段映射关系

| 前端表单 | 后端字段     | 数据库字段   | 显示列   |
| -------- | ------------ | ------------ | -------- |
| 患者ID   | patient_id   | patient_id   | 患者信息 |
| 患者姓名 | patient_name | patient_name | 患者信息 |
| 影像类型 | modality     | modality     | 影像类型 |
| 扫描日期 | scan_date    | scan_date    | 扫描日期 |
| 备注     | diagnosis    | diagnosis    | -        |
| -        | status       | status       | 状态     |
| -        | id           | id           | 病例ID   |

## 🐛 如果数据不显示

### 检查后端日志
```bash
# 查看上传请求的日志
# 确认是否收到所有字段
```

### 检查浏览器控制台
```javascript
// 打开开发者工具，查看Network标签
// 检查 /api/medical/upload 请求
// 检查 /api/medical/list 响应
```

### 手动验证数据库
```python
# 进入Python shell
from backend.main import create_app
from backend.models import db
from backend.models.medical_image import MedicalImage

app = create_app()
with app.app_context():
    images = MedicalImage.query.all()
    for img in images:
        print(f"ID: {img.id}, 患者: {img.patient_name}, 状态: {img.status}")
```

## 📝 状态说明

| 状态值     | 显示文本 | 说明           |
| ---------- | -------- | -------------- |
| new        | 新建     | 刚上传的病例   |
| processing | 处理中   | 正在进行AI分析 |
| completed  | 已完成   | 分析完成       |

## ✨ 下一步

- 在"处理与分割"页面中，点击"开始分析"后，状态会更新为"处理中"
- 分析完成后，状态会更新为"已完成"
- 可以在"结果查看"页面查看详细的检测结果
