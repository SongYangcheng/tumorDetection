# 前端组件文档

## 概述

前端采用Vue 3 + TypeScript + Vite构建的现代化单页应用。

## 技术栈

- **Vue 3**: 组合式API
- **TypeScript**: 类型安全
- **Vite**: 快速开发和构建
- **Vue Router**: 客户端路由
- **Pinia**: 状态管理

## 项目结构

```
frontend/src/
├── main.ts              # 应用入口
├── App.vue              # 根组件
├── router/              # 路由配置
│   └── index.ts
├── views/               # 页面组件
│   ├── HomeView.vue
│   ├── UploadView.vue
│   └── ResultsView.vue
├── services/            # API服务
│   └── api.ts
├── stores/              # 状态管理
│   └── counter.ts
└── components/          # 可复用组件 (待扩展)
```

## 路由配置

### 路由表

| 路径       | 组件        | 描述         |
| ---------- | ----------- | ------------ |
| `/`        | HomeView    | 应用首页     |
| `/upload`  | UploadView  | 图像上传页面 |
| `/results` | ResultsView | 检测结果展示 |

### 导航守卫

目前未配置导航守卫，可根据需要添加认证检查。

## 组件说明

### HomeView

**功能**: 应用首页，提供导航入口

**特性**:
- 欢迎信息展示
- 快速导航到上传页面

### UploadView

**功能**: 医学图像上传界面

**特性**:
- 文件选择器 (支持图像格式)
- 表单验证
- 上传进度显示
- 错误处理

**状态管理**:
- `selectedFile`: 选中的文件
- `uploading`: 上传状态
- `error`: 错误信息

### ResultsView

**功能**: 肿瘤检测结果展示

**特性**:
- 原始图像显示
- 检测框可视化
- 置信度信息
- 检测结果列表

**交互**:
- 重新上传按钮
- 结果导出 (待实现)

## API集成

### 服务层设计

`services/api.ts` 封装所有后端API调用：

```typescript
export const api = {
  uploadImage(file: File): Promise<UploadResponse>
  detectTumor(imageData: string): Promise<DetectResponse>
  healthCheck(): Promise<{status: string}>
}
```

### 类型定义

```typescript
interface DetectionResult {
  class: string
  confidence: number
  bbox: number[]
}

interface UploadResponse {
  message: string
  image: string
}

interface DetectResponse {
  detections: DetectionResult[]
  count: number
}
```

## 状态管理

### Pinia Store

目前使用示例store，可扩展为：

- 用户会话管理
- 上传历史记录
- 检测结果缓存
- UI状态管理

## 样式规范

### CSS框架

目前使用原生CSS，可考虑集成：
- Tailwind CSS
- Vuetify
- Element Plus

### 响应式设计

- 移动端适配
- 桌面端优化
- 图像自适应缩放

## 开发指南

### 组件开发

1. 使用组合式API (`<script setup>`)
2. 添加TypeScript类型
3. 遵循单文件组件模式
4. 使用scoped样式

### 新页面添加

1. 在 `views/` 创建组件
2. 在 `router/index.ts` 添加路由
3. 更新导航菜单

### API调用

1. 在 `services/api.ts` 添加方法
2. 定义请求/响应类型
3. 在组件中调用并处理结果

## 构建和部署

### 开发环境

```bash
npm run dev
```

### 生产构建

```bash
npm run build
npm run preview
```

### 环境变量

支持的环境变量：
- `VITE_API_BASE_URL`: API基础URL

## 性能优化

### 代码分割

- 路由级别的懒加载
- 第三方库按需导入

### 图像优化

- Base64编码显示
- 未来可添加压缩

### 缓存策略

- API响应缓存
- 静态资源缓存

## 测试策略

### 单元测试

- Vue组件测试 (Vitest)
- API服务测试

### E2E测试

- 用户流程测试 (Playwright/Cypress)

## 可访问性

- 语义化HTML
- 键盘导航支持
- 屏幕阅读器兼容
- 颜色对比度检查