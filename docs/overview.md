# 项目概述

## tumorDetection

基于YOLO11影像组学的脑部肿瘤精准分割与术前规划系统的设计与实现。

## 功能特性

- **肿瘤检测**: 使用YOLO11深度学习模型进行脑部肿瘤自动检测
- **图像分割**: 提供精准的肿瘤区域分割
- **术前规划**: 支持手术规划和决策辅助
- **Web界面**: 现代化的Vue.js前端界面
- **REST API**: 完整的后端API接口

## 技术栈

### 后端
- **Python 3.8+**
- **Flask**: Web框架
- **YOLO11 (Ultralytics)**: 目标检测模型
- **PyTorch**: 深度学习框架
- **Pillow**: 图像处理

### 前端
- **Vue 3**: 渐进式JavaScript框架
- **TypeScript**: 类型安全的JavaScript
- **Vite**: 快速构建工具
- **Vue Router**: 单页应用路由
- **Pinia**: 状态管理

### 开发工具
- **Git**: 版本控制
- **VS Code**: 推荐IDE
- **Docker**: 容器化部署

## 项目结构

```
tumorDetection/
├── backend/                 # Python后端
│   ├── main.py             # Flask应用入口
│   ├── models/             # YOLO模型文件
│   └── utils/              # 工具函数
├── frontend/                # Vue前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── services/       # API服务
│   │   └── stores/         # 状态管理
│   └── public/             # 静态资源
├── docs/                   # 项目文档
├── requirements.txt        # Python依赖
└── README.md              # 项目说明
```

## 目标用户

- 神经外科医生
- 放射科医师
- 医学影像分析师
- 医疗AI研究人员

## 许可证

本项目采用MIT许可证。