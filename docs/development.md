# 开发指南

## 环境要求

### 系统要求
- **操作系统**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.8 或更高版本
- **Node.js**: 18.0 或更高版本
- **Git**: 2.0 或更高版本

### 硬件要求
- **内存**: 至少8GB RAM
- **存储**: 至少10GB可用空间
- **GPU**: NVIDIA GPU (可选，用于模型训练)

## 开发环境搭建

### 1. 克隆项目

```bash
git clone <repository-url>
cd tumorDetection
```

### 2. 后端环境配置

```bash
# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 3. 前端环境配置

```bash
cd frontend
npm install
```

### 4. 验证安装

```bash
# 后端
python backend/main.py

# 前端 (新终端)
cd frontend
npm run dev
```

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/your-feature-name
```

### 2. 代码开发

遵循以下原则：
- 使用有意义的提交信息
- 保持代码简洁和可读
- 添加必要的注释
- 编写测试代码

### 3. 代码检查

```bash
# 前端类型检查
cd frontend
npm run type-check

# 前端构建检查
npm run build
```

### 4. 提交代码

```bash
git add .
git commit -m "feat: 添加新功能描述"
git push origin feature/your-feature-name
```

### 5. 创建Pull Request

在GitHub上创建PR，等待代码审查。

## 代码规范

### Python (后端)

#### 命名规范
- **变量和函数**: snake_case
- **类**: PascalCase
- **常量**: UPPER_CASE

#### 代码风格
- 使用Black格式化代码
- 使用isort整理导入
- 遵循PEP 8标准

#### 示例
```python
# 正确
def process_image(image_path: str) -> dict:
    """处理医学图像"""
    pass

# 错误
def processimage(imagepath):
    pass
```

### TypeScript/JavaScript (前端)

#### 命名规范
- **变量和函数**: camelCase
- **组件**: PascalCase
- **文件**: kebab-case

#### 代码风格
- 使用ESLint和Prettier
- 使用TypeScript严格模式
- 遵循Vue风格指南

#### 示例
```typescript
// 正确
const handleFileUpload = (file: File) => {
  // 处理文件上传
}

// 错误
const handlefileupload = (file) => {
  // 处理文件上传
}
```

## 项目结构规范

### 后端文件组织

```
backend/
├── main.py              # 应用入口
├── models/              # 模型文件
├── utils/               # 工具函数
├── tests/               # 测试文件
└── config.py            # 配置文件 (未来)
```

### 前端文件组织

```
frontend/src/
├── components/          # 可复用组件
├── views/               # 页面组件
├── services/            # API服务
├── stores/              # 状态管理
├── utils/               # 工具函数
├── types/               # 类型定义
└── assets/              # 静态资源
```

## 测试策略

### 后端测试

```bash
# 运行单元测试
python -m pytest backend/tests/

# 运行覆盖率测试
python -m pytest --cov=backend
```

### 前端测试

```bash
# 运行单元测试
npm run test

# 运行E2E测试
npm run test:e2e
```

## 调试技巧

### 后端调试

- 使用Flask调试模式
- 使用print语句或logging
- 使用PDB调试器

```python
# 在代码中添加断点
import pdb; pdb.set_trace()
```

### 前端调试

- 使用Vue DevTools
- 使用浏览器开发者工具
- 使用console.log调试

## 常见问题

### 后端问题

**问题**: 模型加载失败
**解决**: 检查模型文件路径，确保文件存在

**问题**: 端口被占用
**解决**: 修改main.py中的端口号或释放端口

### 前端问题

**问题**: 热重载不工作
**解决**: 重启开发服务器

**问题**: API调用失败
**解决**: 检查后端服务是否运行，检查网络连接

## 性能优化

### 后端优化

- 使用异步处理
- 实现缓存机制
- 优化数据库查询

### 前端优化

- 代码分割
- 懒加载组件
- 优化图片加载

## 安全注意事项

- 不要提交敏感信息到版本控制
- 使用环境变量管理配置
- 定期更新依赖包
- 实施输入验证
- 使用HTTPS传输

## 学习资源

- [Flask官方文档](https://flask.palletsprojects.com/)
- [Vue.js官方文档](https://vuejs.org/)
- [YOLO文档](https://docs.ultralytics.com/)
- [TypeScript手册](https://www.typescriptlang.org/)