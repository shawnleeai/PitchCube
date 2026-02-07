# 贡献指南

感谢你对 PitchCube 的兴趣！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果你发现了 bug 或有功能建议：

1. 先搜索现有的 issues，避免重复
2. 创建新 issue，使用对应的模板
3. 提供详细的复现步骤（对于 bug）

### 提交代码

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发环境设置

```bash
# 1. Fork 并克隆仓库
git clone https://github.com/yourusername/pitchcube.git
cd pitchcube

# 2. 运行设置脚本
./scripts/setup.sh

# 3. 启动开发服务器
./scripts/start.sh dev
```

### 代码规范

#### Python (后端)

- 使用 Black 格式化代码
- 遵循 PEP 8 规范
- 添加类型注解
- 编写文档字符串

```bash
# 格式化代码
cd backend
black app/
isort app/

# 类型检查
mypy app/
```

#### TypeScript/JavaScript (前端)

- 使用 ESLint 和 Prettier
- 遵循项目已有的代码风格
- 使用 TypeScript 类型

```bash
# 格式化代码
cd frontend
npm run lint
npm run format
```

### 提交规范

提交信息格式：

```
<type>: <subject>

<body>

<footer>
```

类型 (type)：

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档
- `style`: 格式（不影响代码运行的变动）
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试
- `chore`: 构建过程或辅助工具的变动

示例：

```
feat: add poster template selection

- Add 4 new poster templates
- Implement template preview
- Add template filtering by category

Closes #123
```

### 测试

- 为新功能添加测试
- 确保所有测试通过
- 保持测试覆盖率

```bash
# 后端测试
cd backend
pytest

# 前端测试
cd frontend
npm test
```

### 文档

- 更新 README.md 如果需要
- 更新 API 文档
- 添加代码注释

## 行为准则

- 尊重他人
- 欢迎新人
- 专注于建设性反馈
- 保持专业

## 获取帮助

- 查看 [文档](docs/)
- 加入 [Discord](https://discord.gg/pitchcube)
- 发送邮件至：hello@pitchcube.app

## 许可证

通过贡献代码，你同意将你的贡献在 MIT 许可证下授权。
