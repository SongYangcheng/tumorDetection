# 贡献指南

## 欢迎贡献

感谢您对tumorDetection项目的兴趣！我们欢迎各种形式的贡献，包括但不限于：

- 报告bug
- 提交功能请求
- 编写代码
- 改进文档
- 参与讨论

## 行为准则

本项目采用[贡献者公约](https://www.contributor-covenant.org/)作为行为准则。请确保您的行为符合以下原则：

- 尊重所有贡献者
- 保持专业和友好的沟通
- 接受建设性的批评
- 关注项目目标

## 贡献流程

### 1. 准备工作

在开始贡献之前，请确保：

- 阅读项目文档
- 理解项目架构
- 设置开发环境
- 熟悉代码规范

### 2. 选择任务

您可以通过以下方式找到贡献机会：

- 查看[Issues](../../issues)列表
- 查看[Projects](../../projects)面板
- 参与[Discussions](../../discussions)

### 3. 创建分支

```bash
# 从主分支创建功能分支
git checkout -b feature/your-feature-name

# 或者修复bug
git checkout -b fix/issue-number-description
```

### 4. 开发代码

在开发过程中，请遵循：

- [开发指南](development.md)
- [代码规范](development.md#代码规范)
- [测试策略](development.md#测试策略)

### 5. 提交代码

```bash
# 添加更改
git add .

# 提交时使用清晰的提交信息
git commit -m "type(scope): description

- Detailed description of changes
- What problem was solved
- Any breaking changes"

# 推送分支
git push origin feature/your-feature-name
```

#### 提交信息规范

使用[Conventional Commits](https://conventionalcommits.org/)格式：

```
type(scope): description

[optional body]

[optional footer]
```

**类型 (type)**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或工具配置

**范围 (scope)**: 可选，指定影响的模块，如 `backend`, `frontend`, `api`

### 6. 创建Pull Request

1. 在GitHub上访问您的分支
2. 点击"Compare & pull request"
3. 填写PR描述：
   - 问题描述
   - 解决方案
   - 测试方法
   - 相关issue链接
4. 请求审查

## 代码审查流程

### 审查者职责

- 检查代码质量和规范
- 验证功能正确性
- 确保测试覆盖
- 提供建设性反馈

### 贡献者职责

- 及时响应审查意见
- 解释设计决策
- 根据反馈修改代码
- 保持耐心和开放态度

## Issue管理

### 报告Bug

创建bug报告时，请提供：

- 详细的复现步骤
- 期望的行为
- 实际的行为
- 环境信息 (OS, 浏览器, Python/Node版本)
- 相关的日志或截图

### 功能请求

创建功能请求时，请提供：

- 功能描述
- 使用场景
- 为什么需要这个功能
- 可选的实现建议

## 文档贡献

### 更新现有文档

1. 找到相关文档文件
2. 进行修改
3. 确保格式正确
4. 提交PR

### 添加新文档

1. 在适当位置创建新文件
2. 更新目录索引
3. 遵循现有文档风格

## 测试贡献

### 编写测试

- 为新功能编写单元测试
- 为bug修复编写回归测试
- 确保测试覆盖率不下降

### 运行测试

```bash
# 后端测试
cd backend
python -m pytest

# 前端测试
cd frontend
npm run test
```

## 翻译贡献

如果您想帮助翻译文档：

1. 检查[现有翻译](../../tree/main/docs)
2. 创建翻译分支
3. 翻译相关文件
4. 提交PR

## 社区参与

### 加入讨论

- [GitHub Discussions](../../discussions)
- [Slack/Discord] (如果有)
- 邮件列表 (如果有)

### 分享经验

- 撰写博客文章
- 录制教程视频
- 演讲或会议分享

## 认可贡献

所有贡献者将被：

- 列在[贡献者列表](../../contributors)
- 在发布说明中提及
- 获得社区认可

## 联系方式

如果您有任何问题：

- 创建[GitHub Issue](../../issues)
- 参与[GitHub Discussions](../../discussions)
- 发送邮件至: maintainers@tumordetection.com

## 许可证

通过贡献代码，您同意您的贡献将采用与项目相同的[许可证](../LICENSE)。